import os
import subprocess
import sys
import re

# 检查 ffmpeg 是否已安装
def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def load_vocabulary(vocab_file="vocabulary.txt"):
    """
    加载词汇表文件并返回替换映射字典
    
    参数:
        vocab_file: 词汇表文件路径
        
    返回:
        包含错误词->正确词映射的字典
    """
    vocab_dict = {}
    if os.path.exists(vocab_file):
        try:
            with open(vocab_file, 'r', encoding='utf-8') as f:
                vocab_lines = f.readlines()
            
            for line in vocab_lines:
                line = line.strip()
                if not line or line.startswith('#'):  # 跳过空行和注释
                    continue
                    
                if '=>' in line:
                    wrong, correct = line.split('=>', 1)
                    vocab_dict[wrong.strip()] = correct.strip()
            
            print(f"已加载 {len(vocab_dict)} 个词汇映射项")
        except Exception as e:
            print(f"加载词汇表失败: {str(e)}")
    
    return vocab_dict

def apply_vocabulary_correction(text, vocab_dict):
    """
    应用词汇表修正到文本
    
    参数:
        text: 要修正的文本
        vocab_dict: 词汇映射字典
        
    返回:
        修正后的文本
    """
    if not vocab_dict:
        return text
        
    corrected_text = text
    corrections_applied = 0
    
    # 按照词长度降序排序，避免短词替换干扰长词替换
    sorted_words = sorted(vocab_dict.keys(), key=len, reverse=True)
    
    # 应用词汇表替换
    for wrong in sorted_words:
        if wrong in corrected_text:
            before = corrected_text
            corrected_text = corrected_text.replace(wrong, vocab_dict[wrong])
            if before != corrected_text:
                corrections_applied += 1
                print(f"词汇替换: '{wrong}' -> '{vocab_dict[wrong]}'")
    
    if corrections_applied > 0:
        print(f"总计应用了 {corrections_applied} 处词汇修正")
        print(f"修正前: {text}")
        print(f"修正后: {corrected_text}")
    
    return corrected_text

def transcribe_audio(audio_path: str, model_size: str = "medium") -> str:
    """
    使用 Whisper 模型转写音频文件
    
    参数:
        audio_path: 音频文件路径
        model_size: Whisper 模型大小，可选值: "tiny", "base", "small", "medium", "large"
                    模型越大准确率越高，但需要更多内存和计算资源
    
    返回:
        转写的文本
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"音频文件未找到: {audio_path}")
    
    if not check_ffmpeg():
        print("错误: 未检测到 ffmpeg，这是 Whisper 模型处理音频所必需的。")
        print("请安装 ffmpeg: https://ffmpeg.org/download.html")
        print("Windows 用户可以通过 chocolatey 安装: choco install ffmpeg")
        print("或下载: https://www.gyan.dev/ffmpeg/builds/ 并添加到系统 PATH")
        sys.exit(1)
    
    try:
        import whisper
        print(f"加载 Whisper {model_size} 模型中...")
        model = whisper.load_model(model_size)
        print("正在转写音频...")
        
        # 为中文语音添加特定参数
        transcribe_options = {
            'language': 'zh',           # 指定语言为中文
            'task': 'transcribe',       # 指定任务类型
            'fp16': False,              # 在CPU上禁用FP16以避免警告
            'beam_size': 5,             # 增加波束搜索大小以提高准确性
            'best_of': 5                # 返回最佳结果
        }
        
        # 加载机器狗相关的指令集提示词
        initial_prompt = """
        这是与机器狗相关的语音指令: 捡起羽毛球, 拿起红球, 坐下, 站立, 趴下, 
        停下, 打滚, 打招呼, 跳舞, 前空翻, 拜年, 伸懒腰, 踏步, 摆姿势,
        抓取, 释放, 停止移动, 恢复站立, 设置速度, 跳一支舞, 捡起来, 去捡
        """
        
        if initial_prompt:
            transcribe_options['initial_prompt'] = initial_prompt
        
        # 执行音频转写
        result = model.transcribe(audio_path, **transcribe_options)
        transcript = result["text"].strip()
        print(f"原始转写结果: {transcript}")
        
        # 加载并应用词汇表修正
        vocab_dict = load_vocabulary()
        corrected_transcript = apply_vocabulary_correction(transcript, vocab_dict)
        
        return corrected_transcript
        
    except ImportError:
        print("错误: 无法导入 whisper 库。")
        print("请尝试重新安装 whisper: pip install -U openai-whisper")
        sys.exit(1)
    except Exception as e:
        print(f"转写时出错: {str(e)}")
        sys.exit(1)
