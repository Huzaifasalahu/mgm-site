"""
AutoClaw - Autonomous AI Agent Platform
Main Entry Point

This module orchestrates the launch of core services including:
- HTTP server for API endpoints
- Agent loop execution
- GUI initialization
- Skill loading
"""

import sys
import os
import asyncio
import threading
import signal
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from agent import AutoClawAgent
from skills import SkillLoader
from ui.main_window import MainWindow
from tools import ToolManager


class AutoClawApplication:
    """Main application class that coordinates all components."""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.skills_dir = self.project_root / "skills"
        self.memory_dir = self.project_root / "memory"
        self.config_file = self.project_root / "config.json"
        
        # Initialize components
        self.skill_loader = SkillLoader(self.skills_dir)
        self.tool_manager = ToolManager()
        self.agent = None
        self.gui = None
        
        # Ensure directories exist
        self.memory_dir.mkdir(exist_ok=True)
        
        # Configuration
        self.config = {
            "llm_provider": "openai",
            "llm_model": "gpt-4o",
            "api_key": "",
            "api_base": None,
            "browser_profile": None,
            "messaging": {
                "feishu_webhook": "",
                "slack_webhook": "",
                "telegram_bot_token": ""
            },
            "scheduler_enabled": True
        }
        
        # Load existing config
        self.load_config()
        
    def load_config(self):
        """Load configuration from file."""
        import json
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
    
    def save_config(self):
        """Save configuration to file."""
        import json
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
    
    def initialize_agent(self):
        """Initialize the AI agent with loaded skills."""
        # Load all available skills
        skills = self.skill_loader.load_skills()
        print(f"Loaded {len(skills)} skills")
        
        # Create agent instance
        self.agent = AutoClawAgent(
            skills=skills,
            tool_manager=self.tool_manager,
            config=self.config,
            memory_dir=self.memory_dir
        )
        
        return self.agent
    
    def run_gui(self):
        """Run the graphical user interface."""
        from PyQt5.QtWidgets import QApplication
        
        # Initialize agent if not already done
        if not self.agent:
            self.initialize_agent()
        
        app = QApplication(sys.argv)
        app.setApplicationName("AutoClaw")
        app.setOrganizationName("AutoClaw")
        
        # Create main window
        self.gui = MainWindow(self.agent, self.config, self)
        self.gui.show()
        
        # Run event loop
        sys.exit(app.exec_())
    
    def run_cli(self):
        """Run in command-line mode."""
        if not self.agent:
            self.initialize_agent()
        
        print("=" * 60)
        print("AutoClaw CLI Mode")
        print("=" * 60)
        print("Type 'exit' to quit, 'help' for commands")
        print()
        
        while True:
            try:
                user_input = input("\n🤖 AutoClaw > ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'exit':
                    break
                
                if user_input.lower() == 'help':
                    self.print_help()
                    continue
                
                if user_input.lower() == 'config':
                    self.show_config()
                    continue
                
                # Execute task
                asyncio.run(self.execute_task(user_input))
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    async def execute_task(self, goal: str):
        """Execute a task using the agent."""
        result = await self.agent.execute_goal(goal)
        print(f"\n✅ Result: {result}")
    
    def print_help(self):
        """Print help information."""
        print("""
Available Commands:
  exit     - Exit the application
  help     - Show this help message
  config   - Show current configuration
  <goal>   - Enter a natural language goal for the agent
  
Examples:
  - "Search for Python tutorials and save them to my documents"
  - "Create a report from the CSV file in my downloads folder"
  - "Send a message to my team on Slack about the meeting"
        """)
    
    def show_config(self):
        """Show current configuration."""
        print("\nCurrent Configuration:")
        print("-" * 40)
        for key, value in self.config.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for k, v in value.items():
                    if 'key' in k.lower() or 'token' in k.lower():
                        v = "***" + v[-4:] if v else "(not set)"
                    print(f"  {k}: {v}")
            else:
                if 'key' in key.lower() or 'token' in key.lower():
                    value = "***" + value[-4:] if value else "(not set)"
                print(f"{key}: {value}")
        print("-" * 40)


def main():
    """Main entry point."""
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║              🦞 AutoClaw v1.0                     ║
    ║         Autonomous AI Agent Platform              ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    app = AutoClawApplication()
    
    # Determine run mode
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        app.run_cli()
    else:
        # Default to GUI mode
        try:
            from PyQt5.QtWidgets import QApplication
            app.run_gui()
        except ImportError:
            print("PyQt5 not available, falling back to CLI mode")
            app.run_cli()


if __name__ == "__main__":
    main()
