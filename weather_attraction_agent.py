AGENT_SYSTEM_PROMPT = """
你是一个带记忆、自动备选、反思能力的智能旅行助手。遵循Thought-Action循环解决用户需求。

# 全局记忆信息（思考时必须优先参考）
长期用户偏好: {{LONG_MEM_PREFER}}
本轮推荐历史与用户反馈: {{SHORT_MEM_RECORD}}

# 核心规则
1. 记忆功能：用户提到偏好（喜欢历史景点/预算/讨厌爬山等），需要主动更新长期记忆；每次推荐必须结合用户偏好。
2. 门票售罄处理：调用get_attraction后若Observation提到景点售罄，下一步必须Action调用get_alternative_attraction查询同类型备选。
3. 反思机制：如果短期记忆中用户连续拒绝3个推荐，思考时先反思被拒原因，调整景点类型、预算、距离约束再重新推荐，并清空拒绝记录。

# 可用工具:
- `get_weather(city: str)`: 查询指定城市的实时天气。
- `get_attraction(city: str, weather: str, prefer_type: str)`: 根据城市、天气、用户偏好搜索景点，返回门票售卖状态。
- `get_alternative_attraction(city: str, weather: str, target_type: str, exclude_spots: str)`: 景点售罄时，查询同类型备选景点，排除已推荐过的景点。

# 输出格式要求:
每次回复严格一对Thought+Action
Thought: [思考，融合用户偏好、售罄判断、连续拒绝反思逻辑]
Action: 二选一
1. 工具调用：function_name(arg1="xx",arg2="xx")
2. 结束任务：Finish[最终完整回答，包含偏好、景点、备选方案]

约束：单次只输出一组Thought-Action，Action单独一行；信息足够时用Finish终止循环。
请开始吧！
"""

class LongTermMemory:
    """长期记忆：持久保存用户固定偏好（景点偏好、预算、出行方式、厌恶类型）"""
    def __init__(self):
        self.storage = {}

    def update(self, pref_dict: dict):
        self.storage.update(pref_dict)

    def get_all(self):
        return self.storage.copy()

class ShortTermSessionMemory:
    """短期会话记忆：保存本轮推荐记录、用户反馈（accept/reject）"""
    def __init__(self):
        self.recommend_records = []  # [{"spot":xxx, "feedback":"accept"/"reject"}]

    def add_record(self, spot_name: str, feedback: str):
        self.recommend_records.append({"spot": spot_name, "feedback": feedback})

    def get_continuous_reject_count(self) -> int:
        """统计末尾连续拒绝的数量"""
        cnt = 0
        for item in reversed(self.recommend_records):
            if item["feedback"] == "reject":
                cnt += 1
            else:
                break
        return cnt

    def clear_reject_records(self):
        """触发反思后清空连续拒绝计数"""
        self.recommend_records = []

# 全局初始化记忆对象
long_memory = LongTermMemory()
short_memory = ShortTermSessionMemory()


import requests

def get_weather(city: str) -> str:
    """
    通过调用 wttr.in API 查询真实的天气信息。
    """
    # API端点，我们请求JSON格式的数据
    url = f"https://wttr.in/{city}?format=j1"
    
    try:
        # 发起网络请求
        response = requests.get(url)
        # 检查响应状态码是否为200 (成功)
        response.raise_for_status() 
        # 解析返回的JSON数据
        data = response.json()
        
        # 提取当前天气状况
        current_condition = data['current_condition'][0]
        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']
        
        # 格式化成自然语言返回
        return f"{city}当前天气:{weather_desc}，气温{temp_c}摄氏度"
        
    except requests.exceptions.RequestException as e:
        # 处理网络错误
        return f"错误:查询天气时遇到网络问题 - {e}"
    except (KeyError, IndexError) as e:
        # 处理数据解析错误
        return f"错误:解析天气数据失败，可能是城市名称无效 - {e}"


import os
from tavily import TavilyClient

