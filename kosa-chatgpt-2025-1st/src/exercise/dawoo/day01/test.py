import gradio as gr

history = {"content":"I am happy to provide you that report and plot."}

print(type(history))
with gr.Blocks() as demo:
    gr.Chatbot(history)

demo.launch()