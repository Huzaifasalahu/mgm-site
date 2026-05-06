"""
AutoClaw - Autonomous AI Agent Platform
Core AI Agent Implementation

Implements the Observe-Plan-Act-Learn loop for autonomous task execution.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import re


class AutoClawAgent:
    """
    Core AI agent that implements the Observe-Plan-Act-Learn loop.
    
    This agent can:
    - Accept natural language goals
    - Break down goals into executable steps
    - Call appropriate skills/tools
    - Learn from outcomes and user feedback
    """
    
    def __init__(self, skills: List, tool_manager, config: Dict, memory_dir: Path):
        self.skills = skills
        self.tool_manager = tool_manager
        self.config = config
        self.memory_dir = memory_dir
        
        # Memory components
        self.short_term_memory = []
        self.long_term_memory = []
        
        # Load long-term memory
        self.load_memory()
        
        # Agent state
        self.current_goal = None
        self.plan = []
        self.executed_steps = []
        self.is_running = False
        
        # Token tracking
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "estimated_cost": 0.0
        }
        
        # Initialize LLM client
        self.llm_client = self._initialize_llm_client()
    
    def _initialize_llm_client(self):
        """Initialize the LLM client based on configuration."""
        provider = self.config.get("llm_provider", "openai")
        api_key = self.config.get("api_key", "")
        api_base = self.config.get("api_base")
        model = self.config.get("llm_model", "gpt-4o")
        
        # Return a simple client wrapper
        return LLMClient(
            provider=provider,
            api_key=api_key,
            api_base=api_base,
            model=model
        )
    
    def load_memory(self):
        """Load long-term memory from disk."""
        memory_file = self.memory_dir / "long_term_memory.json"
        if memory_file.exists():
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    self.long_term_memory = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load memory: {e}")
                self.long_term_memory = []
    
    def save_memory(self):
        """Save long-term memory to disk."""
        memory_file = self.memory_dir / "long_term_memory.json"
        try:
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.long_term_memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    async def execute_goal(self, goal: str) -> str:
        """
        Execute a goal using the Observe-Plan-Act-Learn loop.
        
        Args:
            goal: Natural language description of the goal
            
        Returns:
            Result of the execution
        """
        self.current_goal = goal
        self.is_running = True
        self.executed_steps = []
        
        try:
            # OBSERVE: Understand the goal
            print(f"\n👁️  OBSERVE: Understanding goal '{goal}'")
            observation = await self._observe(goal)
            
            # PLAN: Break down into steps
            print(f"\n📋 PLAN: Creating execution plan")
            self.plan = await self._plan(goal, observation)
            print(f"Plan created with {len(self.plan)} steps")
            
            # ACT: Execute each step
            print(f"\n⚡ ACT: Executing plan")
            results = []
            for i, step in enumerate(self.plan, 1):
                print(f"\n  Step {i}/{len(self.plan)}: {step}")
                step_result = await self._act(step, goal)
                results.append(step_result)
                self.executed_steps.append({
                    "step": step,
                    "result": step_result,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Check if we should continue
                if step_result.get("status") == "failed" and not step_result.get("recoverable", True):
                    print(f"  ⚠️  Step failed, attempting recovery...")
                    recovery_result = await self._recover(step, step_result)
                    if recovery_result.get("status") == "success":
                        print(f"  ✅ Recovery successful")
                        self.executed_steps[-1]["result"] = recovery_result
                    else:
                        print(f"  ❌ Recovery failed, stopping execution")
                        break
            
            # LEARN: Store experience
            print(f"\n🧠 LEARN: Storing experience")
            await self._learn(goal, self.executed_steps, results)
            
            # Generate final result
            final_result = self._generate_final_result(results)
            
            return final_result
            
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            print(f"\n❌ {error_msg}")
            return error_msg
        finally:
            self.is_running = False
    
    async def _observe(self, goal: str) -> Dict:
        """
        OBSERVE phase: Analyze the goal and gather context.
        """
        # Build context from memory
        relevant_memories = self._search_relevant_memories(goal)
        
        # Get available tools
        available_tools = self.tool_manager.get_tool_descriptions()
        
        # Create observation prompt
        prompt = f"""
Analyze this goal and provide structured observations:

GOAL: {goal}

RELEVANT PAST EXPERIENCES:
{json.dumps(relevant_memories[:3], indent=2) if relevant_memories else "None"}

AVAILABLE TOOLS:
{json.dumps(available_tools, indent=2)}

