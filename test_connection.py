import os
from openai import OpenAI

api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("未找到 DEEPSEEK_API_KEY，请先设置环境变量")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "只回复：连通成功"}],
)

print(response.choices[0].message.content)