'''def get_attraction(city: str, weather: str) -> str:
    """
    根据城市和天气，使用Tavily Search API搜索并返回优化后的景点推荐。
    """
    # 1. 从环境变量中读取API密钥
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "错误:未配置TAVILY_API_KEY环境变量。"

    # 2. 初始化Tavily客户端
    tavily = TavilyClient(api_key=api_key)
    
    # 3. 构造一个精确的查询
    query = f"'{city}' 在'{weather}'天气下最值得去的旅游景点推荐及理由"
    
    try:
        # 4. 调用API，include_answer=True会返回一个综合性的回答
        response = tavily.search(query=query, search_depth="basic", include_answer=True)
        
        # 5. Tavily返回的结果已经非常干净，可以直接使用
        # response['answer'] 是一个基于所有搜索结果的总结性回答
        if response.get("answer"):
            return response["answer"]
        
        # 如果没有综合性回答，则格式化原始结果
        formatted_results = []
        for result in response.get("results", []):
            formatted_results.append(f"- {result['title']}: {result['content']}")
        
        if not formatted_results:
             return "抱歉，没有找到相关的旅游景点推荐。"

        return "根据搜索，为您找到以下信息:\n" + "\n".join(formatted_results)

    except Exception as e:
        return f"错误:执行Tavily搜索时出现问题 - {e}"'''


def get_attraction(city: str, weather: str, prefer_type: str = "") -> str:
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "错误:未配置TAVILY_API_KEY环境变量。"
    tavily = TavilyClient(api_key=api_key)
    query = f"'{city}' {weather}天气适合{prefer_type}景点，标注各景点门票是否售罄"
    try:
        response = tavily.search(query=query, search_depth="basic", include_answer=True)
        if response.get("answer"):
            return response["answer"]
        formatted = []
        for res in response.get("results", []):
            formatted.append(f"- {res['title']}: {res['content']}")
        return "景点信息:\n" + "\n".join(formatted) if formatted else "无景点数据"
    except Exception as e:
        return f"工具异常:{e}"

# 新增工具：查询同类型备选景点
def get_alternative_attraction(city: str, weather: str, target_type: str, exclude_spots: str):
    """当原景点售罄，调用此工具获取替代景点"""
    api_key = os.environ.get("TAVILY_API_KEY")
    tavily = TavilyClient(api_key=api_key)
    query = f"{city} {weather}天气，{target_type}类型备选景点，排除{exclude_spots}"
    res = tavily.search(query=query, include_answer=True)
    return res.get("answer", "无备选景点推荐")

# 更新工具字典
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
    "get_alternative_attraction": get_alternative_attraction,
}



from openai import OpenAI

class OpenAICompatibleClient:
    """
    一个用于调用任何兼容OpenAI接口的LLM服务的客户端。
    """
    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str, system_prompt: str) -> str:
        """调用LLM API来生成回应。"""
        print("正在调用大语言模型...")
        try:
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            answer = response.choices[0].message.content
            print("大语言模型响应成功。")
            return answer
        except Exception as e:
            print(f"调用LLM API时发生错误: {e}")
            return "错误:调用语言模型服务时出错。"

'''
apikey:sk-qqxNFFIQO1jGCdRv2781C7348cC44337B8083740E188B966

baseurl:https://aihubmix.com

id:coding-glm-5.2-free
'''

import re

# --- 1. 配置LLM客户端 ---
# 请根据您使用的服务，将这里替换成对应的凭证和地址
API_KEY = "sk-7ee63d1fc192437793bd47d8d5c833e2"
BASE_URL = "https://api.deepseek.com"
MODEL_ID = "deepseek-v4-flash"
TAVILY_API_KEY="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"
os.environ['TAVILY_API_KEY'] = "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"

llm = OpenAICompatibleClient(
    model=MODEL_ID,
    api_key=API_KEY,
    base_url=BASE_URL
)

# --- 2. 初始化 ---
user_prompt = "你好，请帮我查询一下今天北京的天气，我偏爱历史古迹，预算单日200元，然后根据天气推荐合适景点，如果没票给我备选；如果推荐不合我心意我会拒绝"
prompt_history = [f"用户请求: {user_prompt}"]


print(f"用户输入: {user_prompt}\n" + "="*40)

# --- 3. 运行主循环 ---

