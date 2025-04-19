"""
Run as `streamlit run clintrialsgpt.py`
"""

import streamlit as st
from src.chat_openai_utils import OpenAIClient
import src.prompts as prompts
import copy
from src.clin_trials_api import clinical_trials_api

st.title("*ClinTrialsGPT v1.0*")
st.markdown("**ChatGPT grounded in the latest US Clinical Trials database.**")
st.markdown(
    "*(c) Copyright 2025. [Vin Bhaskara](https://vinbhaskara.github.io/) and [Philip Mathew](https://www.linkedin.com/in/philipmathewmd/).*"
)

model_options = [
    "chatgpt-4o-latest",
    "gpt-4o-mini",
]
selected_option = st.selectbox("Choose an LLM:", model_options, index=1)

with open("./src/openai-api-key.txt", "r") as f:
    api_key_file = f.read().strip()

api_key = st.text_input("OpenAI API Key: ", type="password", value=api_key_file)
if api_key != api_key_file:
    st.session_state["client"] = OpenAIClient(api_key)
    with open("./src/openai-api-key.txt", "w") as f:
        f.write(api_key.strip())

cols = st.columns(4)

with cols[0]:
    if st.button("Reset Context"):
        if "clinical_trials_context" in st.session_state.keys():
            del st.session_state["clinical_trials_context"]

with cols[1]:
    if st.button("Restart App"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()


TOP_NUMBER_OF_TRIALS_TO_CONSIDER = 8

if ("client" not in st.session_state.keys()) or (
    "gpt" not in st.session_state["client_name"]
):
    st.session_state["client"] = OpenAIClient(api_key)
    st.session_state["client_name"] = "gpt"


client = st.session_state["client"]

if "clinical_trials_context" not in st.session_state.keys():
    st.session_state["clinical_trials_context"] = None

clinical_trials_context = st.session_state["clinical_trials_context"]

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": prompts.system_prompt,
        }
    ]

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": prompts.intro_assistant_prompt,
        }
    )

for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Welcome!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        all_messages = copy.deepcopy(st.session_state.messages)

        if clinical_trials_context is None:
            # agentic system - ask the model to see if this is relevant query for meddra
            latest_client_message = dict(
                [i for i in all_messages if i["role"] == "user"][-1]
            )

            latest_client_message["content"] = (
                prompts.agentic_prompt_for_rag_check
                + "\n<user>\n"
                + latest_client_message["content"]
                + "\n</user>\n"
            )

            agentic_response = client.get_chat_response(
                model_name=selected_option,
                messages=[latest_client_message],
                stream=False,
            )

            output_agent_response = agentic_response.choices[0].message.content

            # agentic
            try:
                agentic_response_dict = eval(output_agent_response.strip())
            except Exception as e:
                print(
                    "Bad agentic RAG output that couldn't be eval into dict with expected keys. Output: ",
                    output_agent_response,
                )
                agentic_response_dict = None
                print(e)

        # retrieve from the clinical trials database via the API
        if (clinical_trials_context is not None) or (
            (agentic_response_dict is not None)
            and (sum([len(i.strip()) for i in agentic_response_dict.keys()]) > 0)
        ):
            try:
                if clinical_trials_context is None:
                    condition = " AND ".join(
                        [
                            i.strip()
                            for i in agentic_response_dict["condition"]
                            .strip()
                            .split(",")
                        ]
                    )
                    terms = " AND ".join(
                        [
                            i.strip()
                            for i in agentic_response_dict["terms"].strip().split(",")
                        ]
                    )
                    intervention = " AND ".join(
                        [
                            i.strip()
                            for i in agentic_response_dict["intervention"]
                            .strip()
                            .split(",")
                        ]
                    )
                    st.write(
                        "> `Condition`: [{}], `Intervention`: [{}], `Terms`: [{}]".format(
                            condition, intervention, terms
                        )
                    )

                if (
                    (clinical_trials_context is not None)
                    or (len(condition.strip()) > 0)
                    or (len(terms.strip()) > 0)
                    or (len(intervention.strip()) > 0)
                ):

                    clinical_trials_context = (
                        clinical_trials_api(
                            condition,
                            terms,
                            intervention,
                            topK=TOP_NUMBER_OF_TRIALS_TO_CONSIDER,
                        )
                        if clinical_trials_context is None
                        else clinical_trials_context
                    )

                if len(clinical_trials_context[0]) > 0:
                    st.markdown(
                        "> Trials in context:  \n> "
                        + ",  \n> ".join(clinical_trials_context[0])
                        + "  \n> (To clear the above context in memory, press the *'Reset Context'* button)"
                    )
                else:
                    st.write(
                        "No relevant entries found in the clinical trials database."
                    )
                # change the context only if the similarity is high enough
                user_query = all_messages[-1]["content"]

                if len(clinical_trials_context[0]) > 0:

                    if st.session_state["clinical_trials_context"] is None:
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

                    st.session_state["clinical_trials_context"] = (
                        clinical_trials_context
                    )
                else:
                    clinical_trials_context = None
                    st.session_state["clinical_trials_context"] = None

            except Exception as e:
                print(e)
                print(
                    "Bad agentic RAG converted dict that didn't have expected keys. Eval dict: ",
                    agentic_response_dict,
                )
                clinical_trials_context = None
                st.session_state["clinical_trials_context"] = None

        stream = client.get_chat_response(
            model_name=selected_option, messages=all_messages
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})
