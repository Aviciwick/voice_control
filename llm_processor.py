import json
import re
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL, TEMPERATURE, PROMPT_TEMPLATE

# 创建 OpenAI 客户端
client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

# 语音识别文本修正字典
SPEECH_CORRECTIONS = {
    # 常见的语音识别错误
    # 捡起相关
    "剪輯": "捡起",
    "剪起": "捡起",
    "剪机": "捡起",
    "剪几": "捡起",
    "捡鸡": "捡起",
    "今起": "捡起", 
    "尖起": "捡起",
    "捡其": "捡起",
    "钱起": "捡起",
    "前起": "捡起",
    "见起": "捡起",
    
    #瓶子相关
    "水平": "水瓶",
    
    # 羽毛球相关
    "與模球": "羽毛球",
    "模球": "羽毛球",
    "毛求": "羽毛球",
    "与毛球": "羽毛球",
    "余毛球": "羽毛球",
    "鸟球": "羽毛球",
    "毛秋": "羽毛球",
    "有毛球": "羽毛球",
    
    # 坐下相关
    "掰年": "拜年",
    "白年": "拜年",
    "白念": "拜年",
    "做下": "坐下",
    "坐吓": "坐下",
    "左下": "坐下",
    "走下": "坐下",
    "做些": "坐下",
    
    # 去捡相关
    "续剪": "去捡",
    "续捡": "去捡",
    "需捡": "去捡",
    "去尖": "去捡",
    "去见": "去捡",
    "去检": "去捡",
    "出剪": "去捡",
    "出捡": "去捡",
    
    # 停止相关
    "停一停": "停下",
    "停一下": "停下",
    "停住": "停下",
    "停止": "停下",
    "别动": "停下",
    "不要动": "停下",
    
    # 站立相关
    "转立": "站立",
    "占立": "站立",
    "站力": "站立",
    "站里": "站立",
    "站起来": "站立",
    "站起": "站立",
    
    # 跳舞相关
    "跳支舞": "跳舞",
    "跳个舞": "跳舞",
    "跳一段": "跳舞",
    "跳一跳": "跳舞",
    "舞蹈": "跳舞",
    
    # 动作映射到指令
    "握住": "grab",
    "拿住": "grab",
    "拿起": "grab",
    "抓住": "grab",
    "松开": "release",
    "放开": "release",
    "释放": "release",
    "丢掉": "release",
    "站好": "StandUp",
    "站稳": "StandUp",
    "趴下": "StandDown",
    "躺下": "StandDown",
    "坐好": "Sit",
    "坐稳": "Sit",
    "打招呼": "Hello",
    "问好": "Hello",
    "伸懒腰": "Stretch",
    "伸个懒腰": "Stretch",
    "走步": "ContinuousGait",
    "踏步": "ContinuousGait",
    "原地踏步": "ContinuousGait",
    "打滚": "Wallow",
    "滚一滚": "Wallow",
    "翻滚": "Wallow",
    "摆造型": "Pose",
    "摆姿势": "Pose",
    "摆个姿势": "Pose",
    "拜年": "Scrape",
    "作揖": "Scrape",
    "跳舞": "Dance",
}

def correct_speech_recognition(text):
    """修正常见的语音识别错误"""
    corrected_text = text
    
    # 应用所有修正规则
    for error, correction in SPEECH_CORRECTIONS.items():
        corrected_text = corrected_text.replace(error, correction)
    
    # 如果文本被修改，打印出来
    if corrected_text != text:
        print(f"语音识别修正: '{text}' -> '{corrected_text}'")
        
    return corrected_text

def clean_json_string(json_text):
    """清理并修复 JSON 字符串中的常见格式问题"""
    if not json_text:
        return "{}"
        
    # 1. 移除所有前导和尾随的空白字符
    json_text = json_text.strip()
    
    # 2. 如果文本不是以 { 开头，尝试找到第一个 {
    if not json_text.startswith("{"):
        match = re.search(r'\{', json_text)
        if match:
            json_text = json_text[match.start():]
    
    # 3. 如果文本不是以 } 结尾，尝试找到最后一个 }
    if not json_text.endswith("}"):
        match = re.search(r'\}', json_text)
        if match:
            json_text = json_text[:match.end()]
    
    # 4. 处理可能存在的多个JSON对象（只保留第一个完整的JSON对象）
    try:
        # 尝试找到第一个有效的JSON对象
        brace_count = 0
        end_pos = 0
        
        for i, char in enumerate(json_text):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i + 1
                    break
        
        if end_pos > 0:
            json_text = json_text[:end_pos]
    except:
        # 如果上述方法失败，至少确保移除尾部的额外数据
        pass
    
    # 5. 移除可能在JSON中间的无效换行符和特殊字符
    try:
        # 先尝试直接解析，如果失败再进行进一步清理
        json.loads(json_text)
    except:
        # 使用更严格的正则表达式来提取有效的JSON
        pattern = r'(\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\})'
        matches = re.findall(pattern, json_text)
        if matches:
            # 取最长的匹配作为有效JSON
            json_text = max(matches, key=len)
    
    return json_text

def get_structured_data(transcript: str, return_raw_response: bool = False) -> dict:
    """
    将语音转写文本转换为结构化数据
    
    参数:
        transcript: 语音转写文本
        return_raw_response: 是否返回原始 API 响应
        
    返回:
        如果 return_raw_response=False，返回结构化数据字典
        如果 return_raw_response=True，返回 (结构化数据字典, 原始 API 响应) 元组
    """
    if not transcript or transcript.strip() == "":
        print("警告: 转写文本为空")
        result = {"error": "转写文本为空"}
        return (result, "未调用 API") if return_raw_response else result
    
    # 修正常见的语音识别错误
    corrected_transcript = correct_speech_recognition(transcript)
    
    try:
        # 准备 prompt，增加要求使用英文回复的指令
        base_prompt = PROMPT_TEMPLATE.format(transcript=corrected_transcript)
        english_instruction = "\n\nIMPORTANT: You must respond in English only. All JSON field names and values must be in English."
        prompt = base_prompt + english_instruction
        
        print(f"发送到模型的提示词长度: {len(prompt)} 字符")
        
        # 调用 API，增加强制英文的设置
        print(f"正在调用 API...")
        response = client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[
                {"role": "system", "content": "You must respond in English only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # 获取 API 返回的完整内容
        json_text = response.choices[0].message.content
        
        # 构建原始响应
        raw_response = f"""=== API 响应内容 ===
{json_text}
"""
        
        print(f"收到 API 响应（长度: {len(json_text)} 字符）")
        
        try:
            # 尝试直接解析 JSON
            parsed_json = json.loads(json_text)
            return (parsed_json, raw_response) if return_raw_response else parsed_json
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试清理后再解析
            cleaned_json = clean_json_string(json_text)
            parsed_json = json.loads(cleaned_json)
            return (parsed_json, raw_response) if return_raw_response else parsed_json
            
    except Exception as e:
        error_msg = str(e)
        print(f"API 调用或处理过程中出错: {error_msg}")
        
        result = {"error": f"处理错误: {error_msg}", "raw_transcript": corrected_transcript}
        return (result, f"错误: {error_msg}") if return_raw_response else result
