import gradio as gr
from model_setup import load_model
from response_generator import generate_response

model, tokenizer = load_model()

def generate_response_stream(user_input, chat_history):
    try:
        prompt = user_input
        text = generate_response(prompt, model, tokenizer)
        chat_history.append((prompt, ""))
        words = text.split()
        for i, word in enumerate(words):
            chat_history[-1] = (prompt, " ".join(words[:i + 1]))
            yield chat_history
    except Exception as e:
        chat_history.append(("Error", f"Error: {str(e)}"))
        yield chat_history

custom_css = """
#title {
    font-size: 3em;
    text-align: center;
    font-weight: bold;
    margin-bottom: 20px;
    margin-top: 20px;
    color: #333;
}
#interface {
    background-color: #f5f5f5;
    padding: 30px;
    border-radius: 15px;
    width: 80%;
    max-width: 1200px;
    margin: auto;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
#chatbot {
    min-height: auto;
    max-height: none;
    overflow-y: visible;
    border: 0.5px solid #ddd;
    padding: 15px;
    background-color: #ffffff;
    border-radius: 10px;
    line-height: 1.5;
    font-size: 1.6em;
}
#chatbot p {
    margin: 0;
}
"""

with gr.Blocks(css=custom_css) as iface:
    gr.Markdown("<h1 id='title'>Hệ Thống Hỏi Đáp Y Tế VSS AI</h1>")
    gr.Markdown("Nhập câu hỏi của bạn vào ô bên dưới và nhận phản hồi lại từ hệ thống của chúng tôi.")
    chatbot = gr.Chatbot(elem_id="chatbot", label="Trò chuyện")
    user_input = gr.Textbox(label="Nhập câu hỏi của bạn tại đây", placeholder="Ví dụ: Các vấn đề bạn cần hỗ trợ là gì?")
    submit_button = gr.Button("Gửi câu hỏi")

    user_input.submit(generate_response_stream, inputs=[user_input, gr.State([])], outputs=[chatbot])
    submit_button.click(generate_response_stream, inputs=[user_input, gr.State([])], outputs=[chatbot])

iface.launch(share=True)