import tkinter as tk
from talking import Talking  # Talking 클래스가 정의된 파일을 임포트합니다.
import time

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatBot Control Panel")

        self.talking_instance = Talking()

        self.start_button = tk.Button(root, text="Start Chat", command=self.start_chat)
        self.start_button.pack(pady=20)

        self.stop_button = tk.Button(root, text="Stop Chat", command=self.stop_chat, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

    def start_chat(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.run_chat_loop()

    def stop_chat(self):
        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

    def run_chat_loop(self):
        while True:
            response, imotion = self.talking_instance.get_response_imotion()
            TTS(response)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
