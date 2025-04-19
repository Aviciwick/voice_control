import json
import os
import sys
import argparse
import time
from pathlib import Path
from typing import Optional, Tuple
from speech_recognition import transcribe_audio
from llm_processor import get_structured_data

def main(audio_path: str, model_size: str = "medium", save_transcript: bool = False) -> Tuple[Optional[dict], Optional[str]]:
    """
    处理音频文件并返回结构化数据
    
    参数:
        audio_path: 音频文件路径
        model_size: Whisper 模型大小，默认为 "medium"
        save_transcript: 是否保存转写文本，默认为 False
        
    返回:
        (结构化数据字典, 转写文本) 元组，如果处理失败则返回 (None, None)
    """
    try:
        start_time = time.time()
        
        print("="*50)
        print(f"🎤 处理音频文件: {audio_path}")
        print(f"🔍 使用 Whisper {model_size} 模型")
        print("="*50)
        
        # 步骤 1: 转写音频
        print("\n📝 步骤 1: 转写音频为文本...")
        transcript = transcribe_audio(audio_path, model_size)
        print(f"✅ 转写完成! 用时: {time.time() - start_time:.2f} 秒")
        print(f"\n📃 转写文本:\n{transcript}\n")
        
        # 如果需要，保存转写文本
        if save_transcript:
            audio_path_obj = Path(audio_path)
            transcript_path = str(audio_path_obj.with_suffix('')) + "_转写.txt"
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            print(f"📋 转写文本已保存至: {transcript_path}")
        
        # 步骤 2: 使用 OpenAI API 将文本转换为结构化数据
        print("\n🧠 步骤 2: 将文本转换为结构化数据...")
        structured_data, raw_response = get_structured_data(transcript, return_raw_response=True)
        print(f"✅ 处理完成! 总用时: {time.time() - start_time:.2f} 秒\n")
        
        # 显示结构化数据
        print("📊 结构化数据:")
        formatted_json = json.dumps(structured_data, ensure_ascii=False, indent=2)
        print(formatted_json)
        
        # 保存结果
        audio_path_obj = Path(audio_path)
        result_path = str(audio_path_obj.with_suffix('')) + "_结果.json"
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(formatted_json)
        print(f"\n💾 结果已保存至: {result_path}")
        
        # 保存原始 API 响应
        raw_response_path = str(audio_path_obj.with_suffix('')) + "_原始响应.txt"
        with open(raw_response_path, "w", encoding="utf-8") as f:
            f.write(raw_response)
        print(f"📝 原始 API 响应已保存至: {raw_response_path}")
        
        # 返回结果
        return structured_data, transcript
        
    except FileNotFoundError as e:
        print(f"❌ 错误: 文件未找到 - {e}")
        print(f"请确认音频文件路径是否正确: {audio_path}")
        return None, None
        
    except ImportError as e:
        print(f"❌ 错误: 导入模块失败 - {e}")
        print("请确保已安装所需依赖，运行: pip install openai-whisper openai")
        return None, None
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断，程序已停止")
        return None, None
        
    except Exception as e:
        print(f"❌ 错误: {type(e).__name__} - {e}")
        print("如需帮助，请查阅 README.md 文件中的故障排除部分")
        return None, None

def find_audio_file() -> Optional[str]:
    """查找当前目录中的第一个音频文件"""
    print("正在查找音频文件...")
    
    # 支持的音频格式
    audio_extensions = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"]
    
    # 首先在 Audio 目录中查找（如果存在）
    audio_dir = Path("Audio")
    if audio_dir.exists() and audio_dir.is_dir():
        print(f"正在 Audio/ 目录中搜索音频文件...")
        for ext in audio_extensions:
            for file in audio_dir.glob(f"*{ext}"):
                print(f"找到音频文件: {file}")
                return str(file)
    
    # 如果在 Audio 目录中没有找到，在当前目录中查找
    print("在当前目录中搜索音频文件...")
    for ext in audio_extensions:
        for file in Path(".").glob(f"*{ext}"):
            print(f"找到音频文件: {file}")
            return str(file)
    
    print("❌ 未找到音频文件，请提供音频文件路径")
    return None

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="语音转结构化数据工具")
    parser.add_argument("audio_file", nargs="?", help="音频文件路径")
    parser.add_argument("--model", "-m", choices=["tiny", "base", "small", "medium", "large"], 
                        default="medium", help="Whisper 模型大小 (默认: medium)")
    parser.add_argument("--save-transcript", "-s", action="store_true", 
                        help="保存语音转写文本")
    
    return parser.parse_args()

if __name__ == "__main__":
    # 解析命令行参数
    args = parse_arguments()
    
    # 如果没有提供音频文件，尝试自动查找
    audio_path = args.audio_file
    if not audio_path:
        audio_path = find_audio_file()
        if not audio_path:
            print("请通过命令行参数指定音频文件路径，例如:")
            print("python main.py path/to/audio.mp3")
            sys.exit(1)
    
    # 确保保存结果的目录存在
    results_dir = Path("results")
    if not results_dir.exists():
        results_dir.mkdir()
        print(f"已创建 {results_dir} 目录用于保存结果")
    
    # 处理音频文件
    structured_data, transcript = main(audio_path, args.model, args.save_transcript)
    
    # 根据处理结果显示适当的消息
    if structured_data is not None:
        if "error" in structured_data:
            print(f"\n⚠️ 警告: 处理过程中出现问题 - {structured_data['error']}")
            sys.exit(1)
        else:
            print("\n✨ 处理成功完成!")
            
            # 提取动作和对象（如果存在）
            action = structured_data.get("action", "未识别")
            obj = structured_data.get("object", "")
            
            if action and action != "未识别":
                print(f"\n🤖 机器狗指令: {action}" + (f" ({obj})" if obj else ""))
            sys.exit(0)
    else:
        print("\n❌ 处理失败")
        sys.exit(1)
