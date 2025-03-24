import chainlit as cl
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.llms import ChatMessage
from llama_index.llms.gemini import Gemini
import os
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY", "AIzaSyBJl_iA_Bn2QbKUEmrIQc5ZJgbL-Xj510c")

llm = Gemini(model="models/gemini-2.0-flash")

@cl.on_chat_start
async def on_chat_start():
    history = [
        {
            "role": "assistant",
            "content": "Hello! How can I help you?"
        }
    ]
    chat_engine = SimpleChatEngine.from_defaults(llm=llm)
    cl.user_session.set("chat_engine", chat_engine)
    cl.user_session.set("history", history)
    await cl.Message(content="Hello! How can I help you?", author="Assistant").send()

@cl.on_message
async def on_message(message: cl.Message):
    chat_engine =cl.user_session.get("chat_engine")
    history = cl.user_session.get("history")
    history.append(
        {
            "role": "user",
            "content": message.content
        }
    )
    chat_history = [ChatMessage(**chat_message) for chat_message in history]
    response = chat_engine.stream_chat(message.content, chat_history=chat_history)
    msg = cl.Message(content="", author="Assistant")
    for token in response.response_gen:
        await msg.stream_token(token)
    await msg.send()
    # response = await chat_engine.achat(message.content)
    # await cl.Message(content=str(response), author="Assistant").send()
    if cl.context.session.client_type == "copilot":
        fn = cl.CopilotFunction(
            name="test",
            args={
                "message": message.content,
                # "response": str(response)
                "response": msg.content
                }
        )
        await fn.acall()
