import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

# 持久维护的对话历史（system 只放一次）
messages = [
    {"role": "system", "content": "你是一个简洁、helpful 的助手。"}
]

print("多轮对话已启动。输入 quit 退出。\n")

while True:
    user_input = input("你: ").strip()
    if not user_input:
        continue
    if user_input.lower() in ("quit", "exit", "退出"):
        print("再见！")
        break

    # 追加用户消息
    messages.append({"role": "user", "content": user_input})

    # 把完整历史发给 API
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
    )

    reply = response.choices[0].message.content
    # 追加 AI 回复，供下一轮使用
    messages.append({"role": "assistant", "content": reply})

    print(f"AI: {reply}\n")