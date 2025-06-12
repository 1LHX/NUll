import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量（项目根目录有 .env 文件,其中写有api key）
load_dotenv()

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 读取文件内容
file_path = "output.txt"

if not os.path.exists(file_path):
    print(f"错误：文件 {file_path} 不存在！")
    exit(1)
else:
    with open(file_path, "r", encoding="utf-8") as f:
        original_text = f.read().strip()

    if not original_text or original_text == "无文字内容":
        print("无需纠错的文本内容")
        exit(0)

    # 构造提示词
    prompt = (
        "该文本可能部分汉字存在错误，请你根据语义和读音和常见词组来判断。"
        "请你逐行输出与该文本字符串相同的，语义通顺的经过纠错后的中文句子。"
        "保持原文的行数和格式，每行对应纠错后的内容。"
        "如果某行没有错误，请原样输出。"
        "不需要输出除了纠错后的句子外的其他内容：\n\n"
        + original_text
    )

    try:
        # 发起请求
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "你是一个中文文本纠错助手，请保持原文的行数格式。"},
                {"role": "user", "content": prompt},
            ],
        )

        # 获取模型回复
        corrected_text = completion.choices[0].message.content.strip()
        
        # 将纠错后的文本保存到新文件
        with open("corrected_output.txt", "w", encoding="utf-8") as f:
            f.write(corrected_text)
            
        # 简单输出成功标识，避免编码问题
        print("SUCCESS")

    except Exception as e:
        print(f"文本纠错出现异常: {str(e)}")
        exit(1)