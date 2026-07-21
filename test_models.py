from google import genai
from config import AI_API_KEY

client = genai.Client(api_key=AI_API_KEY)

for m in client.models.list():
    if "generateContent" in m.supported_actions:
        print(m.name)