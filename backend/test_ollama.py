#!/usr/bin/env python3
"""
Test script for Ollama integration with the stock research application.
Run this to verify that Ollama is working correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.llm_service import get_llm_service
from app.config import settings

def test_ollama_integration():
    """Test Ollama integration with different models."""
    
    print("🧪 Testing Ollama Integration")
    print("=" * 50)
    
    # Test different Ollama providers
    providers = [
        "ollama-llama3.1",
        "ollama-llama3.2",
        "ollama-mixtral",
        "ollama-deepseek-r1"
    ]
    
    for provider in providers:
        print(f"\n📋 Testing provider: {provider}")
        print("-" * 30)
        
        try:
            # Initialize the LLM service
            llm_service = get_llm_service(provider)
            
            # Test with a simple stock-related query
            system_prompt = "You are a helpful financial analyst assistant."
            user_message = "What are the key factors to consider when analyzing a stock's performance?"
            
            print(f"🤖 Sending query to {provider}...")
            response = llm_service.invoke(system_prompt, user_message)
            
            print(f"✅ Success! Response length: {len(response)} characters")
            print(f"📝 First 200 characters: {response[:200]}...")
            
        except Exception as e:
            print(f"❌ Error with {provider}: {str(e)}")
            print("💡 Make sure Ollama is running and the model is installed:")
            print(f"   ollama serve")
            print(f"   ollama pull {provider.split('-')[1]}:{provider.split('-')[2] if len(provider.split('-')) > 2 else '8b'}")
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")

def check_ollama_status():
    """Check if Ollama service is running."""
    import httpx
    
    try:
        response = httpx.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama is running with {len(models)} models installed:")
            for model in models:
                print(f"   - {model['name']}")
            return True
        else:
            print("❌ Ollama is running but returned an error")
            return False
    except Exception as e:
        print(f"❌ Ollama is not running: {str(e)}")
        print("💡 Start Ollama with: ollama serve")
        return False

if __name__ == "__main__":
    print("🚀 Stock Research Ollama Test")
    print("=" * 50)
    
    # Check Ollama status first
    if check_ollama_status():
        print("\n")
        test_ollama_integration()
    else:
        print("\n❌ Please start Ollama first and install some models.")
        print("\nQuick setup:")
        print("1. ollama serve")
        print("2. ollama pull llama3.1:8b")
        print("3. python test_ollama.py")
