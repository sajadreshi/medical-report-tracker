"""Prompt builder utility for loading and building prompts from YAML files."""

import os
import yaml
from typing import Dict, Optional
from langchain_core.prompts import ChatPromptTemplate


class PromptBuilder:
    """Builds ChatPromptTemplate from YAML configuration files."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the PromptBuilder.
        
        Args:
            config_path: Path to the YAML config file. If None, uses default path.
        """
        if config_path is None:
            # Default to config/prompts.yaml relative to project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(project_root, "config", "prompts.yaml")
        
        self.config_path = config_path
        self._config = None
    
    def load_config(self) -> Dict:
        """
        Load YAML configuration file.
        
        Returns:
            Dictionary containing the parsed YAML configuration
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            yaml.YAMLError: If the YAML file is malformed
        """
        if self._config is None:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Prompt config file not found: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        
        return self._config
    
    def build_prompt(self, prompt_name: str = "rag_assistant") -> ChatPromptTemplate:
        """
        Build a ChatPromptTemplate from YAML configuration.
        
        Args:
            prompt_name: Name of the prompt template in the YAML file
            
        Returns:
            ChatPromptTemplate instance
            
        Raises:
            KeyError: If the prompt_name is not found in the config
            ValueError: If the template structure is invalid
        """
        config = self.load_config()
        
        if prompt_name not in config:
            raise KeyError(f"Prompt '{prompt_name}' not found in config file")
        
        prompt_config = config[prompt_name]
        
        # Extract components
        system = prompt_config.get('system', '')
        instructions = prompt_config.get('instructions', '')
        template_str = prompt_config.get('template', '')
        
        if not template_str:
            raise ValueError(f"Template string is required for prompt '{prompt_name}'")
        
        # Build the final template by replacing {system} and {instructions} placeholders
        # But preserve {context} and {question} for later use
        # Use string replace to avoid KeyError on {context} and {question}
        final_template = template_str.replace('{system}', system).replace('{instructions}', instructions)
        
        # Create ChatPromptTemplate
        prompt_template = ChatPromptTemplate.from_template(final_template)
        
        return prompt_template
    
    def get_prompt_config(self, prompt_name: str = "rag_assistant") -> Dict:
        """
        Get the raw prompt configuration dictionary.
        
        Args:
            prompt_name: Name of the prompt template in the YAML file
            
        Returns:
            Dictionary containing the prompt configuration
        """
        config = self.load_config()
        return config.get(prompt_name, {})

