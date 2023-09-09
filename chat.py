import openai
import streamlit as st
import json

# Define functions to interact with the JSON file
def load_settings():
    try:
        with open('settings.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_settings(settings):
    with open('settings.json', 'w') as file:
        json.dump(settings, file, indent=4)

#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


# Load settings or use default values if not found
settings = load_settings()

show_token_cost_default = settings.get("show_token_cost", False)
api_key_default = settings.get("api_key", "")
temperature_default = settings.get("temperature", 0.7)
top_p_default = settings.get("top_p", 1.0)
model_default = settings.get("model", "gpt-3.5-turbo")

# Sidebar settings
show_token_cost = True
api_key = st.sidebar.text_input("API Key", api_key_default)
temperature = st.sidebar.slider("Temperature", 0.1, 1.0, temperature_default)
top_p = st.sidebar.slider("Top P", 0.1, 1.0, top_p_default)
model = st.sidebar.selectbox("Model", ["gpt-3.5-turbo", "text-davinci-002"], index=0 if model_default == "gpt-3.5-turbo" else 1)

# Update settings with the new values
settings.update({
    "show_token_cost": show_token_cost,
    "api_key": api_key,
    "temperature": temperature,
    "top_p": top_p,
    "model": model
})
save_settings(settings)


def calculate_tokens(tokens : float):
    return tokens

if "cumulative_tokens" not in st.session_state:
    st.session_state.cumulative_tokens = 0
if "cumulative_cost" not in st.session_state:
    st.session_state.cumulative_cost = 0

cost_per_token = 0.01  # Hypothetical cost, you should replace it with the actual cost.


st.title("ChatGPT Max 3.0")

# Sidebar for API Key, Model Selection, and Model Parameters
st.sidebar.header("Settings")

# Display cumulative tokens and cost in the left sidebar
# st.sidebar.markdown(f"**Total Tokens Used This Session:** {st.session_state.cumulative_tokens}")
# st.sidebar.markdown(f"**Total Cost This Session:** ${st.session_state.cumulative_cost:.2f}")




# Set the API key if it's provided
if api_key:
    openai.api_key = api_key
else:
    st.warning("Please provide a valid OpenAI API Key.")
    st.stop()



if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def google_search(query):
    """
    Search Google and return the top 3 results' URLs.
    """
    return f"Top # Google Results for {query}"

if prompt := st.chat_input("What is up?"):


    if prompt.strip().lower().startswith("/search google "):
        search_query = prompt.replace("search google ", "", 1)
        results = google_search(search_query)
        formatted_results = "\n".join([f"- {url}" for url in results])
        response_text = f"Top 3 Google results for '{search_query}':\n{formatted_results}"
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(response_text)
        st.stop()

    # Check for "reset" command from user
    if prompt.strip().lower() == "/reset":
        st.session_state.messages = []  # Clear the conversation
        st.session_state.cumulative_tokens = 0  # Reset cumulative tokens
        st.session_state.cumulative_cost = 0  # Reset cumulative cost
        st.sidebar.markdown(f"**Total Tokens Used This Session:** {st.session_state.cumulative_tokens}")
        st.sidebar.markdown(f"**Total Cost This Session:** ${st.session_state.cumulative_cost:.2f}")
        st.write("Conversation and counters have been reset!")
        st.stop()  # Halts further execution for this run of the app

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        response_obj = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
            temperature=temperature,
            top_p=top_p,
        )

        for response in response_obj:
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
            
        
        if show_token_cost:
            total_tokens_used = calculate_tokens(500)
            total_cost = total_tokens_used * cost_per_token
            st.session_state.cumulative_tokens += total_tokens_used
            st.session_state.cumulative_cost += total_cost

            # Redisplay the updated cumulative tokens and cost in the left sidebar
            st.sidebar.markdown(f"**Total Tokens Used This Session:** {st.session_state.cumulative_tokens}")
            st.sidebar.markdown(f"**Total Cost This Session:** ${st.session_state.cumulative_cost:.2f}")
        
       
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

