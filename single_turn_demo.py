import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

question = input("请输入一个问题: ").strip()

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": question}],
)

print("\nAI 回复:")
print(response.choices[0].message.content)