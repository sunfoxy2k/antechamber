import os
from dotenv import load_dotenv


def setup_env():
    """Load environment variables and verify OpenAI API key"""
    load_dotenv()
    
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️ Warning: OPENAI_API_KEY not found")
        print("Please set it with: export OPENAI_API_KEY='your-api-key-here'")
        return False
    else:
        print("✅ OpenAI API key loaded successfully")
        return True 