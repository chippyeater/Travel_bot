import os
import requests
import json
import sqlite3

# 设置OpenAI API Key
openai_api_key = "hk-yh7svb10000382049a9d4fc4b45d30d17534947f19e7b6c4"

# 设置OpenAI API头信息
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_api_key}"
}

def call_openai_api(messages):
    data = {
        "max_tokens": 2000,
        "model": "gpt-3.5-turbo",
        "temperature": 0.8,
        "top_p": 1,
        "presence_penalty": 1,
        "messages": messages
    }
    response = requests.post("https://api.openai-hk.com/v1/chat/completions", headers=headers, data=json.dumps(data).encode('utf-8'))
    result = response.json()
    return result['choices'][0]['message']['content']

