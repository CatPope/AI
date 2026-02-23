from transformers import AutoProcessor, Gemma3nForConditionalGeneration, TextStreamer
from PIL import Image
import torch
import requests
from io import BytesIO

# 모델 ID
model_id = "google/gemma-3n-e4b-it"

# 모델 및 프로세서 로드
model = Gemma3nForConditionalGeneration.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.bfloat16
).eval()

processor = AutoProcessor.from_pretrained(model_id)

# image 불러오기
image_paths = [
    "C:/Users/qwer/Documents/GitHub/AI/LangChain/asking_company/doc/images/20240228501573.webp"
]
# image = Image.open(image_path).convert("RGB")
for image_path in image_paths:
    # 채팅 메시지 구성
    messages = [
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."}]
        },
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image_path},
                {"type": "text", "text": "이 사진이 무엇인지 설명하고, 구체적이게 설명해봐."}
            ]
        }
    ]

    # 입력 텐서 준비
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt"
    ).to(model.device)

    input_len = inputs["input_ids"].shape[-1]

    # 스트리밍 출력 준비
    streamer = TextStreamer(processor.tokenizer, skip_prompt=True, skip_special_tokens=True)

    # 추론 및 실시간 출력
    with torch.inference_mode():
        _ = model.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=False,
            streamer=streamer
        )
