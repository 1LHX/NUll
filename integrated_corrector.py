"""
# 处理文本文件
python integrated_corrector.py text_input.txt

# 处理图片文件
python integrated_corrector.py image.png

# 处理视频文件
python integrated_corrector.py video_20250612_121048.mp4
"""

import subprocess
import sys
import os
import cv2
from pathlib import Path
import shutil

# 设置控制台编码为UTF-8（解决Windows中文显示问题）
import locale

if sys.platform == "win32":
    try:
        # 尝试设置控制台代码页为UTF-8
        os.system("chcp 65001 > nul")
        # 设置标准输出编码
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


# 检查并安装必要的模块
def check_and_install_requirements():
    """检查并安装必要的依赖包"""
    try:
        import cv2
        import numpy as np
        return True
    except ImportError as e:
        missing_module = str(e).split("'")[1] if "'" in str(e) else "unknown"
        print(f"缺少必要模块: {missing_module}")

        if missing_module == "cv2":
            return install_opencv()
        elif missing_module == "numpy":
            return install_numpy()
        else:
            print(f"未知模块错误: {missing_module}")
            return False


def is_conda_environment():
    """检查是否在conda环境中"""
    return 'conda' in sys.executable.lower() or 'anaconda' in sys.executable.lower() or os.environ.get(
        'CONDA_PREFIX') is not None


def install_opencv():
    """安装OpenCV"""
    if is_conda_environment():
        print("检测到conda环境，正在安装 opencv...")
        try:
            subprocess.check_call(["conda", "install", "-c", "conda-forge", "opencv", "-y"])
            print("opencv 安装成功")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("conda安装失败，尝试使用pip...")

    print("📦 正在使用pip安装 opencv-python...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python"])
        print("opencv-python 安装成功")
        return True
    except subprocess.CalledProcessError:
        print("opencv-python 安装失败")
        print("请手动安装:")
        print("  conda环境: conda install -c conda-forge opencv")
        print("  pip环境: pip install opencv-python")
        return False


def install_numpy():
    """安装NumPy"""
    if is_conda_environment():
        print("检测到conda环境，正在安装 numpy...")
        try:
            subprocess.check_call(["conda", "install", "numpy", "-y"])
            print("numpy 安装成功")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("conda安装失败，尝试使用pip...")

    print("正在使用pip安装 numpy...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
        print("numpy 安装成功")
        return True
    except subprocess.CalledProcessError:
        print("numpy 安装失败，请手动安装: pip install numpy")
        return False


def detect_file_type(file_path):
    """检测文件类型"""
    if not os.path.exists(file_path):
        return None

    file_ext = file_path.lower().split('.')[-1]

    # 图片格式
    image_formats = ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'webp']
    # 视频格式
    video_formats = ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm', 'm4v']
    # 文本格式
    text_formats = ['txt', 'text']

    if file_ext in image_formats:
        return 'image'
    elif file_ext in video_formats:
        return 'video'
    elif file_ext in text_formats:
        return 'text'
    else:
        return 'unknown'


def extract_frames_from_video(video_path, output_dir="temp_frames", frame_interval=60):
    """从视频中提取关键帧"""
    import cv2

    if not os.path.exists(video_path):
        print(f"视频文件不存在: {video_path}")
        return []

    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)

    # 检查视频是否成功打开
    if not cap.isOpened():
        print(f"无法打开视频文件: {video_path}")
        return []

    # 获取视频信息
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0

    print(f"视频信息: 总帧数={total_frames}, FPS={fps:.2f}, 时长={duration:.2f}秒")
    print(f"开始从视频中提取帧（每{frame_interval}帧提取一次）...")

    frame_count = 0
    saved_frames = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame_path = os.path.join(output_dir, f"frame_{frame_count:06d}.jpg")
            # 计算时间点（秒）
            timestamp = frame_count / fps if fps > 0 else 0
            # 提高图片质量
            cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            saved_frames.append((frame_path, timestamp))
            print(f"  保存帧: {frame_path} (时间: {timestamp:.2f}秒)")

        frame_count += 1

    cap.release()
    print(f"共提取了 {len(saved_frames)} 帧")
    return saved_frames


