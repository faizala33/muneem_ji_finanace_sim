import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: No GOOGLE_API_KEY found in .env file.")
    exit()

print(f"🔑 Found Key: {api_key[:5]}...{api_key[-4:]}")

try:
    # Configure
    genai.configure(api_key=api_key)
    
    # List available models to see what your Key can actually see
    print("\n📋 Checking available models for this key...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name}")

    # Try to generate text
    print("\n🧪 Testing Generation with 'gemini-1.5-flash'...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, are you working?")
    print(f"✅ SUCCESS! Response: {response.text}")

except Exception as e:
    print(f"\n❌ FAILURE: {str(e)}")