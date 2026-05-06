"""
AutoClaw - Autonomous AI Agent Platform
Skill Loader

Automatically discovers and loads all skills from the skills directory.
"""

import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Any


class SkillLoader:
    """
    Discovers and loads skills from the skills directory.
    
    Skills are Python modules that export skill definitions.
    """
    
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.loaded_skills = {}
    
    def load_skills(self) -> List[Dict]:
        """
        Load all skills from the skills directory.
        
        Returns:
            List of skill definitions
        """
        skills = []
        
        # Scan for skill modules
        skill_files = list(self.skills_dir.glob("*.py"))
        
        for skill_file in skill_files:
            if skill_file.name.startswith("_"):
                continue
            
            try:
                # Import the module
                module_name = f"skills.{skill_file.stem}"
                module = importlib.import_module(module_name)
                
                # Look for SKILL_METADATA in the module
                if hasattr(module, "SKILL_METADATA"):
                    skill_def = module.SKILL_METADATA.copy()
                    skill_def["module"] = module
                    skill_def["file"] = str(skill_file)
                    skills.append(skill_def)
                    self.loaded_skills[skill_def.get("name", skill_file.stem)] = skill_def
                    
            except Exception as e:
                print(f"Warning: Could not load skill from {skill_file}: {e}")
        
        return skills
    
    def get_skill(self, name: str) -> Optional[Dict]:
        """Get a skill by name."""
        return self.loaded_skills.get(name)
    
    def reload_skills(self) -> List[Dict]:
        """Reload all skills (useful after installing new skills)."""
        self.loaded_skills = {}
        return self.load_skills()
    
    def get_skill_store_info(self) -> Dict:
        """Get information about the skill store."""
        return {
            "total_skills": len(self.loaded_skills),
            "skills": [
                {
                    "name": s.get("name"),
                    "description": s.get("description"),
                    "version": s.get("version", "1.0"),
                    "author": s.get("author", "Unknown")
                }
                for s in self.loaded_skills.values()
            ]
        }


# Export for use in other modules
__all__ = ["SkillLoader"]