max_loop = 8
for i in range(max_loop):
    print(f"--- 循环 {i+1} ---\n")
    full_prompt = "\n".join(prompt_history)
    
    # 1. 填充记忆到系统提示词
    long_pref = long_memory.get_all()
    short_rec = short_memory.recommend_records
    inject_sys = AGENT_SYSTEM_PROMPT.replace("{{LONG_MEM_PREFER}}", str(long_pref))
    inject_sys = inject_sys.replace("{{SHORT_MEM_RECORD}}", str(short_rec))

    # 2. 调用LLM生成Thought-Action
    llm_output = llm.generate(full_prompt, system_prompt=inject_sys)
    match = re.search(r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)', llm_output, re.DOTALL)
    if match:
        llm_output = match.group(1).strip()
    print(f"模型输出:\n{llm_output}\n")
    prompt_history.append(llm_output)

    # 3. 解析Action
    action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
    if not action_match:
        obs = "错误：输出格式非法，严格按照Thought+Action格式返回"
        obs_str = f"Observation: {obs}"
        print(f"{obs_str}\n" + "="*40)
        prompt_history.append(obs_str)
        continue
    action_str = action_match.group(1).strip()

    # 任务结束分支
    if action_str.startswith("Finish"):
        final_ans = re.match(r"Finish\[(.*)\]", action_str).group(1)
        print(f"任务完成，最终答案:\n{final_ans}")
        break

    # 解析工具名与参数
    tool_name = re.search(r"(\w+)\(", action_str).group(1)
    args_str = re.search(r"\((.*)\)", action_str).group(1)
    kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

    # 执行工具
    if tool_name in available_tools:
        observation = available_tools[tool_name](**kwargs)
    else:
        observation = f"错误：不存在工具 {tool_name}"
    obs_str = f"Observation: {observation}"
    print(f"{obs_str}\n" + "="*40)
    prompt_history.append(obs_str)

    # ===================== 新增：用户交互反馈逻辑 =====================
    # 模拟用户对本次推荐景点给出反馈（accept/reject/更新偏好）
    if "get_attraction" in action_str or "get_alternative_attraction" in action_str:
        user_feedback = input("请输入反馈 accept / reject / update偏好: ")
        # 更新长期记忆
        if user_feedback == "update偏好":
            new_pref_text = input("输入你的新偏好: ")
            # LLM解析偏好结构化存入长期记忆
            parse_prompt = f"把用户偏好转为字典，输出json：{new_pref_text}"
            pref_json = llm.generate(parse_prompt, system_prompt="只输出json")
            import json
            pref_dict = json.loads(pref_json)
            long_memory.update(pref_dict)
            continue
        # 提取当前推荐景点存入短期记忆
        spot_name = kwargs.get("city", "未知景点") + "历史古迹"
        short_memory.add_record(spot_name, user_feedback)
        # 判断是否连续3次拒绝，下一轮自动反思
        reject_cnt = short_memory.get_continuous_reject_count()
        if reject_cnt >= 3:
            print(f"检测到连续{reject_cnt}次拒绝，下一轮将自动反思调整推荐策略！")
    #输出：
    '''
    用户输入: 你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。
    ========================================
    --- 循环 1 ---

    正在调用大语言模型...
    大语言模型响应成功。
    模型输出:
    Thought: 用户请求查询北京今天的天气，并根据天气推荐景点。我需要先调用get_weather工具获取北京的实时天气信息。

    Action: get_weather(city="北京")

    解析到的 Action: get_weather(city="北京")

    Observation: 北京当前天气:Sunny，气温31摄氏度
    ========================================
    --- 循环 2 ---

    正在调用大语言模型...
    大语言模型响应成功。
    模型输出:
    Thought: 我已经获取到了北京的天气是晴朗，气温31摄氏度。现在我需要根据城市和天气信息调用get_attraction工具来推荐合适的旅游景点。

    Action: get_attraction(city="北京", weather="Sunny")

    解析到的 Action: get_attraction(city="北京", weather="Sunny")

    Observation: In sunny Beijing, visit the Forbidden City, Temple of Heaven, and Olympic Park for pleasant weather and iconic landmarks.
    ========================================
    --- 循环 3 ---

    正在调用大语言模型...
    大语言模型响应成功。
    模型输出:
    Thought: 我已经成功获取了北京的天气情况（晴朗，31摄氏度）以及根据天气推荐的景点（故宫、天坛、奥林匹克公园）。现在可以整合这些信息给用户一个完整的回复。

    Action: Finish[根据查询结果，北京今天天气晴朗，气温31摄氏度。非常适合出游！根据这个天气情况，为您推荐以下景点：故宫、天坛和奥林匹克公园。这些地方在晴朗的天气下景色宜人，非常适合游览。]

    解析到的 Action: Finish[根据查询结果，北京今天天气晴朗，气温31摄氏度。非常适合出游！根据这个天气情况，为您推荐以下景点：故宫、天坛和奥林匹克公园。这些地方在晴朗的天气下景色宜人，非常适合游览。]

    任务完成，最终答案: 根据查询结果，北京今天天气晴朗，气温31摄氏度。非常适合出游！根据这个天气情况，为您推荐以下景点：故宫、天坛和奥林匹克公园。这些地方在晴朗的天气下景色宜人，非常适合游览。
    '''
    
