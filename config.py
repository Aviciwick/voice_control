OPENAI_API_KEY = "634b7100-a736-4e86-b9a1-56b2cbb546e9"
OPENAI_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL = "deepseek-v3-250324"
TEMPERATURE = 0.1  # 较低的温度值使输出更加确定性

PROMPT_TEMPLATE = """
你现在需要给一只机器狗发送指令，机器狗仅支持以下动作：

动作名	功能概述 参数
grab	抓取 object
release	释放 无
StopMove	停下 无
StandUp	站立 无
StandDown	趴下 无
RecoveryStand	恢复站立 无
Sit	坐下 无
SpeedLevel	设置速度档位 level：速度档位枚举值，取值  -1  为慢速，0  为正常，1  为快速。
Hello	打招呼
Stretch	伸懒腰
ContinuousGait	踏步 flag：设置 true  为开启，false  为关闭。
Wallow	打滚 flag：设置 true  为摆姿式，false  为恢复。
Pose	摆姿势
Scrape	拜年
Dance	跳舞

只返回JSON格式数据，不要有任何其他文字或解释。json中仅需两种内容：action，object。
因为语音转文字模型不是很理想，你需要思考一些中文同音字，请充分分析，
请将以下语音内容提取为结构化信息，并返回JSON格式，所有内容翻译成英文输出：
"{transcript}"
"""
