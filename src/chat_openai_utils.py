from openai import OpenAI


class OpenAIClient:
    def __init__(self, openai_api_key):
        self.client = self.get_client_openai(openai_api_key)

    def get_client_openai(self, openai_api_key):
        client = OpenAI(api_key=openai_api_key)
        return client

    def get_chat_response(self, model_name, messages, stream=True):
        stream_ = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": m["role"], "content": m["content"]} for m in messages],
            stream=stream,
        )
        return stream_
