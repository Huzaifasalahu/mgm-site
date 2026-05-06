"""
AutoClaw - Autonomous AI Agent Platform
Memory Skill

Persistent RAG memory and skill adaptation system.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

SKILL_METADATA = {
    "name": "memory",
    "version": "1.0.0",
    "description": "Persistent RAG memory and skill adaptation",
    "author": "AutoClaw Team",
    "capabilities": [
        "store_memory",
        "search_memories",
        "delete_memory",
        "get_feedback",
        "adapt_skill"
    ]
}


class MemoryManager:
    """
    Long-term memory management with RAG capabilities.
    
    Features:
    - Store task outcomes and learnings
    - Search relevant memories using TF-IDF
    - User feedback tracking
    - Self-adaptation for skills
    """
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.memories_file = self.memory_dir / "memories.json"
        self.feedback_file = self.memory_dir / "feedback.json"
        self.skills_adapted_file = self.memory_dir / "adapted_skills.json"
        
        # In-memory cache
        self.memories = []
        self.feedback = []
        self.adapted_skills = {}
        
        # Load existing data
        self._load_all()
    
    def _load_all(self):
        """Load all persisted data."""
        self._load_memories()
        self._load_feedback()
        self._load_adapted_skills()
    
    def _load_memories(self):
        """Load memories from disk."""
        if self.memories_file.exists():
            try:
                with open(self.memories_file, 'r', encoding='utf-8') as f:
                    self.memories = json.load(f)
            except:
                self.memories = []
    
    def _save_memories(self):
        """Save memories to disk."""
        with open(self.memories_file, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, indent=2, ensure_ascii=False)
    
    def _load_feedback(self):
        """Load feedback from disk."""
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    self.feedback = json.load(f)
            except:
                self.feedback = []
    
    def _save_feedback(self):
        """Save feedback to disk."""
        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(self.feedback, f, indent=2, ensure_ascii=False)
    
    def _load_adapted_skills(self):
        """Load adapted skills from disk."""
        if self.skills_adapted_file.exists():
            try:
                with open(self.skills_adapted_file, 'r', encoding='utf-8') as f:
                    self.adapted_skills = json.load(f)
            except:
                self.adapted_skills = {}
    
    def _save_adapted_skills(self):
        """Save adapted skills to disk."""
        with open(self.skills_adapted_file, 'w', encoding='utf-8') as f:
            json.dump(self.adapted_skills, f, indent=2, ensure_ascii=False)
    
    async def store_memory(self, goal: str, steps: List[Dict], 
                          outcome: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Store a memory of a completed task.
        
        Args:
            goal: The original goal
            steps: Steps taken to achieve the goal
            outcome: Final outcome (success/partial/failure)
            metadata: Additional metadata
            
        Returns:
            Storage result
        """
        memory = {
            "id": hashlib.md5(f"{goal}{datetime.now().isoformat()}".encode()).hexdigest()[:12],
            "goal": goal,
            "steps": steps,
            "outcome": outcome,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "access_count": 0,
            "tags": self._extract_tags(goal)
        }
        
        self.memories.append(memory)
        
        # Limit memory size
        if len(self.memories) > 1000:
            # Keep most accessed memories
            self.memories.sort(key=lambda x: x.get("access_count", 0), reverse=True)
            self.memories = self.memories[:500]
        
        self._save_memories()
        
        return {
            "success": True,
            "memory_id": memory["id"],
            "message": f"Stored memory for goal: {goal[:50]}..."
        }
    
    async def search_memories(self, query: str, limit: int = 5) -> Dict:
        """
        Search for relevant memories using TF-IDF-like scoring.
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            Matching memories
        """
        if not self.memories:
            return {"success": True, "results": [], "count": 0}
        
        # Tokenize query
        query_tokens = set(query.lower().split())
        
        scored = []
        for memory in self.memories:
            # Create searchable text
            text = f"{memory['goal']} {memory['outcome']} {' '.join([s.get('step', '') for s in memory.get('steps', [])])}"
            memory_tokens = set(text.lower().split())
            
            # Calculate overlap score
            overlap = len(query_tokens & memory_tokens)
            score = overlap / max(len(query_tokens), 1)
            
            # Boost by access count
            score *= (1 + memory.get("access_count", 0) * 0.1)
            
            scored.append((score, memory))
        
        # Sort and return top results
        scored.sort(key=lambda x: x[0], reverse=True)
        results = scored[:limit]
        
        # Update access counts
        for _, memory in results:
            memory["access_count"] = memory.get("access_count", 0) + 1
        
        self._save_memories()
        
        return {
            "success": True,
            "results": [{"score": s, "memory": m} for s, m in results],
            "count": len(results),
            "query": query
        }
    
    async def delete_memory(self, memory_id: str) -> Dict:
        """Delete a memory by ID."""
        for i, memory in enumerate(self.memories):
            if memory["id"] == memory_id:
                deleted = self.memories.pop(i)
                self._save_memories()
                return {
                    "success": True,
                    "deleted_id": memory_id,
                    "message": "Memory deleted"
                }
        
        return {
            "success": False,
            "error": f"Memory not found: {memory_id}"
        }
    
    async def store_feedback(self, memory_id: str, rating: int,
                            comment: Optional[str] = None) -> Dict:
        """
        Store user feedback for a memory.
        
        Args:
            memory_id: Memory ID
            rating: Rating (1-5)
            comment: Optional comment
            
        Returns:
            Feedback storage result
        """
        # Verify memory exists
        memory_exists = any(m["id"] == memory_id for m in self.memories)
        if not memory_exists:
            return {"success": False, "error": "Memory not found"}
        
        feedback_entry = {
            "memory_id": memory_id,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        
        self.feedback.append(feedback_entry)
        self._save_feedback()
        
        return {
            "success": True,
            "message": f"Feedback stored: {rating}/5 stars"
        }
    
    async def get_feedback(self, memory_id: str) -> Dict:
        """Get feedback for a specific memory."""
        relevant = [f for f in self.feedback if f["memory_id"] == memory_id]
        
        if not relevant:
            return {"success": True, "feedback": [], "average_rating": None}
        
        avg_rating = sum(f["rating"] for f in relevant) / len(relevant)
        
        return {
            "success": True,
            "feedback": relevant,
            "count": len(relevant),
            "average_rating": round(avg_rating, 2)
        }
    
    async def adapt_skill(self, skill_name: str, adaptation: Dict) -> Dict:
        """
        Record a skill adaptation based on learning.
        
        Args:
            skill_name: Name of the skill
            adaptation: Adaptation details
            
        Returns:
            Adaptation result
        """
        if skill_name not in self.adapted_skills:
            self.adapted_skills[skill_name] = {
                "adaptations": [],
                "version": 1
            }
        
        adaptation_entry = {
            "adaptation": adaptation,
            "timestamp": datetime.now().isoformat(),
            "based_on_memories": adaptation.get("memory_ids", [])
        }
        
        self.adapted_skills[skill_name]["adaptations"].append(adaptation_entry)
        self.adapted_skills[skill_name]["version"] += 1
        
        self._save_adapted_skills()
        
        return {
            "success": True,
            "skill": skill_name,
            "new_version": self.adapted_skills[skill_name]["version"],
            "message": f"Skill '{skill_name}' adapted"
        }
    
    def get_adapted_skill(self, skill_name: str) -> Optional[Dict]:
        """Get adaptations for a skill."""
        return self.adapted_skills.get(skill_name)
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract simple tags from text."""
        # Simple keyword extraction
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'could', 'should', 'may', 'might', 'must', 'shall'}
        
        words = text.lower().split()
        tags = [w for w in words if w not in stopwords and len(w) > 3]
        return list(set(tags))[:10]
    
    async def execute(self, action: str, **kwargs) -> Dict:
        """Generic execute method."""
        if action == "store_memory":
            return await self.store_memory(
                kwargs.get("goal", ""),
                kwargs.get("steps", []),
                kwargs.get("outcome", ""),
                kwargs.get("metadata")
            )
        elif action == "search_memories":
            return await self.search_memories(
                kwargs.get("query", ""),
                kwargs.get("limit", 5)
            )
        elif action == "delete_memory":
            return await self.delete_memory(kwargs.get("memory_id", ""))
        elif action == "store_feedback":
            return await self.store_feedback(
                kwargs.get("memory_id", ""),
                kwargs.get("rating", 3),
                kwargs.get("comment")
            )
        elif action == "get_feedback":
            return await self.get_feedback(kwargs.get("memory_id", ""))
        elif action == "adapt_skill":
            return await self.adapt_skill(
                kwargs.get("skill_name", ""),
                kwargs.get("adaptation", {})
            )
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
