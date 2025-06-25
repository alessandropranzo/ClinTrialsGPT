"""
A2A Agent implementation for ClinTrialsGPT
"""

import json
import copy
from typing import Dict, Any, List, Optional
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.context import State
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from src.chat_openai_utils import OpenAIClient
from src.clin_trials_api import clinical_trials_api
import src.prompts as prompts
from a2a.types import TextPart


class ClinTrialsA2AAgent:
    """
    A2A Agent for Clinical Trials GPT
    """
    
    def __init__(self, openai_api_key: str = None, model_name: str = "gpt-4o-mini"):
        self.openai_client = OpenAIClient(openai_api_key)
        self.model_name = model_name
        self.clinical_trials_context = None
        self.messages = [
            {
                "role": "system",
                "content": prompts.system_prompt,
            }
        ]
        self.messages.append(
            {
                "role": "assistant",
                "content": prompts.intro_assistant_prompt,
            }
        )
    
    def _check_if_clinical_trial_query(self, user_message: str) -> Dict[str, str]:
        """
        Check if the user message is related to clinical trials and extract search parameters
        """
        all_client_messages = [{"role": "user", "content": user_message}]
        latest_client_message = all_client_messages[-1]
        latest_client_message["content"] = (
            prompts.agentic_prompt_for_rag_check
            + "\n<user>\n"
            + "\n".join([i["content"] for i in all_client_messages])
            + "\n</user>\n"
        )

        agentic_response = self.openai_client.get_chat_response(
            model_name=self.model_name,
            messages=[latest_client_message],
            stream=False,
        )

        output_agent_response = agentic_response.choices[0].message.content

        try:
            agentic_response_dict = eval(output_agent_response.strip())
            return agentic_response_dict
        except Exception as e:
            print(f"Error parsing agentic response: {e}")
            return {"condition": "", "terms": "", "intervention": ""}
    
    def _search_clinical_trials(self, condition: str, terms: str, intervention: str) -> tuple:
        """
        Search clinical trials using the API
        """
        # Join conditions by AND because someone may be interested in a specific combination of conditions
        condition = " AND ".join(
            [i.strip() for i in condition.strip().split(",") if i.strip()]
        )
        # Join by OR because terms is more like a filtering criteria to narrow down things
        terms = " OR ".join(
            [i.strip() for i in terms.strip().split(",") if i.strip()]
        )
        # Join by OR because one may be interested in looking at multiple OR interactions (e.g. drug or surgical)
        intervention = " OR ".join(
            [i.strip() for i in intervention.strip().split(",") if i.strip()]
        )
        
        if len(condition) + len(intervention) + len(terms) > 0:
            return clinical_trials_api(
                condition, terms, intervention, topK=8
            )
        return [], ""
    
    def _process_with_context(self, user_query: str, clinical_trials_context: tuple) -> str:
        """
        Process user query with clinical trials context
        """
        all_messages = copy.deepcopy(self.messages)
        
        if clinical_trials_context and len(clinical_trials_context[0]) > 0:
            if self.clinical_trials_context is None:
                all_messages[-1]["content"] = (
                    prompts.prompt_before_rag_context_to_prime_model
                    + "\n\n <rag_context>"
                    + clinical_trials_context[1]
                    + "</rag_context>"
                    + "\n\n <user>"
                    + user_query
                    + "</user>"
                )
            else:
                all_messages[-1]["content"] = (
                    prompts.prompt_before_rag_context_to_prime_model_no_summary
                    + "\n\n <rag_context>"
                    + clinical_trials_context[1]
                    + "</rag_context>"
                    + "\n\n <user>"
                    + user_query
                    + "</user>"
                )
        else:
            all_messages.append({"role": "user", "content": user_query})
        
        stream = self.openai_client.get_chat_response(
            model_name=self.model_name, messages=all_messages
        )
        
        # Collect the streamed response
        response_content = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                response_content += chunk.choices[0].delta.content
        
        return response_content
    
    def process_message(self, user_message: str) -> str:
        """
        Main method to process a user message and return a response
        """
        # Check if this is a clinical trial related query
        agentic_response_dict = self._check_if_clinical_trial_query(user_message)
        
        # If we have search parameters, search for clinical trials
        if (self.clinical_trials_context is None and 
            sum([len(i.strip()) for i in agentic_response_dict.values()]) > 0):
            
            try:
                condition = agentic_response_dict.get("condition", "")
                terms = agentic_response_dict.get("terms", "")
                intervention = agentic_response_dict.get("intervention", "")
                
                if len(condition.strip()) > 0 or len(terms.strip()) > 0 or len(intervention.strip()) > 0:
                    self.clinical_trials_context = self._search_clinical_trials(
                        condition, terms, intervention
                    )
            except Exception as e:
                print(f"Error searching clinical trials: {e}")
                self.clinical_trials_context = None
        
        # Process the message with context
        response = self._process_with_context(user_message, self.clinical_trials_context)
        
        # Update conversation history
        self.messages.append({"role": "user", "content": user_message})
        self.messages.append({"role": "assistant", "content": response})
        
        return response


class ClinTrialsAgentExecutor(AgentExecutor):
    """
    A2A Agent Executor for Clinical Trials GPT
    """
    
    def __init__(self, openai_api_key: str, model_name: str = "gpt-4o-mini"):
        self.agent = ClinTrialsA2AAgent(openai_api_key, model_name)
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Execute the agent with the given context
        """
        user_message = ""

        for part in context.message.parts:
            if isinstance(part.root, TextPart):
                user_message += part.root.text
        
        # Process the message
        response = self.agent.process_message(user_message)
        
        # Create the response message
        response_message = new_agent_text_message(response)
        await event_queue.enqueue_event(response_message)
    
    async def cancel(self, context: RequestContext, event_queue) -> None:
        """
        Cancel the current task execution
        """
        # Mark the task as cancelled
        raise NotImplementedError("Not implemented")