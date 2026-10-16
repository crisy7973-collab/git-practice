import os
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)


def calculator(expression: str) -> str:
    """只允许数字和 + - * / ( ) 空格，做四则运算。"""
    allowed = set("0123456789+-*/(). ")
    if not expression or not set(expression) <= allowed:
        return "错误：表达式不合法"
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"错误：{e}"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式，支持加减乘除和括号",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如 (3+5)*2",
                    }
                },
                "required": ["expression"],
            },
        },
    }
]

TOOL_MAP = {"calculator": calculator}

messages = [
    {
        "role": "system",
        "content": "你是助手。遇到算术题必须调用 calculator 工具，不要自己心算。",
    }
]

print("Tool Call 演示。输入 quit 退出。\n")

while True:
    user_input = input("你: ").strip()
    if not user_input:
        continue
    if user_input.lower() in ("quit", "exit", "退出"):
        print("再见！")
        break

    messages.append({"role": "user", "content": user_input})

    # 可能多轮：模型持续要调工具，直到给出最终文字回复
    while True:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=TOOLS,
        )
        msg = response.choices[0].message

        # 没有 tool_calls：普通文字回复，结束本轮
        if not msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content})
            print(f"AI: {msg.content}\n")
            break

        # 先把带 tool_calls 的 assistant 消息写入历史
        messages.append(msg)

        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            print(f"[调用工具] {name}({args})")

            result = TOOL_MAP[name](**args)
            print(f"[工具结果] {result}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                }
            )