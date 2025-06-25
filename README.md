# ClinTrialsGPT v1.0

**Harness the power of LLMs to synthesize and reason over live clinical trial data -- bridging trial evidence and insight in real-time!**

*(c) Copyright 2025. [Vin Bhaskara](https://vinbhaskara.github.io/) and [Dr. Philip Mathew, MD](https://www.linkedin.com/in/philipmathewmd/).*

Tl;dr. Quick installation: `docker run -p 8000:8000 vinbhaskara/clintrialsgpt:latest`

Chat just as you would with ChatGPT -- except that any query relevant to clinical trials will trigger an API call to the ClinicalTrials.gov database with relevant search terms inferred from the user's query (i.e. "agentic retrieval"). The responses to queries are grounded in the clinical trial data retrieved with appropriate citations. 

**Docker hub image link:** [vinbhaskara/clintrialsgpt:latest](https://hub.docker.com/r/vinbhaskara/clintrialsgpt)

**Here is an example screenshot:**

![screenshot](screenshot.png)

## 🆕 A2A Protocol Support

ClinTrialsGPT now supports the **A2A (Agent2Agent) protocol** developed by Google! This allows the agent to be used as a remote service by other applications and agents.

### A2A Features
- **Remote Agent Access**: Use ClinTrialsGPT as a service from other applications
- **Standardized Protocol**: Follows Google's A2A specification for agent communication
- **Streaming Support**: Real-time streaming responses
- **Agent Discovery**: Automatic capability discovery via agent cards
- **Context Management**: Maintain conversation context across requests

### Quick A2A Start
```bash
# Start A2A server
python start_a2a_server.py --mode a2a

# Or use Docker
docker run -p 8000:8000 vinbhaskara/clintrialsgpt:latest
```

For detailed A2A documentation, see [README_A2A.md](README_A2A.md).

## How to run the app?

Find your OpenAI API key by following instructions here: [Link](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key)

Three ways to get the app running - 

### 1. Running on Docker

First, install [Docker](https://www.docker.com/). 

#### Pull image and run (easiest and preferred way)

After installing Docker, open the Terminal/Command Prompt and run:

**For A2A Server (default):**
```bash
docker run -p 8000:8000 vinbhaskara/clintrialsgpt:latest
```

**For Streamlit App:**
```bash
docker run -p 8501:8501 -e RUN_MODE=streamlit vinbhaskara/clintrialsgpt:latest
```

#### Or, build your own image

Run `docker-compose up --build` to build your own local image:
- A2A server will be available at [http://localhost:8000](http://localhost:8000)
- Streamlit app will be available at [http://localhost:8501](http://localhost:8501)

### 2. Installing on your local machine

After installing the required python packages in `requirements.txt`:

**For A2A Server (default):**
```bash
python start_a2a_server.py --mode a2a
# Or directly: python a2a_server.py
```

**For Streamlit App:**
```bash
python start_a2a_server.py --mode streamlit
# Or directly: streamlit run clintrialsgpt.py
```

### 3. Using the startup script

The `start_a2a_server.py` script provides an easy way to choose between modes:

```bash
# Check if OpenAI API key is configured
python start_a2a_server.py --check-key

# Start A2A server (default)
python start_a2a_server.py

# Start Streamlit app
python start_a2a_server.py --mode streamlit
```

## API Endpoints (A2A Server)

Check the official [A2A SDK website](https://a2aproject.github.io/A2A/sdk/python/) for further development info.


## Disclaimer

This tool is for informational and educational purposes only. It does not provide medical advice, diagnosis, or treatment. The information is retrieved from publicly available clinical trials data and may be incomplete, outdated, or misinterpreted.

By using this app, you acknowledge that all use is at your own risk. The creators accept no responsibility or liability for any outcomes, decisions, or actions taken based on the information provided.

Always consult a qualified healthcare professional for medical advice.
