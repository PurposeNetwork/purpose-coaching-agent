import anthropic
import streamlit as st

from system_prompt import SYSTEM_PROMPT

MODEL = "claude-sonnet-4-6"
BRAND_COLOR = "#0F4C81"
WELCOME_MESSAGE = (
    "Welcome to the Purpose coaching agent. I'm here to help you think "
    "through leadership challenges. What's on your mind?"
)

st.set_page_config(page_title="Purpose Coaching Agent", page_icon="🧭")

st.markdown(
    f"""
    <style>
    .purpose-header {{
        background-color: {BRAND_COLOR};
        padding: 1.5rem 1.5rem 1.25rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
    }}
    .purpose-header h1 {{
        color: #ffffff;
        font-size: 1.6rem;
        margin: 0;
    }}
    .purpose-header p {{
        color: #d7e3ef;
        font-size: 0.95rem;
        margin: 0.25rem 0 0 0;
    }}
    </style>
    <div class="purpose-header">
        <h1>Purpose Coaching Agent</h1>
        <p>AI coaching for nonprofit leaders</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def check_passcode() -> bool:
    if st.session_state.get("authenticated"):
        return True

    st.subheader("Enter passcode")
    passcode = st.text_input("Passcode", type="password")
    submitted = st.button("Enter")

    if submitted:
        if passcode == st.secrets.get("APP_PASSCODE"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect passcode.")

    return False


if not check_passcode():
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("What's on your mind?")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # The Anthropic API requires the message list to start with a
                # "user" turn, but our history opens with the assistant's
                # welcome message — prepend a synthetic opener so the welcome
                # message still reaches the API as real context.
                api_messages = [
                    {"role": "user", "content": "(The coaching session has started.)"},
                    *st.session_state.messages,
                ]
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=1500,
                    system=SYSTEM_PROMPT,
                    messages=api_messages,
                )
                reply = next(
                    (block.text for block in response.content if block.type == "text"),
                    "",
                )
            except anthropic.APIError as e:
                st.markdown(f"Something went wrong talking to the coaching agent: {e}")
                reply = None
            else:
                st.markdown(reply)

    if reply is not None:
        st.session_state.messages.append({"role": "assistant", "content": reply})
