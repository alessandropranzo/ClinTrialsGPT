from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class OpenAIClient:
    def __init__(self, openai_api_key=None):
        # Use provided API key or get from environment
        # api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        # if not api_key:
        #     raise ValueError("OpenAI API key must be provided either as parameter or via OPENAI_API_KEY environment variable")
        
        self.client = OpenAI()

    def get_chat_response(self, model_name, messages, stream=True):
        stream_ = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": m["role"], "content": m["content"]} for m in messages],
            stream=stream,
        )
        return stream_
