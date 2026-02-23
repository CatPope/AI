import requests
import json
import sys
import unicodedata
from dotenv import load_dotenv
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_core.messages import HumanMessage
from langchain_teddynote.logging import langsmith
from langchain_core.language_models.llms import LLM
from typing import Optional
from PIL import Image


load_dotenv()
langsmith("llm_test", set_enable=True)
class RESTAPILLM(LLM):
    api_url: str
    n_predict: int = 50
    temperature: float = 0.2
    system_prompt: Optional[str] = ""

    def _call(self, prompt, stop=None):
        headers = {"Content-Type": "application/json"}
        payload = {
            "prompt": f"{self.system_prompt}/n질문: {prompt}",
            "n_predict": self.n_predict,
            "temperature": self.temperature,
            "stream": False
        }
        response = requests.post(self.api_url, headers=headers, json=payload)
        if response.ok:
            data = response.json()
            return data.get("content", "")
        else:
            return f"[REST API 오류] {response.status_code}: {response.text}"

    @property
    def _llm_type(self):
        return "rest_api_llm"

if __name__ == "__main__":
    while True:
        mode = input("select mode( server/local ): ")
        if mode == "server":
            api_url = "http://192.168.10.239:8081/completion"  # 실제 서버 주소로 교체
            system_prompt = ""

            llm = RESTAPILLM(
                api_url=api_url,
                n_predict=30000,
                temperature=0,
                system_prompt=system_prompt,
            )
            break
        elif mode == "local":
            model_path = "C:/Users/qwer/Documents/GitHub/AI/LangChain/asking_company/model/gemma-3-r1984-27b-q8_0.gguf"
            llm = LlamaCpp(
                model_path=model_path,
                n_ctx=30000,
                n_gpu_layers=-1,
                temperature=0.2,
                verbose=True,
            )
            break
    while True:
        try:
            usr_inp = input("user: ")
            if usr_inp.strip().lower() in ["exit", "quit", "q"]:
                print("대화를 종료합니다.")
                break
            elif usr_inp.strip() == "":
                continue
            elif usr_inp == "image":
                image_url = input("image URL: ")
                image = Image.open(image_url).convert("RGB")
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": "Describe this image in detail."},
                        {"type": "image", "image": image},
                    ],
                )
            else:
                message = HumanMessage(content=usr_inp)

            print("chat: ", end="")
            result  = llm.invoke([message])
            print(result)
        except KeyboardInterrupt:
            print("/n[종료] 사용자가 중단하였습니다.")
            break
        except Exception as e:
            print(f"/n[에러] {e}")