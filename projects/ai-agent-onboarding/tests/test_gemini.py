from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Test
response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Say hello!"
)

print(response.text)
print("Google ADK working!")
