# 语音控制机器狗系统

## 项目简介
本系统将语音指令通过 Whisper 模型转写为文本，并调用大语言模型提取为结构化 JSON 指令，用于控制机器狗。系统支持多种动作指令解析，如抓取物体、坐下、站立等，使您可以方便地通过语音来控制机器狗。

## 功能特点
- 支持多种音频格式（WAV、MP3、M4A、FLAC等）
- 自动检测并使用本地音频文件
- 可通过命令行指定任意音频文件
- 结果自动保存为JSON文件，方便集成到机器狗控制系统
- 实时显示处理流程和结果
- **可选择不同大小的 Whisper 模型以平衡准确性和速度**
- **支持保存语音转写文本**
- **内置语音识别错误修正机制，提高指令识别准确率**

## 机器狗支持的动作
系统当前支持以下机器狗动作：

| 动作名 | 功能概述 |
|--------|---------|
| grab | 抓取物体 |
| release | 释放物体 |
| StopMove | 停止移动 |
| StandUp | 站立 |
| StandDown | 趴下 |
| RecoveryStand | 恢复站立姿势 |
| Sit | 坐下 |
| SpeedLevel | 设置速度档位 |
| Hello | 打招呼 |
| Stretch | 伸懒腰 |
| ContinuousGait | 踏步 |
| Wallow | 打滚 |
| Pose | 摆姿势 |
| Scrape | 拜年 |
| Dance | 跳舞 |

## 安装依赖

### 1. 安装 Python 依赖
```bash
pip install openai-whisper openai
```

### 2. 安装 FFmpeg（必需）
Whisper 模型需要 FFmpeg 处理音频文件：

**Windows:**
- 方法1：使用 Chocolatey 安装：`choco install ffmpeg`
- 方法2：从 [ffmpeg.org](https://ffmpeg.org/download.html) 或 [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) 下载，解压后添加到系统 PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update && sudo apt install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg  # CentOS/RHEL
```

## API 配置
在 `config.py` 中设置您的 OpenAI API 密钥和提示模板。默认使用 GPT-3.5-Turbo 模型，您也可以修改为其他模型。

## 使用说明

### 基本用法
```bash
python main.py
```
系统将自动检测当前目录下的第一个音频文件并处理。

### 指定音频文件
```bash
python main.py 路径/到/您的/音频文件.mp3
```

### 提高语音识别准确性
使用更大的 Whisper 模型可以显著提高语音识别准确性：
```bash
python main.py --model medium  # 默认选项，平衡准确性和速度
python main.py --model large   # 最高准确性，但需要更多内存和计算资源
```

### 保存语音转写文本
```bash
python main.py --save-transcript
```

### 完整命令行选项
```bash
python main.py [音频文件] [--model MODEL] [--save-transcript]

选项:
  --model, -m {tiny,base,small,medium,large}
                        Whisper 模型大小 (默认: medium)
  --save-transcript, -s
                        保存语音转写文本
```

## 语音指令示例

以下是一些您可以尝试的语音指令示例：

1. "抓取那个红球" → `{"action": "grab", "object": "red ball"}`
2. "请坐下" → `{"action": "Sit"}`
3. "停止移动" → `{"action": "StopMove"}`
4. "跳个舞" → `{"action": "Dance"}`
5. "捡起羽毛球" → `{"action": "grab", "object": "badminton"}`

## 提高语音识别准确性的方法

1. **使用更大的模型**：
   - tiny → base → small → medium → large（准确性依次提高）
   - 较大的模型需要更多内存和计算资源

2. **改善录音质量**：
   - 使用高质量麦克风
   - 减少背景噪音
   - 保持适当的讲话距离和音量

3. **优化音频文件**：
   - 使用音频编辑软件去除噪音
   - 确保采样率至少为 16kHz
   - 避免音频过度压缩

4. **调整语音节奏**：
   - 语速适中，清晰发音
   - 避免口语化表达和省略

5. **预处理专业术语**：
   - 在 `llm_processor.py` 中添加常见术语的映射
   - 编辑 `vocabulary.txt` 添加自定义词汇

## 处理流程
1. 加载并检查音频文件
2. 使用 Whisper 模型转写音频为文本
3. 对转写文本进行错误修正
4. 调用 OpenAI API 将文本转换为结构化 JSON 指令
5. 显示并保存结果

## 输出结果
- 终端显示转写文本和结构化 JSON 数据
- 自动将结果保存为与音频文件同名的 JSON 文件（如 audio.mp3 → audio_结果.json）
- 可选保存原始转写文本（如 audio.mp3 → audio_转写.txt）
- API 原始响应保存为文本文件（如 audio.mp3 → audio_原始响应.txt）

## 自定义和扩展

### 添加新的语音识别修正规则
在 `llm_processor.py` 文件中，您可以编辑 `SPEECH_CORRECTIONS` 字典来添加常见的语音识别错误修正：

```python
SPEECH_CORRECTIONS = {
    # 添加您的自定义修正项
    "错误文本": "正确文本",
    "鸡蛋": "捡起",
    # 更多修正...
}
```

### 修改提示词模板
在 `config.py` 文件中，您可以编辑 `PROMPT_TEMPLATE` 来自定义提示词模板，以适应不同的机器狗型号或指令集。

## 常见问题解决

### 1. Whisper 模型无法加载
确保正确安装了 openai-whisper 而非其他 whisper 库：
```bash
pip uninstall whisper
pip install openai-whisper
```

### 2. FFmpeg 相关错误
错误信息：`FileNotFoundError: [WinError 2] 系统找不到指定的文件`
解决方法：确保已安装 FFmpeg 并添加到系统 PATH

### 3. 转写结果差或错误
- 尝试使用更大的模型：`python main.py --model large`
- 使用更高质量的音频文件
- 为特定命令添加自定义映射规则（在 `llm_processor.py` 中）

### 4. 内存不足错误
如果使用 large 模型时出现内存不足错误，请降级到 medium 或 small 模型：
```bash
python main.py --model medium
```

### 5. OpenAI API 错误
- 检查 API 密钥是否正确
- 确认网络连接
- 检查 API 额度是否充足

### 6. 指令未被正确解析
- 检查 `config.py` 中的提示词模板是否正确
- 尝试修改语音表达方式，使用更直接、明确的指令
- 在 `llm_processor.py` 中添加特定指令的错误修正规则

## 项目结构
- `main.py`: 主程序入口
- `speech_recognition.py`: 语音识别模块
- `llm_processor.py`: 大语言模型处理和指令解析模块
- `config.py`: 配置文件，含API密钥和提示词模板
- `vocabulary.txt`: 自定义识别词汇表
- `Audio/`: 音频文件目录
- `results/`: 结果输出目录

## 更新日志

### 2023年10月更新
- **增强词汇表处理**：重写了语音识别词汇表处理逻辑，使其更加健壮和高效
- **扩展错误修正**：显著扩展了`SPEECH_CORRECTIONS`字典，增加了数十个常见语音识别错误的修正规则
- **优化用户界面**：改进了命令行输出，添加了更友好的进度指示和错误提示
- **自动化文件处理**：增强了自动查找音频文件的功能，优先从Audio目录中查找
- **增强错误处理**：完善了各种异常情况的处理逻辑，提高了系统稳定性
- **改进文档**：更新了README，提供了更详细的使用说明和故障排除方法
- **性能优化**：改进了词汇表应用逻辑，按照词长度排序以避免短词替换干扰长词替换
