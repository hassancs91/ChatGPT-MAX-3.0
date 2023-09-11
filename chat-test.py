import os
import json
import openai
import streamlit as st
import google_serp
import prompts
import blog_posts
import tokens_count

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "show_token_cost": False,
    "api_key": "",
    "temperature": 0.7,
    "top_p": 1.0,
    "model": "gpt-3.5-turbo",
}


def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_SETTINGS


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)


def handle_reset():
    st.session_state.messages = []
    st.session_state.cumulative_tokens = 0
    st.session_state.cumulative_cost = 0
    update_sidebar_tokens_cost()
    st.write("Conversation and counters have been reset!")
    st.stop()


def update_sidebar_tokens_cost():
    st.sidebar.markdown(
        f"**Total Tokens Used This Session:** {st.session_state.cumulative_tokens}"
    )
    st.sidebar.markdown(
        f"**Total Cost This Session:** ${st.session_state.cumulative_cost:.6f}"
    )


def handle_command(prompt):
    if prompt.strip().lower() == "/reset":
        handle_reset()

    elif prompt.strip().lower().startswith("/summarize"):
        blog_url = prompt.split(" ", 1)[1].strip()
        with st.chat_message("assistant"):
            blog_summary_prompt = blog_posts.get_blog_summary_prompt(blog_url)
            response_obj = openai.ChatCompletion.create(
                model=sidebar_config["model"],
                messages=[{"role": "user", "content": blog_summary_prompt}],
                temperature=sidebar_config["temperature"],
                top_p=sidebar_config["top_p"],
                stream=True,
            )
            blog_summary = ""
            for response in response_obj:
                blog_summary += response.choices[0].delta.get("content", "")
            st.session_state.messages.append(
                {"role": "assistant", "content": blog_summary}
            )

    elif prompt.strip().lower().startswith("/rewrite"):
        input_text = prompt.split(" ", 1)[1].strip()
        with st.chat_message("assistant"):
            rewrite_prompt = prompts.rewrite_prompt.format(text=input_text)
            response_obj = openai.ChatCompletion.create(
                model=sidebar_config["model"],
                messages=[{"role": "user", "content": rewrite_prompt}],
                temperature=sidebar_config["temperature"],
                top_p=sidebar_config["top_p"],
                stream=True,
            )
            new_written_text = ""
            for response in response_obj:
                new_written_text += response.choices[0].delta.get("content", "")
            st.session_state.messages.append(
                {"role": "assistant", "content": new_written_text}
            )

    elif prompt.strip().lower().startswith("/google"):
        input_query = prompt.split(" ", 1)[1].strip()
        with st.chat_message("assistant"):
            search_results = google_serp.search_google_web_automation(input_query)
            overall_summary = ""
            source_links = "\n\nSources:\n\n"
            for result in search_results:
                blog_url = result["url"]
                source_links += blog_url + "\n\n"
                blog_summary_prompt = blog_posts.get_blog_summary_prompt(blog_url)
                response_obj = openai.ChatCompletion.create(
                    model=sidebar_config["model"],
                    messages=[{"role": "user", "content": blog_summary_prompt}],
                    temperature=sidebar_config["temperature"],
                    top_p=sidebar_config["top_p"],
                    stream=True,
                )
                blog_summary = ""
                for response in response_obj:
                    blog_summary += response.choices[0].delta.get("content", "")
                overall_summary += blog_summary
            new_search_prompt = prompts.google_search_prompt.format(
                input=overall_summary
            )
            response_obj = openai.ChatCompletion.create(
                model=sidebar_config["model"],
                messages=[{"role": "user", "content": new_search_prompt}],
                temperature=sidebar_config["temperature"],
                top_p=sidebar_config["top_p"],
                stream=True,
            )
            research_final = ""
            for response in response_obj:
                research_final += response.choices[0].delta.get("content", "")
            st.session_state.messages.append(
                {"role": "assistant", "content": research_final + source_links}
            )

    else:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            response_obj = openai.ChatCompletion.create(
                model=sidebar_config["model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                temperature=sidebar_config["temperature"],
                top_p=sidebar_config["top_p"],
            )
            full_response = ""
            for response in response_obj:
                full_response += response.choices[0].delta.get("content", "")
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
            st.markdown(full_response)

        if st.session_state.settings["show_token_cost"]:
            token_usage = tokens_count.calculate_tokens(st.session_state.messages)
            st.session_state.cumulative_tokens += token_usage
            cost = token_usage / 1000 * 0.06
            st.session_state.cumulative_cost += cost
            update_sidebar_tokens_cost()


def main():
    st.set_page_config(page_title="AI Assistant", layout="wide")

    if "settings" not in st.session_state:
        st.session_state.settings = load_settings()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "cumulative_tokens" not in st.session_state:
        st.session_state.cumulative_tokens = 0

    if "cumulative_cost" not in st.session_state:
        st.session_state.cumulative_cost = 0

    sidebar_config = st.session_state.settings
    openai.api_key = sidebar_config["api_key"]

    st.sidebar.title("Settings")
    sidebar_config["api_key"] = st.sidebar.text_input(
        "OpenAI API Key", value=sidebar_config["api_key"], type="password"
    )
    sidebar_config["model"] = st.sidebar.selectbox(
        "Model", ["gpt-3.5-turbo", "text-davinci-002"], index=0
    )
    sidebar_config["temperature"] = st.sidebar.slider(
        "Temperature", 0.0, 1.0, sidebar_config["temperature"], 0.01
    )
    sidebar_config["top_p"] = st.sidebar.slider(
        "Top P", 0.0, 1.0, sidebar_config["top_p"], 0.01
    )
    sidebar_config["show_token_cost"] = st.sidebar.checkbox(
        "Show Tokens & Cost", sidebar_config["show_token_cost"]
    )
    if st.sidebar.button("Save Settings"):
        save_settings(sidebar_config)

    st.title("Chat with AI Assistant")
    prompt = st.text_input("What would you like to ask?")
    if st.button("Send"):
        handle_command(prompt)

    update_sidebar_tokens_cost()
