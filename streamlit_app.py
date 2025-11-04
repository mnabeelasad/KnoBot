import streamlit as st
import requests
import base64
import json
from streamlit_mermaid import st_mermaid
from pyvis.network import Network
import streamlit.components.v1 as components

# --- Configuration ---
FASTAPI_BASE_URL = "http://127.0.0.1:8000/v1"
API_REGISTER_URL = f"{FASTAPI_BASE_URL}/users/register"
API_LOGIN_URL = f"{FASTAPI_BASE_URL}/users/login"
API_USER_ME_URL = f"{FASTAPI_BASE_URL}/users/me"
API_CONVERSATIONS_URL = f"{FASTAPI_BASE_URL}/conversations"
API_SYNC_MESSAGE_URL = f"{FASTAPI_BASE_URL}/conversations/message"
API_TEXT_STREAM_URL = f"{FASTAPI_BASE_URL}/conversations/message/stream"
API_AGENTS_URL = f"{FASTAPI_BASE_URL}/agents"
API_AGENT_VISUALIZE_URL = f"{FASTAPI_BASE_URL}/agents/{{agent_name}}/visualize"
API_ARTIFACTS_URL = f"{FASTAPI_BASE_URL}/artifacts"
API_UPLOAD_URL = f"{FASTAPI_BASE_URL}/artifacts/upload"
API_CHARACTERS_URL = f"{FASTAPI_BASE_URL}/characters"
API_AUDIO_DOWNLOAD_URL = f"{FASTAPI_BASE_URL}/conversations/message/audio"

# --- Page Setup ---
st.set_page_config(page_title="WattOS AI", layout="wide", initial_sidebar_state="expanded")

# --- Session State ---
if "token" not in st.session_state: st.session_state.token = None
if "user" not in st.session_state: st.session_state.user = None
if "messages" not in st.session_state: st.session_state.messages = []
if "thread_id" not in st.session_state: st.session_state.thread_id = None
if "chat_started" not in st.session_state: st.session_state.chat_started = False
if "audio_mode" not in st.session_state: st.session_state.audio_mode = False
if "character" not in st.session_state: st.session_state.character = "Assistant"
if "llm_model" not in st.session_state: st.session_state.llm_model = "gpt-4o"
if "agent_models" not in st.session_state: st.session_state.agent_models = []
if "characters" not in st.session_state: st.session_state.characters = []

