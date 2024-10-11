import streamlit as st
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.callbacks.base import BaseCallbackHandler


class StreamHander(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.write(self.text)


def print_messages():
    if "messages" in st.session_state and len(st.session_state["messages"]) > 0:  # noqa E501
        for chat_message in st.session_state["messages"]:
            st.chat_message(chat_message.role).write(f"{chat_message.content}")


def get_session_history(session_ids: str) -> BaseChatMessageHistory:
    print("session_ids:", session_ids)
    if session_ids not in st.session_state["store"]:
        st.session_state["store"][session_ids] = ChatMessageHistory()
    return st.session_state["store"][session_ids]
