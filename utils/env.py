import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

class EnvUtils:
    """
    Utility class for managing environment variables and configuration
    """
    _instance = None
    _env_loaded = False

    def __new__(cls):
        """
        Singleton implementation to ensure env is loaded only once
        """
        if not cls._instance:
            cls._instance = super(EnvUtils, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Load environment variables if not already loaded
        """
        if not self.__class__._env_loaded:
            self.load_env()
            self.__class__._env_loaded = True

    def load_env(self, env_path: Optional[str] = None):
        """
        Load environment variables from .env file
        
        Args:
            env_path (str, optional): Path to .env file. 
                                      Defaults to searching in current and parent directories
        """
        # List of potential .env file locations
        possible_paths = [
            env_path,  # Custom path if provided
            '.env',    # Current directory
            '../.env', # Parent directory
            os.path.join(os.path.dirname(__file__), '.env'),  # Same directory as script
            os.path.join(os.path.dirname(__file__), '../.env')  # Parent of script directory
        ]

        # Try loading from possible paths
        for path in possible_paths:
            if path and os.path.exists(path):
                load_dotenv(path, override=True)
                print(f"Loaded environment variables from {path}")
                return

        print("No .env file found. Using existing environment variables.")

    @staticmethod
    def get_env(key: str, default: Optional[Any] = None) -> Optional[str]:
        """
        Retrieve an environment variable
        
        Args:
            key (str): Environment variable name
            default (optional): Default value if variable not found
        
        Returns:
            str or default value: Environment variable value
        """
        return os.getenv(key, default)

    @staticmethod
    def get_required_env(key: str) -> str:
        """
        Retrieve a required environment variable
        
        Args:
            key (str): Environment variable name
        
        Returns:
            str: Environment variable value
        
        Raises:
            ValueError: If environment variable is not set
        """
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value

    def get_config(self, config_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve multiple configuration values with defaults
        
        Args:
            config_map (dict): Dictionary of config keys to default values
        
        Returns:
            dict: Configuration values
        """
        return {
            key: self.get_env(key, default) 
            for key, default in config_map.items()
        }
    @staticmethod
    def get_llm():
        """Get the appropriate LLM based on environment configuration"""
        model_type = EnvUtils().get_required_env("MODEL_TYPE").lower()
        if model_type == "ollama":
            from langchain_ollama import ChatOllama
            return ChatOllama(
                model="mistral",
                temperature=0
            )
        else:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model="gpt-4",
                temperature=0
            )
# Example usage
def main():
    # Initialize EnvUtils (will load .env)
    env_utils = EnvUtils()

    # Get a specific environment variable
    Kafka_topic = env_utils.get_env('Kafka_topic')
    print(f"Kafka_topic: {Kafka_topic}")

   

if __name__ == "__main__":
    main()