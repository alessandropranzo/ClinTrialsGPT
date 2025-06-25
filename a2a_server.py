"""
A2A Server for ClinTrialsGPT
"""

import os
import asyncio
from typing import Optional
from a2a.server.apps import A2AStarletteApplication
from a2a.server.agent_execution import SimpleRequestContextBuilder
from a2a.server.tasks import InMemoryTaskStore, InMemoryPushNotifier
from a2a.server.events import InMemoryQueueManager
from a2a.server.request_handlers import DefaultRequestHandler
from src.a2a_agent import ClinTrialsAgentExecutor
from src.agent_card import create_agent_card


class ClinTrialsA2AServer:
    """
    A2A Server for Clinical Trials GPT
    """
    
    def __init__(self, openai_api_key: str, model_name: str = "gpt-4o-mini"):
        self.openai_api_key = openai_api_key
        self.model_name = model_name
        self.agent_executor = ClinTrialsAgentExecutor(openai_api_key, model_name)
        self.agent_card = create_agent_card()
        
        # Initialize A2A components
        self.task_store = InMemoryTaskStore()
        # self.push_notifier = InMemoryPushNotifier()
        # self.queue_manager = InMemoryQueueManager()
        
        # Create request handler
        self.request_handler = DefaultRequestHandler(
            agent_executor=self.agent_executor,
            task_store=self.task_store
        )
        
        # Create request context builder
        self.context_builder = SimpleRequestContextBuilder()
        
        # Create the A2A application
        self.app = A2AStarletteApplication(
            agent_card=self.agent_card,
            http_handler=self.request_handler,
            context_builder=self.context_builder
        )
    
    def get_app(self):
        """
        Get the Starlette application
        """
        return self.app.build()


def create_server(openai_api_key: Optional[str] = None, model_name: str = "gpt-4o-mini"):
    """
    Create and configure the A2A server
    """
    # Get OpenAI API key from environment or parameter
    if openai_api_key is None:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            # Try to read from file
            try:
                with open("./src/openai-api-key.txt", "r") as f:
                    openai_api_key = f.read().strip()
            except FileNotFoundError:
                raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable or provide it as a parameter.")
    
    # Create the server
    server = ClinTrialsA2AServer(openai_api_key, model_name)
    return server.get_app()


if __name__ == "__main__":
    import uvicorn
    
    # Create the server
    app = create_server()
    
    # Run the server
    print("Starting ClinTrialsGPT A2A Server...")
    #print("Server will be available at: http://localhost:8000")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 