#输出2:
'''
用户输入: 你好，请帮我查询一下今天北京的天气，我偏爱历史古迹，预算单日200元，然后根据天气推荐合适景点，如果没票给我备选；如果推荐不合我心意我会拒绝
========================================
--- 循环 1 ---

正在调用大语言模型...
大语言模型响应成功。
模型输出:
Thought: 用户要求查询北京今天天气，偏好历史古迹，预算200元。我需要先获取天气信息，再根据天气推荐景点。
Action: get_weather(city="北京")

Observation: 北京当前天气:Partly cloudy，气温24摄氏度
========================================
--- 循环 2 ---

正在调用大语言模型...
大语言模型响应成功。
模型输出:
Thought: 北京天气为Partly cloudy，适合户外活动。用户偏爱历史古迹且预算200元，现在调用景点查询工具按天气和历史类型推荐景点。
Action: get_attraction(city="北京", weather="Partly cloudy", prefer_type="历史古迹")

Observation: Many Beijing historical sites have sold out, especially during holidays. Popular spots like the Forbidden City and the Great Wall are often fully booked. Check official sites or trusted platforms for availability.
========================================
请输入反馈 accept / reject / update偏好: accept
--- 循环 3 ---

正在调用大语言模型...
大语言模型响应成功。
模型输出:
Thought: 北京天气为Partly cloudy，适合出行；用户偏爱历史古迹且预算200元。但查询结果显示许多热门历史景点已售罄，因此需要根据规则调用备选工具，查询同类型且有余票的景点。

Action: get_alternative_attraction(city="北京", weather="Partly cloudy", target_type="历史古迹", exclude_spots="")

Observation: Beijing's top historical sites include the Forbidden City, Temple of Heaven, and the Great Wall at Mutianyu. These landmarks showcase the city's rich cultural heritage.
========================================
请输入反馈 accept / reject / update偏好: accept
--- 循环 4 ---

正在调用大语言模型...
大语言模型响应成功。
模型输出:
Thought: 北京天气为Partly cloudy，适合游览。用户偏爱历史古迹且预算200元。热门历史景点已售罄，根据备选工具返回的有余票景点（故宫、天坛、慕田峪长城），结合预算筛选：故宫门票60元、天坛15元、慕田峪长城45元均符合预算。优先推荐最具代表性且价格适中的天坛，备选慕田峪长城。用户可后续反馈是否接受。

Action: Finish[根据您的偏好（历史古迹、预算200元）和北京今天Partly cloudy天气，推荐景点：天坛（门票15元，历史古迹，有余票）；若您不满意，备选方案：慕田峪长城（门票45元，历史古迹）。这些景点均符合您的预算和历史偏好。请确认是否接受？]

任务完成，最终答案:
根据您的偏好（历史古迹、预算200元）和北京今天Partly cloudy天气，推荐景点：天坛（门票15元，历史古迹，有余票）；若您不满意，备选方案：慕田峪长城（门票45元，历史古迹）。这些景点均符合您的预算和历史偏好。请确认是否接受？
'''
