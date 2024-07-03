import tkinter as tk
from talking import Talking  # Talking 클래스가 정의된 파일을 임포트합니다.

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
        self.talking_instance.stop = False
        self.run_chat_loop()

    def stop_chat(self):
        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.talking_instance.stop = True

    def run_chat_loop(self):
        while not self.talking_instance.stop:
            question = self.talking_instance.STT()
            print(f"나> {question}")

            question = self.talking_instance.handle_exit(question)
            if self.talking_instance.stop:
                print("대화를 종료합니다.")
                self.talking_instance.TTS("안녕~")
                question = ""
            
            while self.talking_instance.stop:
                print("중단중...")
                self.talking_instance.TTS("중단중입니다.")
                self.root.update()  # GUI를 업데이트하여 반응성 유지
                time.sleep(1)

            if question:
                response = self.talking_instance.ask(question)
                print(f"강정이> {response}")
                self.talking_instance.TTS(response)
                self.root.update()  # GUI를 업데이트하여 반응성 유지

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
