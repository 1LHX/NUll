# -*- coding: utf-8 -*-
"""
示例：如何从其他代码文件调用文本纠错器
"""

from text_file_corrector import text_file_corrector
import os

def main():
    """示例主函数"""
    print("文本纠错器调用示例")
    print("=" * 50)
    
    # 输入文件路径
    input_file = "input_text.txt"
    
    # 方法1：使用默认设置
    print("方法1：使用默认设置进行纠错")
    result1 = text_file_corrector(input_file)
    
    if result1["success"]:
        print(f"✓ 纠错成功！")
        print(f"  输入文件: {input_file}")
        print(f"  输出文件: {result1['output_file_path']}")
        print(f"  总行数: {result1['total_lines']}")
        print(f"  纠错行数: {result1['corrected_lines']}")
        print(f"  纠错率: {result1['correction_rate']:.1f}%")
    else:
        print(f"✗ 纠错失败: {result1['error']}")
    
    print()
    
    # 方法2：自定义配置
    print("方法2：使用自定义配置进行纠错")
    result2 = text_file_corrector(
        input_file_path=input_file,
        strategy='pipeline',  # 使用流水线策略
        use_models=['kenlm', 'macbert'],  # 只使用指定模型
        show_progress=True  # 显示进度
    )
    
    if result2["success"]:
        print(f"✓ 纠错成功！")
        print(f"  输出文件: {result2['output_file_path']}")
        
        # 可以继续处理纠错后的文件
        corrected_file = result2['output_file_path']
        print(f"\n查看纠错后的文件内容:")
        try:
            with open(corrected_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content[:200] + "..." if len(content) > 200 else content)
        except Exception as e:
            print(f"读取文件失败: {e}")
    else:
        print(f"✗ 纠错失败: {result2['error']}")

def batch_correct_files(file_list):
    """批量处理多个文件的示例"""
    print("\n批量处理示例")
    print("=" * 50)
    
    results = []
    for file_path in file_list:
        print(f"处理文件: {file_path}")
        result = text_file_corrector(file_path, show_progress=False)
        results.append(result)
        
        if result["success"]:
            print(f"  ✓ 成功，输出: {result['output_file_path']}")
        else:
            print(f"  ✗ 失败: {result['error']}")
    
    return results

if __name__ == "__main__":
    # 确保输入文件存在
    input_file = "input_text.txt"
    if not os.path.exists(input_file):
        print(f"创建示例输入文件: {input_file}")
        with open(input_file, 'w', encoding='utf-8') as f:
            sample_texts = [
                "少先队员因该为老人让坐",
                "人可能够识别这个问题", 
                "这个问题很中要",
                "老是较书的人",
                "我爱我的祖国天氨门"
            ]
            for text in sample_texts:
                f.write(text + '\n')
        print("示例文件已创建")
    
    # 运行示例
    main()
    
    # 批量处理示例（如果有多个文件）
    file_list = [input_file]  # 可以添加更多文件
    if len(file_list) > 0:
        batch_correct_files(file_list)
