import os
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDUUbsUqJLJ5jg7lfaS54sCnY3-rbukCoc")
genai.configure(api_key=api_key)

print("Available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
