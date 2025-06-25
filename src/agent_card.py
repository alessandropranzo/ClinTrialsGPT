"""
Agent Card for ClinTrialsGPT A2A Agent
"""

from a2a.types import AgentCard, AgentSkill, AgentCapabilities
import subprocess

def create_agent_card() -> AgentCard:
    """
    Create the agent card for the Clinical Trials GPT agent
    """
    
    # Define the main skill for clinical trials queries
    clinical_trials_skill = AgentSkill(
        id="query_clinical_trials",
        name="query_clinical_trials",
        description="Query the U.S. ClinicalTrials.gov database for information about clinical trials, studies, treatments, and medical research. This skill can search for trials based on conditions, interventions, and other medical terms.",
        tags=["clinical-trials", "medical-research", "drug-trials"],
        examples=[
            "What are the latest clinical trials for Alzheimer's disease?",
            "Find trials for a new treatment for cancer",
            "Search for trials related to heart disease"
        ]
    )

    ip_address = subprocess.run("ipconfig getifaddr en0", shell=True, capture_output=True, text=True).stdout.strip()
    
    # Create the agent card
    agent_card = AgentCard(
        name="ClinTrialsGPT",
        description="A specialized AI agent that provides information from the U.S. ClinicalTrials.gov database. This agent can search for clinical trials, studies, treatments, and medical research based on user queries.",
        version="1.0.0",
        url=f"http://{ip_address}:8000",
        capabilities=AgentCapabilities(
            streaming=False,
            # pushNotifications=False,
            # stateTransitionHistory=False
        ),
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[clinical_trials_skill],
        metadata={
            "author": "Vin Bhaskara and Dr. Philip Mathew, MD",
            "license": "Copyright 2025",
            "repository": "https://github.com/your-repo/ClinTrialsGPT",
            "capabilities": [
                "Search clinical trials by condition, intervention, or keywords",
                "Provide detailed information about clinical studies",
                "Answer questions about medical research and treatments",
                "Maintain conversation context for follow-up questions"
            ],
            "data_sources": [
                "U.S. ClinicalTrials.gov database"
            ],
            "supported_models": [
                "gpt-4o-latest",
                "gpt-4o-mini"
            ]
        }
    )
    
    return agent_card 