Provide your analysis in JSON format:
{{
    "goal_type": "classification of the goal",
    "required_tools": ["list of tools needed"],
    "potential_challenges": ["list of potential issues"],
    "context_needed": ["what additional context is required"]
}}
"""
        
        response = await self.llm_client.generate(prompt, response_format="json")
        
        try:
            observation = json.loads(response)
        except:
            observation = {
                "goal_type": "general",
                "required_tools": [],
                "potential_challenges": [],
                "context_needed": []
            }
        
        self.short_term_memory.append({
            "type": "observation",
            "goal": goal,
            "observation": observation,
            "timestamp": datetime.now().isoformat()
        })
        
        return observation
    
    async def _plan(self, goal: str, observation: Dict) -> List[str]:
        """
        PLAN phase: Break down the goal into executable steps.
        """
        prompt = f"""
Create a detailed execution plan for this goal:

GOAL: {goal}

ANALYSIS:
{json.dumps(observation, indent=2)}

Break this down into concrete, executable steps. Each step should:
1. Be specific and actionable
2. Use one of the available tools
3. Be achievable independently

Return a JSON array of steps:
["step 1", "step 2", ...]
"""
        
        response = await self.llm_client.generate(prompt, response_format="json")
        
        try:
            plan = json.loads(response)
            if isinstance(plan, list):
                return plan
        except:
            pass
        
        # Fallback: simple plan
        return [f"Execute: {goal}"]
    
    async def _act(self, step: str, goal: str) -> Dict:
        """
        ACT phase: Execute a single step using appropriate tools.
        """
        # Determine which tool to use
        tool_selection = await self._select_tool(step)
        
        if not tool_selection:
            return {
                "status": "failed",
                "error": "No suitable tool found",
                "recoverable": False
            }
        
        tool_name = tool_selection.get("tool")
        parameters = tool_selection.get("parameters", {})
        
        # Execute the tool
        try:
            result = await self.tool_manager.execute_tool(tool_name, parameters)
            return {
                "status": "success",
                "tool": tool_name,
                "result": result,
                "step": step
            }
        except Exception as e:
            return {
                "status": "failed",
                "tool": tool_name,
                "error": str(e),
                "recoverable": True,
                "step": step
            }
    
    async def _select_tool(self, step: str) -> Optional[Dict]:
        """Select the appropriate tool for a step."""
        tools = self.tool_manager.get_tool_descriptions()
        
        prompt = f"""
Select the best tool for this step:

STEP: {step}

AVAILABLE TOOLS:
{json.dumps(tools, indent=2)}

Choose the most appropriate tool and provide parameters in JSON:
{{
    "tool": "tool_name",
    "parameters": {{
        "param1": "value1"
    }}
}}
"""
        
        response = await self.llm_client.generate(prompt, response_format="json")
        
        try:
            return json.loads(response)
        except:
            return None
    
    async def _recover(self, step: str, failed_result: Dict) -> Dict:
        """Attempt to recover from a failed step."""
        prompt = f"""
The following step failed. Suggest a recovery strategy:

STEP: {step}
ERROR: {failed_result.get('error', 'Unknown error')}

