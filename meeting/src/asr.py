import whisper
import os

class ASRService:
    def __init__(self, model_name="base"):
        self.model = whisper.load_model(model_name)

    def transcribe_audio(self, input_path: str, language: str = "ko") -> str:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"파일 없음: {input_path}")
        try:
            result = self.model.transcribe(input_path, fp16=False, language=language)
            return result.get('text', '').strip()
        except Exception as e:
            # 로그 등 연동 가능
            raise RuntimeError(f"Whisper 변환 실패: {e}")

# 테스트 예시 (tests/test_asr.py)
def test_transcribe_audio():
    asr = ASRService()
    text = asr.transcribe_audio("data/input/test_sample.mp3")
    assert isinstance(text, str) and len(text) > 0