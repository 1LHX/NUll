import os
import sys
import base64
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量（项目根目录有 .env 文件,其中写有api key）
load_dotenv()

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


# 将图片转为 data URI
def image_to_data_uri(file_path):
    with open(file_path, "rb") as image_file:
        encoded_str = base64.b64encode(image_file.read()).decode("utf-8")
    mime_type = "image/jpeg" if file_path.lower().endswith(".jpg") or file_path.lower().endswith(
        ".jpeg") else "image/png"
    return f"data:{mime_type};base64,{encoded_str}"


if __name__ == "__main__":
    # 支持命令行参数传入图片路径
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = "image.jpg"

    if not os.path.exists(image_path):
        print(f"错误：文件 {image_path} 不存在！")
        exit(1)

    try:
        # 构造图像数据URI
        image_data_uri = image_to_data_uri(image_path)

        # 自定义提示词（可以自由修改）
        custom_prompt = (
            "请提取这张图片中的所有可见文字内容。"
            "输出纯中文文本内容。"
            "不要遗漏任何段落，输出纯文本即可。"
            "如果图片中没有文字，请输出：无文字内容"
        )

        # 发起请求
        completion = client.chat.completions.create(
            model="qwen-vl-ocr-latest",  # 支持OCR的模型
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data_uri,
                                "min_pixels": 28 * 28 * 4,
                                "max_pixels": 28 * 28 * 8192
                            }
                        },
                        {"type": "text", "text": custom_prompt}
                    ]
                }
            ]
        )

        # 获取识别结果
        extracted_text = completion.choices[0].message.content

        # 将结果保存到 txt 文件（不在控制台输出，避免编码问题）
        output_file_path = "output.txt"
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.write(extracted_text)
            
        # 输出成功标识
        print("OCR_SUCCESS")

    except Exception as e:
        print("出现异常：", str(e))
        exit(1)