# --- UI Components ---
def login_register_ui():
    st.sidebar.header("Welcome")
    login_tab, register_tab = st.sidebar.tabs(["Login", "Register"])
    with login_tab:
        with st.form(key='login_form'):
            st.markdown("### Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.form_submit_button(label="Login"):
                handle_login(username, password)
    with register_tab:
        with st.form(key='register_form'):
            st.markdown("### Register")
            st.info("Password: 8-64 characters.")
            username = st.text_input("Username", key="register_username")
            password = st.text_input("Password", type="password", key="register_password")
            if st.form_submit_button(label="Register"):
                handle_register(username, password)

def chat_controls_ui():
    if st.session_state.user:
        st.sidebar.markdown(f"Logged in as **{st.session_state.user['username']}**")
    st.sidebar.header("Chat Controls")
    character_names = [char['role'] for char in st.session_state.characters]
    if not character_names: character_names = ["Assistant"]
    st.session_state.character = st.sidebar.selectbox("Select Character", character_names)
    st.session_state.llm_model = st.sidebar.selectbox("Select LLM", ["gpt-4o", "gpt-4-turbo"])
    st.session_state.audio_mode = st.sidebar.checkbox("Enable Audio")
    if st.sidebar.button("Start Conversation"):
        start_new_conversation()
    st.sidebar.button("Logout", on_click=logout)

def main_chat_area():
    tabs = st.tabs(["Chatbot", "Characters", "Upload Documents", "Agent Models", "Account Settings"])
    with tabs[0]: render_chatbot_ui()
    with tabs[1]: render_characters_ui()
    with tabs[2]: render_upload_ui()
    with tabs[3]: render_agent_models_ui()
    with tabs[4]: render_account_settings_ui()

def render_chatbot_ui():
    if not st.session_state.chat_started:
        st.info("Start a new conversation from the sidebar.")
        return
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "audio" in msg and msg["audio"]:
                st.audio(msg["audio"], format="audio/mpeg")
    if prompt := st.chat_input("Your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            if st.session_state.audio_mode:
                text_response, audio_bytes = handle_audio_response(prompt)
                if text_response: st.markdown(text_response)
                if audio_bytes: st.audio(audio_bytes, format="audio/mpeg")
                st.session_state.messages.append({"role": "assistant", "content": text_response, "audio": audio_bytes})
            else:
                full_response = st.write_stream(handle_text_response(prompt))
                st.session_state.messages.append({"role": "assistant", "content": full_response})

def render_characters_ui():
    st.header("Manage Characters")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Available Characters")
        if st.session_state.characters:
            for char in st.session_state.characters:
                with st.expander(f"ID: {char['id']} - Role: {char['role']}"):
                    st.write(f"**Agent Model:** {char['agent_model']}")
                    st.write(f"**Voice ID:** {char['voice_id']}")
                    st.code(char['system_prompt'])
                    if st.button("Delete Character", key=f"delete_{char['id']}"):
                        handle_delete_character(char['id'])
        else:
            st.info("No characters found.")
    with col2:
        st.subheader("New / Update Character")
        with st.form("character_form"):
            char_ids = [c['id'] for c in st.session_state.characters]
            char_roles = [c['role'] for c in st.session_state.characters]
            selected_char_id = st.selectbox("Select Character to Update (optional)", options=[None] + char_ids, format_func=lambda x: "New Character" if x is None else f"ID: {x} - {char_roles[char_ids.index(x)]}")
            char_to_edit = next((c for c in st.session_state.characters if c['id'] == selected_char_id), None)
            role = st.text_input("Role (Name)", value=char_to_edit['role'] if char_to_edit else "")
            agent_model = st.selectbox("Agent Model", st.session_state.agent_models, index=st.session_state.agent_models.index(char_to_edit['agent_model']) if char_to_edit and char_to_edit['agent_model'] in st.session_state.agent_models else 0)
            voice_id = st.text_input("Voice ID", value=char_to_edit['voice_id'] if char_to_edit else "Brian")
            voice_model = st.selectbox("Voice Model", ["eleven_flash_v2_5"], index=0)
            system_prompt = st.text_area("System Prompt", height=150, value=char_to_edit['system_prompt'] if char_to_edit else "")
            if st.form_submit_button("Save Character"):
                payload = {"role": role, "agent_model": agent_model, "voice_id": voice_id, "voice_model": voice_model, "system_prompt": system_prompt}
                if selected_char_id:
                    handle_update_character(selected_char_id, payload)
                else:
                    handle_create_character(payload)

def render_upload_ui():
    st.header("Upload and Manage Documents")
    uploaded_file = st.file_uploader("Choose a PDF file to upload", type="pdf")
    if uploaded_file is not None:
        if st.button(f"Process and Upload '{uploaded_file.name}'"):
            with st.spinner("Uploading and processing file..."):
                try:
                    files = {'file': (uploaded_file.name, uploaded_file, 'application/pdf')}
                    response = requests.post(API_UPLOAD_URL, files=files, headers=get_auth_headers())
                    response.raise_for_status()
                    st.success(f"File '{uploaded_file.name}' processed successfully!")
                    st.rerun()
                except requests.exceptions.RequestException as e: st.error(f"Upload failed: {e}")
    st.divider()
    st.subheader("Available Documents")
    try:
        response = requests.get(API_ARTIFACTS_URL, headers=get_auth_headers())
        response.raise_for_status()
        files = response.json()
        if files:
            for file_name in files: st.write(f"- {file_name}")
        else: st.info("No documents have been uploaded yet.")
    except requests.exceptions.RequestException: st.error("Could not fetch documents.")

def render_agent_models_ui():
    st.header("Agent Models")
    if st.session_state.agent_models:
        selected = st.selectbox("Select Agent to Visualize", st.session_state.agent_models)
        if st.button("Get agent visualization"):
            if selected:
                with st.spinner("Fetching visualization..."):
                    try:
                        url = API_AGENT_VISUALIZE_URL.format(agent_name=selected)
                        res = requests.get(url, headers=get_auth_headers())
                        res.raise_for_status()
                        mermaid_text = res.json()["mermaid_text"]
                        st_mermaid(mermaid_text)
                    except requests.RequestException: st.error("Failed to fetch visualization.")
    else:
        st.warning("No agent models found.")

def render_account_settings_ui():
    st.header("Account Settings")
    with st.form("update_user_form"):
        st.subheader("Change Password")
        new_password = st.text_input("New Password", type="password")
        if st.form_submit_button("Update Password"):
            if new_password:
                handle_update_user({"password": new_password})
            else:
                st.warning("Please enter a new password.")

# --- Helper Functions ---
def handle_login(username, password):
    try:
        res = requests.post(API_LOGIN_URL, data={"username": username, "password": password})
        if res.ok:
            st.session_state.token = res.json()["access_token"]
            user_info_res = requests.get(API_USER_ME_URL, headers=get_auth_headers())
            if user_info_res.ok: st.session_state.user = user_info_res.json()
            st.rerun()
        else: st.sidebar.error("Login failed.")
    except requests.RequestException: st.sidebar.error("Connection failed.")

def handle_register(username, password):
    try:
        res = requests.post(API_REGISTER_URL, json={"username": username, "password": password})
        if res.ok: st.sidebar.success("Registered! Please log in.")
        elif res.status_code == 422: st.sidebar.error("Password must be 8-64 chars.")
        else: st.sidebar.error(f"Failed: {res.json().get('detail', 'Unknown')}")
    except requests.RequestException: st.sidebar.error("Connection failed.")

def handle_create_character(payload):
    try:
        res = requests.post(API_CHARACTERS_URL, json=payload, headers=get_auth_headers())
        res.raise_for_status()
        st.success(f"Character '{payload['role']}' created!")
        fetch_initial_data(force=True)
        st.rerun()
    except requests.RequestException: st.error("Failed to create character.")

def handle_update_character(char_id, payload):
    try:
        res = requests.put(f"{API_CHARACTERS_URL}/{char_id}", json=payload, headers=get_auth_headers())
        res.raise_for_status()
        st.success(f"Character ID {char_id} updated!")
        fetch_initial_data(force=True)
        st.rerun()
    except requests.RequestException: st.error("Failed to update character.")

def handle_delete_character(char_id):
    try:
        res = requests.delete(f"{API_CHARACTERS_URL}/{char_id}", headers=get_auth_headers())
        res.raise_for_status()
        st.success(f"Character ID {char_id} deleted!")
        fetch_initial_data(force=True)
        st.rerun()
    except requests.RequestException: st.error("Failed to delete character.")

def handle_update_user(payload):
    try:
        res = requests.put(API_USER_ME_URL, json=payload, headers=get_auth_headers())
        res.raise_for_status()
        st.success("Password updated successfully!")
    except requests.RequestException: st.error("Failed to update password.")

def get_auth_headers(): return {"Authorization": f"Bearer {st.session_state.token}"}

def start_new_conversation():
    try:
        res = requests.post(API_CONVERSATIONS_URL, headers=get_auth_headers())
        res.raise_for_status()
        st.session_state.thread_id = res.json()["thread_id"]
        st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you today?"}]
        st.session_state.chat_started = True
        st.rerun()
    except requests.RequestException: handle_api_error()

def handle_text_response(prompt):
    payload = {"thread_id": st.session_state.thread_id, "message": prompt, "character": st.session_state.character, "llm_model": st.session_state.llm_model}
    try:
        with requests.post(API_TEXT_STREAM_URL, json=payload, headers=get_auth_headers(), stream=True) as res:
            res.raise_for_status()
            for line in res.iter_lines():
                if line and line.decode().startswith("data:"):
                    try:
                        data = json.loads(line.decode()[5:])
                        if data.get("type") == "token": yield data.get("delta", "")
                    except json.JSONDecodeError: pass
    except requests.RequestException: handle_api_error(); yield ""

def handle_audio_response(prompt):
    try:
        with st.spinner("Thinking and generating audio..."):
            payload = {"thread_id": st.session_state.thread_id, "message": prompt, "character": st.session_state.character, "llm_model": st.session_state.llm_model}
            text_res = requests.post(API_SYNC_MESSAGE_URL, json=payload, headers=get_auth_headers())
            text_res.raise_for_status()
            text_data = text_res.json()["response"]
            audio_payload = {"message": text_data}
            audio_res = requests.post(API_AUDIO_DOWNLOAD_URL, json=audio_payload, headers=get_auth_headers())
            audio_res.raise_for_status()
            audio_bytes = audio_res.content
            return text_data, audio_bytes
    except requests.RequestException: handle_api_error(); return "Error: Could not get response.", None

def handle_api_error(): st.error("API error. Session may have expired."); logout(rerun=False)

def logout(rerun=True):
    keys_to_clear = ["token", "user", "messages", "thread_id", "chat_started", "characters", "agent_models"]
    for key in keys_to_clear:
        if key in st.session_state: st.session_state[key] = [] if key in ["messages", "characters", "agent_models"] else None
    if rerun: st.rerun()

def fetch_initial_data(force=False):
    if force or not st.session_state.agent_models or not st.session_state.characters:
        headers = get_auth_headers()
        try:
            agents_res = requests.get(API_AGENTS_URL, headers=headers)
            if agents_res.ok: st.session_state.agent_models = agents_res.json()
            chars_res = requests.get(API_CHARACTERS_URL, headers=headers)
            if chars_res.ok: st.session_state.characters = chars_res.json()
        except requests.RequestException: st.error("Failed to fetch initial data from backend.")

# --- Main App Logic ---
if st.session_state.token is None:
    login_register_ui()
else:
    if not st.session_state.agent_models or not st.session_state.characters:
        fetch_initial_data()
    chat_controls_ui()
    main_chat_area()