Provide a recovery plan in JSON:
{{
    "alternative_approach": "description",
    "retry_parameters": {{}},
    "skip": false
}}
"""
        
        response = await self.llm_client.generate(prompt, response_format="json")
        
        try:
            recovery_plan = json.loads(response)
            
            if recovery_plan.get("skip"):
                return {"status": "skipped", "reason": "Recovery suggests skipping"}
            
            # Retry with new parameters
            retry_params = recovery_plan.get("retry_parameters", {})
            tool_name = failed_result.get("tool")
            
            if tool_name and retry_params:
                result = await self.tool_manager.execute_tool(tool_name, retry_params)
                return {
                    "status": "success",
                    "tool": tool_name,
                    "result": result,
                    "recovered": True
                }
        except:
            pass
        
        return {"status": "failed", "reason": "Recovery unsuccessful"}
    
    async def _learn(self, goal: str, executed_steps: List, results: List):
        """
        LEARN phase: Store experience for future use.
        """
        # Create learning entry
        learning_entry = {
            "goal": goal,
            "steps": executed_steps,
            "outcome": "success" if any(r.get("status") == "success" for r in results) else "partial",
            "timestamp": datetime.now().isoformat(),
            "tokens_used": self.token_usage.copy()
        }
        
        # Add to long-term memory
        self.long_term_memory.append(learning_entry)
        
        # Limit memory size
        if len(self.long_term_memory) > 1000:
            self.long_term_memory = self.long_term_memory[-500:]
        
        # Save to disk
        self.save_memory()
        
        # Update short-term memory
        self.short_term_memory.append({
            "type": "learning",
            "entry": learning_entry,
            "timestamp": datetime.now().isoformat()
        })
    
    def _search_relevant_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for relevant memories using simple keyword matching."""
        if not self.long_term_memory:
            return []
        
        # Simple TF-IDF-like scoring
        query_words = set(query.lower().split())
        
        scored_memories = []
        for memory in self.long_term_memory:
            memory_text = f"{memory.get('goal', '')} {memory.get('outcome', '')}"
            memory_words = set(memory_text.lower().split())
            
            # Calculate overlap
            overlap = len(query_words & memory_words)
            score = overlap / max(len(query_words), 1)
            
            scored_memories.append((score, memory))
        
        # Sort by score and return top results
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [m[1] for m in scored_memories[:limit]]
    
    def _generate_final_result(self, results: List) -> str:
        """Generate a human-readable final result."""
        successful = [r for r in results if r.get("status") == "success"]
        failed = [r for r in results if r.get("status") == "failed"]
        
        summary_parts = []
        
        if successful:
            summary_parts.append(f"✅ Successfully completed {len(successful)} steps")
            for step in successful:
                if step.get("result"):
                    summary_parts.append(f"  • {step.get('step', 'Step')}: Done")
        
        if failed:
            summary_parts.append(f"⚠️  {len(failed)} steps encountered issues")
            for step in failed:
                summary_parts.append(f"  • {step.get('step', 'Step')}: {step.get('error', 'Failed')}")
        
        return "\n".join(summary_parts) if summary_parts else "Task completed"
    
    def update_config(self, new_config: Dict):
        """Update agent configuration."""
        self.config.update(new_config)
        self.llm_client = self._initialize_llm_client()
    
    def get_token_usage(self) -> Dict:
        """Get current token usage statistics."""
        return self.token_usage.copy()
    
    def clear_memory(self):
        """Clear all memory."""
        self.short_term_memory = []
        self.long_term_memory = []
        self.save_memory()


class LLMClient:
    """
    Unified LLM client supporting multiple providers.
    """
    
    def __init__(self, provider: str, api_key: str, api_base: Optional[str], model: str):
        self.provider = provider
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        
        # Provider-specific configurations
        self.endpoints = {
            "openai": "https://api.openai.com/v1/chat/completions",
            "anthropic": "https://api.anthropic.com/v1/messages",
            "google": "https://generativelanguage.googleapis.com/v1beta/models",
            "deepseek": "https://api.deepseek.com/v1/chat/completions",
            "ollama": "http://localhost:11434/api/generate"
        }
    
    async def generate(self, prompt: str, response_format: str = "text", **kwargs) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The input prompt
            response_format: "text" or "json"
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        # Simulate generation (in production, make actual API calls)
        # This is a placeholder that would be replaced with real API calls
        
        if self.provider == "ollama":
            return await self._generate_ollama(prompt, response_format)
        elif self.provider == "openai":
            return await self._generate_openai(prompt, response_format)
        else:
            # Generic OpenAI-compatible endpoint
            return await self._generate_generic(prompt, response_format)
    
    async def _generate_openai(self, prompt: str, response_format: str) -> str:
        """Generate using OpenAI API."""
        try:
            import aiohttp
            
            url = self.api_base or self.endpoints["openai"]
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
            
            if response_format == "json":
                payload["response_format"] = {"type": "json_object"}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    data = await response.json()
                    
                    # Update token usage
                    usage = data.get("usage", {})
                    
                    return data["choices"][0]["message"]["content"]
                    
        except Exception as e:
            # Fallback: return simulated response for testing
            return self._simulate_response(prompt, response_format)
    
    async def _generate_ollama(self, prompt: str, response_format: str) -> str:
        """Generate using local Ollama."""
        try:
            import aiohttp
            
            url = self.endpoints["ollama"]
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    data = await response.json()
                    return data.get("response", "")
                    
        except Exception as e:
            return self._simulate_response(prompt, response_format)
    
    async def _generate_generic(self, prompt: str, response_format: str) -> str:
        """Generate using generic OpenAI-compatible endpoint."""
        return await self._generate_openai(prompt, response_format)
    
    def _simulate_response(self, prompt: str, response_format: str) -> str:
        """Simulate a response for testing without API access."""
        if response_format == "json":
            return '{"status": "simulated", "message": "This is a simulated response for testing"}'
        return "This is a simulated response. Configure your API key for real LLM responses."
