import os
import streamlit as st
from utils import get_session_history, print_messages, StreamHander
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import ChatMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="ChatApp", page_icon=":speech_balloon:")
st.title("ChatApp")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "store" not in st.session_state:
    st.session_state["store"] = dict()

with st.sidebar:
    session_id = st.text_input("Session ID", value="test_session")

    clear_btn = st.button("Clear")
    if clear_btn:
        st.session_state["messages"] = []
        st.rerun()

# 以前のメッセージを表示
print_messages()

if user_input := st.chat_input("メッセージを入力してください"):
    # ユーザーの入力
    st.chat_message("user").write(f"{user_input}")
    st.session_state["messages"].append(ChatMessage(role="user", content=user_input))  # noqa E501

    # AIの返答
    with st.chat_message("assistant"):
        stream_hander = StreamHander(st.empty())

        # LLMを使ってAIの返答を生成
        api_key = os.getenv("OPENAI_API_KEY")
        llm = ChatOpenAI(
            api_key=api_key,
            streaming=True,
            callbacks=[stream_hander]
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Answer briefly to the following question. "
                ),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}")
            ]
        )
        chain = prompt | llm

        chain_with_memory = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )

        response = chain_with_memory.invoke(
            {"question": user_input},
            config={"configurable": {"session_id": session_id}}
        )

        st.session_state["messages"].append(ChatMessage(role="assistant", content=response.content))  # noqa E501