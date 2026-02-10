import os
import sys
import importlib.util
import logging
from typing import List, Any
from langchain.tools import BaseTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillManager:
    """
    Manages the discovery and loading of skills from the 'src/skills' directory.
    """
    def __init__(self, skills_dir: str = "src/skills"):
        """
        Initialize the SkillManager with the directory to scan for skills.
        
        Args:
            skills_dir (str): Relative path to the skills directory from the project root.
        """
        # Determine absolute path relative to the project root
        # Assuming run from project root, or adjusting based on file location
        # If this file is in src/agent, we go up two levels to find root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../"))
        self.skills_dir = os.path.join(project_root, skills_dir)
        self.loaded_skills = {}

    def load_skills(self) -> List[BaseTool]:
        """
        Scans the skills directory and loads all valid skills.
        Returns a list of all tools provided by the loaded skills.
        """
        all_tools = []
        
        if not os.path.exists(self.skills_dir):
            logger.warning(f"Skills directory not found: {self.skills_dir}")
            return all_tools

        logger.info(f"Scanning for skills in: {self.skills_dir}")

        for item in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, item)
            
            # Check if it's a directory and has __init__.py (making it a package)
            if os.path.isdir(skill_path) and "__init__.py" in os.listdir(skill_path):
                try:
                    tools = self._load_skill(item, skill_path)
                    if tools:
                        all_tools.extend(tools)
                        self.loaded_skills[item] = len(tools)
                        logger.info(f"Successfully loaded skill '{item}' with {len(tools)} tools.")
                except Exception as e:
                    logger.error(f"Failed to load skill '{item}': {e}")
        
        return all_tools

    def _load_skill(self, skill_name: str, skill_path: str) -> List[BaseTool]:
        """
        Loads a single skill module and extracts its tools.
        """
        # Dynamically import the module
        spec = importlib.util.spec_from_file_location(skill_name, os.path.join(skill_path, "__init__.py"))
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for skill: {skill_name}")
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[skill_name] = module
        spec.loader.exec_module(module)
        
        # Look for 'TOOLS' list or 'get_tools' function
        if hasattr(module, "TOOLS") and isinstance(module.TOOLS, list):
            return module.TOOLS
        elif hasattr(module, "get_tools") and callable(module.get_tools):
            return module.get_tools()
        else:
            logger.warning(f"Skill '{skill_name}' does not export 'TOOLS' list or 'get_tools' function.")
            return []

if __name__ == "__main__":
    # verification
    manager = SkillManager()
    tools = manager.load_skills()
    print(f"Loaded {len(tools)} tools: {[t.name for t in tools]}")
