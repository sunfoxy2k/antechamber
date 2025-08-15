#!/usr/bin/env python3
"""
Test script to verify Flask + OpenAI setup
"""

import os
import sys
from dotenv import load_dotenv


def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    try:
        import flask
        print(f"✅ Flask {flask.__version__} imported successfully")

        import openai
        print(f"✅ OpenAI {openai.__version__} imported successfully")

        print("✅ python-dotenv imported successfully")

        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_env_loading():
    """Test if .env file can be loaded"""
    print("\nTesting .env file loading...")
    try:
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')

        if api_key:
            if api_key == 'your_openai_api_key_here':
                print("⚠️  .env file loaded but API key is placeholder")
                print("   Please replace 'your_openai_api_key_here' with "
                      "your actual OpenAI API key")
            else:
                print("✅ .env file loaded and API key is configured")
            return True
        else:
            print("❌ OPENAI_API_KEY not found in environment")
            return False
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return False


def test_openai_client():
    """Test OpenAI client initialization"""
    print("\nTesting OpenAI client initialization...")
    try:
        from openai import OpenAI

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            print("⚠️  Cannot test OpenAI client - API key not configured")
            print("   Set your API key in .env file to test OpenAI "
                  "connectivity")
            return False

        OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized successfully")

        # Test API connectivity (optional - only if user wants to test)
        print("   To test API connectivity, uncomment the lines below "
              "and run again")
        # models = client.models.list()
        # print(f"✅ Connected to OpenAI API - {len(models.data)} "
        #       "models available")

        return True
    except Exception as e:
        print(f"❌ Error initializing OpenAI client: {e}")
        return False


def test_flask_app():
    """Test Flask app initialization"""
    print("\nTesting Flask app initialization...")
    try:
        from app import app
        print("✅ Flask app imported successfully")

        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Flask app health check passed")
                return True
            else:
                print(f"❌ Flask app health check failed: "
                      f"{response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error testing Flask app: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Testing Flask + OpenAI Setup")
    print("=" * 40)

    tests = [
        test_imports,
        test_env_loading,
        test_openai_client,
        test_flask_app
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"✅ Passed: {sum(results)}/{len(results)} tests")

    if all(results):
        print("\n🎉 All tests passed! Your setup is ready to use.")
        print("\nTo start the Flask app, run:")
        print("   python app.py")
        print("\nThen visit: http://localhost:5000")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

    return all(results)


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