def process_video_ocr(video_path):
    """处理视频OCR识别"""
    frames = extract_frames_from_video(video_path)
    if not frames:
        return False

    all_text = []
    frame_timestamps = []

    for i, (frame_path, timestamp) in enumerate(frames):
        print(f"\n处理第 {i + 1}/{len(frames)} 帧: {frame_path} (时间: {timestamp:.2f}秒)")

        recog_result = subprocess.run(
            [sys.executable, "Recognition.py", frame_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        print(f"  返回码: {recog_result.returncode}")

        if recog_result.returncode == 0 and "OCR_SUCCESS" in recog_result.stdout:
            if os.path.exists("output.txt"):
                with open("output.txt", "r", encoding='utf-8') as f:
                    frame_text = f.read().strip()
                    if frame_text and frame_text != "无文字内容":
                        all_text.append(frame_text)
                        frame_timestamps.append(timestamp)
                        print(f"  识别到文字: {frame_text[:50]}...")
                    else:
                        print(f"  该帧无文字内容")
                try:
                    os.remove("output.txt")
                except:
                    pass
            else:
                print(f"  未找到输出文件")
        else:
            print(f"  第 {i + 1} 帧识别失败")
            if recog_result.stderr:
                print(f"  错误: {recog_result.stderr}")

    # 清理临时文件
    for frame_path, _ in frames:
        try:
            os.remove(frame_path)
        except:
            pass

    try:
        os.rmdir("temp_frames")
    except:
        pass

    if not all_text:
        print("未从视频中识别到任何文字")
        return False

    # 合并所有文本并去重，同时保存时间信息
    unique_data = []
    seen_texts = set()

    for text, timestamp in zip(all_text, frame_timestamps):
        if text not in seen_texts:
            unique_data.append((text, timestamp))
            seen_texts.add(text)

    # 保存文本到临时文件
    combined_text = "\n".join([text for text, _ in unique_data])

    with open("temp_extracted_text.txt", "w", encoding='utf-8') as f:
        f.write(combined_text)

    # 保存时间信息到单独文件
    with open("timestamps.txt", "w", encoding='utf-8') as f:
        for text, timestamp in unique_data:
            f.write(f"{timestamp:.2f}秒: {text}\n")

    print(f"视频文字识别完成，共识别 {len(unique_data)} 段文字")
    return True


def process_image_ocr(image_path=None):
    """处理图像OCR识别"""
    print("开始执行图像识别任务...")

    # 构建命令参数
    cmd = [sys.executable, "Recognition.py"]
    if image_path:
        cmd.append(image_path)

    recog_result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    if recog_result.returncode != 0 or "OCR_SUCCESS" not in recog_result.stdout:
        print(f"图像识别失败！错误信息：\n{recog_result.stderr}")
        return False

    if not os.path.exists("output.txt"):
        print("未找到输出文件 output.txt")
        return False

    # 将识别结果保存到临时文件
    shutil.copy("output.txt", "temp_extracted_text.txt")

    print("图像识别完成")
    return True


def process_text_file_correction(input_file):
    """使用 text_file_corrector.py 进行第一次纠错"""
    print("\n" + "=" * 60)
    print("第一步：使用 text_file_corrector.py 进行纠错")
    print("=" * 60)

    try:
        # 导入 text_file_corrector 模块
        from text_file_corrector import text_file_corrector

        # 使用 text_file_corrector 进行纠错
        result = text_file_corrector(
            input_file_path=input_file,
            strategy='pipeline',  # 使用流水线策略
            use_models=['kenlm', 'macbert', 'ernie', 'confusion'],  # 使用多个模型
            show_progress=True  # 显示进度
        )

        if result["success"]:
            print(f"第一次纠错成功！")
            print(f"  输入文件: {input_file}")
            print(f"  输出文件: {result['output_file_path']}")
            print(f"  总行数: {result['total_lines']}")
            return result['output_file_path']
        else:
            print(f"第一次纠错失败: {result['error']}")
            return None

    except ImportError:
        print("无法导入 text_file_corrector 模块，请确保 text_file_corrector.py 文件存在")
        return None
    except Exception as e:
        print(f"第一次纠错过程中发生错误: {e}")
        return None


def process_二级_correction(input_file):
    """使用 QwenRewrite.py 进行二级纠错"""
    print("\n" + "=" * 60)
    print("第二步：使用 QwenRewrite.py 进行二级纠错")
    print("=" * 60)

    # 将第一次纠错的结果复制到 output.txt（QwenRewrite.py 的输入文件）
    try:
        shutil.copy(input_file, "output.txt")
    except Exception as e:
        print(f"复制文件失败: {e}")
        return False

    # 先显示第一次纠错后的内容
    # with open("output.txt", "r", encoding='utf-8') as f:
    #     first_correction_text = f.read().strip()
    #     print(f"第一次纠错后内容: {first_correction_text}")

    correction_result = subprocess.run(
        [sys.executable, "QwenRewrite.py"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    if correction_result.returncode == 0:
        print("二级纠错完成")

        # 直接从文件读取最终纠错结果
        if os.path.exists("corrected_output.txt"):
            # with open("corrected_output.txt", "r", encoding='utf-8') as f:
            #     final_corrected_content = f.read().strip()
            #     print(f"最终纠错结果: {final_corrected_content}")

            # 如果有时间戳信息，创建带时间戳的纠错结果
            if os.path.exists("timestamps.txt"):
                create_timestamped_correction()
                print(f"带时间戳的纠错结果已保存到 corrected_with_timestamps.txt")
            else:
                print(f"最终纠错结果已保存到 corrected_output.txt")
        else:
            print("未找到最终纠错结果文件")

        return True
    else:
        print("二级纠错失败")
        if correction_result.stderr:
            print(f"错误信息: {correction_result.stderr}")
        return False


def create_timestamped_correction():
    """创建带时间戳的纠错结果"""
    if not os.path.exists("timestamps.txt") or not os.path.exists("corrected_output.txt"):
        return

    # 读取时间戳信息
    timestamps_data = []
    with open("timestamps.txt", "r", encoding='utf-8') as f:
        for line in f:
            if ": " in line:
                timestamp_str, original_text = line.strip().split(": ", 1)
                timestamps_data.append((timestamp_str, original_text))

    # 读取纠错结果
    with open("corrected_output.txt", "r", encoding='utf-8') as f:
        corrected_content = f.read().strip()

    # 处理纠错结果 - 可能是单行或多行
    if '\n' in corrected_content:
        corrected_lines = corrected_content.split('\n')
    else:
        # 如果是单行文本，按原文分割数量来处理
        corrected_lines = [corrected_content] * len(timestamps_data)

    # 匹配纠错结果与时间戳
    corrected_with_timestamps = []

    for i, (timestamp_str, original_text) in enumerate(timestamps_data):
        if i < len(corrected_lines):
            corrected_text = corrected_lines[i].strip()
        else:
            corrected_text = corrected_content.strip()  # 使用完整的纠错结果

        # 检查是否有修改
        if corrected_text != original_text:
            corrected_with_timestamps.append(f"[{timestamp_str}] 原文: {original_text}")
            corrected_with_timestamps.append(f"[{timestamp_str}] 纠错: {corrected_text}")
            corrected_with_timestamps.append(f"[{timestamp_str}] 修改: {original_text} → {corrected_text}")
        else:
            corrected_with_timestamps.append(f"[{timestamp_str}] 文本: {corrected_text}")

        corrected_with_timestamps.append("")  # 添加空行分隔

    # 保存带时间戳的纠错结果
    with open("corrected_with_timestamps.txt", "w", encoding='utf-8') as f:
        f.write("\n".join(corrected_with_timestamps))


def cleanup_temp_files():
    """清理临时文件"""
    temp_files = [
        "output.txt",
        "timestamps.txt",
        "temp_extracted_text.txt"
    ]

    for temp_file in temp_files:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"删除临时文件 {temp_file} 时发生错误: {e}")


def main():
    input_file = None
    file_type = None

    # 检查命令行参数
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        file_type = detect_file_type(input_file)

        if file_type is None:
            print(f"文件不存在: {input_file}")
            return
        elif file_type == 'unknown':
            print(f"不支持的文件格式: {input_file}")
            print("支持的格式:")
            print("  文本: txt, text")
            print("  图片: jpg, jpeg, png, bmp, gif, tiff, webp")
            print("  视频: mp4, avi, mov, mkv, flv, wmv, webm, m4v")
            return

        print(f"检测到 {file_type} 文件: {input_file}")
    else:
        print("请指定输入文件")
        print("用法: python integrated_corrector.py <文件路径>")
        print("支持文本文件(.txt)、图片文件、视频文件")
        return

    try:
        # 根据文件类型处理
        if file_type == 'text':
            # 文本文件：直接进行两次纠错
            print("\n处理文本文件，将进行两次纠错")

            # 第一次纠错：使用 text_file_corrector.py
            first_corrected_file = process_text_file_correction(input_file)
            if not first_corrected_file:
                print("第一次纠错失败，终止处理")
                return

            # 第二次纠错：使用 QwenRewrite.py 二级
            if not process_二级_correction(first_corrected_file):
                print("第二次纠错失败")
                return

        elif file_type == 'video':
            # 视频文件：先提取文本，再进行两次纠错
            print("\n处理视频文件，将提取文本后进行两次纠错")

            # 检查并安装视频处理依赖
            if not check_and_install_requirements():
                print("依赖安装失败，无法处理视频文件")
                return

            # 提取视频中的文本
            if not process_video_ocr(input_file):
                print("视频文本提取失败，终止处理")
                return

            # 第一次纠错：使用 text_file_corrector.py
            first_corrected_file = process_text_file_correction("temp_extracted_text.txt")
            if not first_corrected_file:
                print("第一次纠错失败，终止处理")
                return

            # 第二次纠错：使用 QwenRewrite.py 二级
            if not process_二级_correction(first_corrected_file):
                print("第二次纠错失败")
                return

        elif file_type == 'image':
            # 图片文件：先提取文本，再进行两次纠错
            print("\n处理图片文件，将提取文本后进行两次纠错")

            # 提取图片中的文本
            if not process_image_ocr(input_file):
                print("图片文本提取失败，终止处理")
                return

            # 第一次纠错：使用 text_file_corrector.py
            first_corrected_file = process_text_file_correction("temp_extracted_text.txt")
            if not first_corrected_file:
                print("第一次纠错失败，终止处理")
                return

            # 第二次纠错：使用 QwenRewrite.py 二级
            if not process_二级_correction(first_corrected_file):
                print("第二次纠错失败")
                return

        print("\n" + "=" * 60)
        print("所有处理步骤完成！")
        print("=" * 60)

        # 显示最终结果文件
        if os.path.exists("corrected_output.txt"):
            print("最终纠错结果文件: corrected_output.txt")

        if os.path.exists("corrected_with_timestamps.txt"):
            print("带时间戳的纠错结果文件: corrected_with_timestamps.txt")

        print("\n请查看输出文件以查看最终纠错结果。")

    except KeyboardInterrupt:
        print("\n\n⚠程序被用户中断")
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理临时文件
        cleanup_temp_files()
        print("\n已清理临时文件")


if __name__ == "__main__":
    main()