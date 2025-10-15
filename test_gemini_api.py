#!/usr/bin/env python3
"""
Test script to verify Gemini API configuration and available models.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CV.settings')

try:
    import django
    django.setup()
    
    from decouple import config
    import google.generativeai as genai
    
    print("🔧 Testing Gemini API Configuration")
    print("=" * 50)
    
    # Check API key
    api_key = config('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        sys.exit(1)
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # List available models
    print("\n📋 Available Gemini Models:")
    try:
        models = genai.list_models()
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"   ✅ {model.name}")
    except Exception as e:
        print(f"❌ Error listing models: {str(e)}")
    
    # Test with different model names
    test_models = [
        'gemini-1.5-pro',
        'gemini-1.5-flash', 
        'gemini-pro',
        'gemini-1.0-pro',
        'gemini-1.5-pro-latest'
    ]
    
    print("\n🧪 Testing Model Availability:")
    for model_name in test_models:
        try:
            model = genai.GenerativeModel(model_name)
            print(f"   ✅ {model_name} - Available")
        except Exception as e:
            print(f"   ❌ {model_name} - Error: {str(e)}")
    
    print("\n🎯 Testing Content Generation:")
    try:
        # Use the first available model
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello, this is a test. Please respond with 'API working'.")
        if response and response.text:
            print(f"   ✅ Content generation successful: {response.text.strip()}")
        else:
            print("   ❌ Content generation failed - empty response")
    except Exception as e:
        print(f"   ❌ Content generation error: {str(e)}")
    
    print("\n✨ Gemini API test completed!")
    
except ImportError as e:
    print(f"❌ Import error: {str(e)}")
    print("Make sure Django and required packages are installed")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")
    sys.exit(1)
