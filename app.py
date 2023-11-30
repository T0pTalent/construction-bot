import gradio as gr
import random
import time
from bot import ChatBot

my_bot = ChatBot()
openai_key = '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'
with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.Button("Clear")

    def user(user_message, history):
        return "", history + [[user_message, None]]

    def bot(history):
        print(history[-1][0])
        bot_message = my_bot.run(history[-1][0])
        print(bot_message)
        history[-1][1] = ""
        for character in bot_message:
            history[-1][1] += character
            time.sleep(0.005)
            yield history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)
    
demo.queue()
demo.launch(share=True)
