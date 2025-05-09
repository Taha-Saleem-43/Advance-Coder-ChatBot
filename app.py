import gradio as gr
import gradio.themes as themes
import os
import requests

# Load GROQ API key from environment variable
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-70b-8192"  # Balanced and fast for Q&A bots

# Customize this system prompt based on your bot's role
SYSTEM_PROMPT = """
You are an expert software engineer and code analyst.
Your responsibilities include writing efficient, clean, and optimized code, analyzing complex programming problems, suggesting improvements, refactoring code, and providing detailed explanations.
You are familiar with advanced topics such as algorithms, data structures, system design, concurrency, optimization, and debugging across languages like Python, C++, and JavaScript.
Respond with professional, accurate, and clear code and reasoning.
"""

def query_groq(message, chat_history):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for user, bot in chat_history:
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": bot})

    # Add latest user message outside the loop
    messages.append({"role": "user", "content": message})

    response = requests.post(GROQ_API_URL, headers=headers, json={
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7
    })

    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        return reply
    else:
        return f"Error {response.status_code}: {response.text}"

def respond(message, chat_history):
    bot_reply = query_groq(message, chat_history)
    chat_history.append((message, bot_reply))
    return "", chat_history

with gr.Blocks(theme=themes.Soft()) as demo:
    gr.Markdown("## Dyno-Coder-BOT 🤖")

    chatbot = gr.Chatbot()
    state = gr.State([])

    with gr.Row():
        msg = gr.Textbox(
            show_label=False,
            placeholder="Type your question here...",
            container=False,
            scale=9
        )
        send = gr.Button("➤", scale=1)  # Compact icon-style button

    clear = gr.Button("Clear Chat")

    send.click(respond, [msg, state], [msg, chatbot])
    msg.submit(respond, [msg, state], [msg, chatbot])  # ENTER key support
    clear.click(lambda: ([], []), None, [chatbot, state])

demo.launch()
