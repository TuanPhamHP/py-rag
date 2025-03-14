import chromadb
import openai
import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def generate_embedding(text: str):
    response = openai.embeddings.create(
        model="text-embedding-ada-002",  # Mô hình OpenAI tạo embedding
        input=text
    )
    return response.data[0].embedding

embedding = generate_embedding("Đây là một văn bản cần tạo embedding.")
print(embedding)