import os
import asyncio
import streamlit as st
from openai.types.responses import ResponseTextDeltaEvent, ResponseImageGenCallPartialImageEvent
from agents import Agent, Runner, ImageGenerationTool, TResponseInputItem
import base64
from io import BytesIO
from PIL import Image

from dotenv import load_dotenv

load_dotenv("/home/ubuntu/work/edu-src-all/.env")

agent = Agent(
    name="ChatBot",
    instructions="당신은 이미지 스타일 수정 전문 어시스턴트입니다. 사용자의 요청에 친절하게 대답하세요.",
    model="gpt-4o-mini",
    tools=[
        ImageGenerationTool(
            tool_config={"model":"gpt-image-1-mini", "type": "image_generation", "quality": "medium"},
        )
    ],

)

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

async def chat_with_bot(messages, uploaded_image=None):
    input_items: list[TResponseInputItem] = []

    for msg in messages[:-1]:
        if msg["role"] == "user":
            input_items.append({"role": "user", "content": msg["content"]})
        else:
            input_items.append({"role": "assistant", "content": msg["content"]})

    role = messages[-1]["role"]
    content = messages[-1]["content"]
        
    if uploaded_image:
        image_base64 = image_to_base64(uploaded_image)
        input_items.append({
                "role": "user",
                "content": [
                    {"type": "input_text", "text": content},
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{image_base64}"},
                ],
            }
        )
    else:
        input_items.append({"role": role, "content": content})
    
    result = Runner.run_streamed(agent, input=input_items)
    return result

import uuid

def main():
    st.title("Multi-turn Chatbot with Agent SDK")

    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "uploaded_image" not in st.session_state:
        st.session_state["uploaded_image"] = None

    with st.sidebar:
        st.header("이미지 업로드")
    
        if st.button("초기화"):
            st.session_state["uploaded_image"] = None
            st.session_state["uploader_key"] = str(uuid.uuid4()) 

        uploaded_file = st.file_uploader(
            "이미지를 선택하세요",
            type=["png", "jpg", "jpeg"],
            help="PNG, JPG, JPEG 형식만 지원됩니다.",
            key=st.session_state["uploader_key"]
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="업로드된 이미지")
            st.session_state["uploaded_image"] = image

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            if "img" in msg:
                st.image(msg["img"], msg["content"], use_container_width=True)
            else:
                st.markdown(msg["content"])

    if user_input := st.chat_input("대화를 입력해주세요."):
        st.session_state["messages"].append(
            {
                "role": "user",
                "content": user_input
            }
        )
        with st.chat_message("user"):
            st.markdown(user_input)

        full_response = ""
        img = None
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            async def stream_response():
                nonlocal full_response
                nonlocal img

                result = await chat_with_bot(
                    st.session_state["messages"],
                    st.session_state.get("uploaded_image")
                )
                
                base64_image = ""
                async for event in result.stream_events():
                    if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                        full_response += event.data.delta
                        message_placeholder.markdown(full_response + "▌")
                    elif event.type == "raw_response_event" and isinstance(event.data, ResponseImageGenCallPartialImageEvent):
                        base64_image += event.data.partial_image_b64

                if len(base64_image) > 0:
                    image_data = base64.b64decode(base64_image)
                    img = Image.open(BytesIO(image_data))
                    message_placeholder.image(img, caption=full_response, use_container_width=True)
                else:
                    message_placeholder.markdown(full_response)
            
            asyncio.run(stream_response())

        if img:
            st.session_state["messages"].append(
                {
                    "role": "assistant",
                    "content": full_response,
                    "img": img
                }
            )
        else:
            st.session_state["messages"].append(
                {
                    "role": "assistant",
                    "content": full_response
                }
            )

if __name__ == "__main__":
    main()