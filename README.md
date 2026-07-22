# agent-study-for-anyone
尝试记录学习agent的过程.jpg
主要学习以下两个项目：https://github.com/datawhalechina/hello-agents & https://github.com/Zchary1106/agent-interview-hub


## 20260719学习笔记
### hello-agents第一章习题作答https://datawhalechina.github.io/hello-agents/#/./chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93?id=%e4%b9%a0%e9%a2%98
  1. - case A：不是一个智能体，因为它不具有自主性，不能通过响应一些外部环境来采取行动，只能够以人的具体命令来执行标准化的输入输出流程，超级计算机只是计算硬件，**无感知**、**无自主决策循环**。
     - case B：是智能体，Tesla汽车能够响应车辆行驶过程中车道环境与其他车辆的变化来采取相应驾驶措施，一般智能驾驶都需要给定一个目的地才能开始，因此特斯拉智能驾驶系统是一个基于目标的智能体。在时间与反应性维度上，它是一个混合式智能体，既要随时反应路面上各种情况，也要在整个运作过程中进行整体性的规划。基于知识表示的分类中，以亚符号主义AI为主，仅少量交通限速、安全阈值用固定规则，并非典型神经符号融合架构。
     - case C：是智能体，AlphaGo通过强化学习来进行未来若干步骤的推理，基于知识表示的分类中，它可以被分为亚符号主义AI。在时间与反应性维度上，它并不需要将时间成本压缩到较小水平，只需要大量计算与推理最终尽可能获胜即可，因此它是典型的规划式智能体。同时它基于内部决策架构，被认为是基于目标的智能体，原因是它所有的思考与推理都是为了赢游戏这一个目标。
     - case D：是智能体，基于内部决策架构的分类，它是一个基于效用的智能体，具体来说，它要尽可能让客户在与它对话中能够有效率的解决问题，并让客户满意。基于时间与反应性的分类来说，它是混合式智能体，既要快速响应顾客需求，也要确保回答的质量即，时回复安抚话术属于反应层；分步执行「查订单→定位问题→输出方案」是多步骤流程规划，两者结合。基于知识表示的分类来说，主体亚符号，外挂独立符号系统，不属于神经符号智能体，ChatGPT 大模型本体是神经网络（亚符号）；订单数据库、业务规则是外部符号工具，仅通过 API 调用拼接，模型内部不存在符号与神经网络深度融合推理。

  2. - performance（评判智能体好坏的指标）：健身目标达成度、运动安全性、动作标准度、计划适配性
     - environment（智能体交互的外部环境）：用户人体、健身场地、可穿戴硬件、外部数据系统
     - actuators（智能体对外输出动作）：健身动作指导，语音播报、饮食方案参考、风险警告
     - sensors（感知环境输入）：可穿戴硬件设备、用户主动输入个人信息、动作识别、历史数据传感器
     - 部分可观察、随机环境、连续时序环境、动态环境、单智能体环境
  3. - 方案A：优点：将一部分订单售后进行自动化处理，只有7天以内的100元以上的非特殊品需要进行人工操作，不存在误判、开发简单、运维成本稳定、可控性强；缺点：流程规则僵硬，无法处理复杂边缘场景、规则迭代成本高、人工压力大
     - 方案B：优点：柔性决策，适配复杂、模糊场景、天然支持个性化差异处理，自动识别用户信誉高低、具备自主迭代能力、解放人工压力；缺点：建设成本高、周期长、存在幻觉问题、解释性差、运行成本高
     - 适用场景：
       - workflow：业务简单、商品标准化、开发预算有限、售后单量小；
       - agent：商品品类复杂，用户分层明显，工单量级大，存在大量非结构化数据，企业具备算法团队，能够承担开发成本。
     - 中小型企业优先选择workflow，开发成本低，售后场景简单；中大型企业使用workflow与agent综合体系
     - 方案C：workflow提前过滤简单售后单，留下较为复杂的模糊边界问题与客户信誉判断问题交给agent解决
  4. - ```python
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
        """;
       ```
       ```python
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
       ```
       ```python
       
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

       ```
       ```python
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
       ```

  5. 电力调度系统
     - 系统1：实时监测电网状态、负荷预测、异常检测、新能源出力预测
     - 系统2：制定电力调度方案、安全约束检查、故障恢复推理、经济运行优化、解释决策原因
     - 首先，系统1持续采集和分析实时运行数据，对负荷变化、设备状态以及新能源出力进行快速预测。当检测到负荷突增、设备异常或新能源发电波动时，立即向系统2发送预警信息及预测结果。随后，系统2结合电网运行规则、安全约束和专家知识，对系统1提供的信息进行深入分析，制定最优调度方案，并验证方案是否满足安全运行要求。如果发现存在风险，则进一步调整调度策略，最终输出可靠的调度决策。调度完成后，系统1继续实时监测电网运行情况，对执行效果进行反馈。当实际运行状态与预测存在偏差时，再次触发系统2进行重新规划，形成"实时感知—智能推理—执行反馈—持续优化"的闭环。
  6. - 智能体出现幻觉主要是由于大模型会出现幻觉，大语言模型本质上是基于大量文本数据进行概率预测，其目标是预测最有可能出现的下一个词，而不是保证事实的真实性。
     - 可能会出现无法finish的情况，陷入死循环：无限调用工具、工具调用失败的死循环、推理循环、api成本增加
     - 任务完成率、准确率、推理能力、工具调用能力、效率、鲁棒性、用户满意度

## 20260720学习笔记
### hello-agents第二章习题作答

  1. - 充分性：任何物理符号，只要组织的足够完善，就一定能够表现出一般智能行为
     - 必要性：任何能够表现一般智能的系统，本质上都必须是一个物理符号系统
     - 现实医学知识数量巨大，而且不断更新，人工维护几乎不可行，这表明：即使符号推理机制正确，如果知识无法完整获取，系统仍然无法表现出真正智能；专家系统只能处理规则覆盖到的情况。符号主义智能体在实践中暴露出的知识获取瓶颈、脆弱性、常识推理困难、缺乏学习能力以及感知能力不足等问题，对"充分性论断"提出了挑战，说明仅依靠符号操作难以实现真正的通用智能。
     - 大语言模型驱动的智能体虽然能够处理语言符号并展现出推理能力，但其内部机制建立在神经网络的分布式表示和概率学习之上，因此更符合现代**神经符号融合Neuro-Symbolic AI**的发展方向，而不是传统物理符号系统假说的经典实现。
  2. - MYCIN未能广泛应用于临床实践，并非仅因为"知识获取瓶颈"和"脆弱性"，还受到法律责任、伦理风险、知识更新、患者个体差异、缺乏学习能力、用户信任以及监管审批等多方面因素的制约。
     - 如果设计现代医疗诊断智能体，应采用大模型+RAG+知识图谱+规则引擎+多模态感知+医生监督的混合架构，使系统既具备持续学习和复杂推理能力，又能保证可解释性、安全性和可靠性。AI应定位为临床决策支持工具（CDSS），辅助医生而非取代医生。
     - 最后，尽管深度学习在感知和预测任务中表现突出，但在规则明确、需要严格可解释、错误代价极高的垂直领域（如税务、银行风控、药物禁忌、航空控制、法律合规等），基于规则的专家系统仍然是更优选择。现代智能系统的发展趋势也并非完全替代规则系统，而是将规则推理与数据驱动方法有机结合，发挥两者各自优势。
  3. ```python
      import re
      import random
      
      # ===========================
      # 上下文记忆
      # ===========================
      memory = {
          "name": None,
          "age": None,
          "job": None
      }
      
      # ===========================
      # ELIZA规则
      # ===========================
      rules = [
      
          # 工作
          (
              r"I work as (.+)",
              [
                  "How do you feel about your work as {}?",
                  "Why did you choose to become {}?",
                  "Do you enjoy being a {}?"
              ]
          ),
      
          # 学习
          (
              r"I study (.+)",
              [
                  "What do you enjoy most about studying {}?",
                  "Is {} difficult for you?",
                  "Why did you choose to study {}?"
              ]
          ),
      
          # 爱好
          (
              r"My hobby is (.+)",
              [
                  "Why do you enjoy {}?",
                  "How long have you been interested in {}?",
                  "What do you like most about {}?"
              ]
          ),
      
          # 喜欢
          (
              r"I like (.+)",
              [
                  "What makes you like {}?",
                  "When did you start liking {}?",
                  "Tell me more about why you like {}."
              ]
          ),
      
          # 疲劳
          (
              r"I am tired",
              [
                  "Have you been working too hard recently?",
                  "Would taking a break help?",
                  "What do you think is making you tired?"
              ]
          ),
      
          # 开心
          (
              r"I am happy",
              [
                  "That's wonderful! What made you happy?",
                  "I'm glad to hear that.",
                  "Can you tell me more about it?"
              ]
          ),
      
          # 难过
          (
              r"I am sad",
              [
                  "I'm sorry to hear that.",
                  "Would you like to talk about it?",
                  "What happened?"
              ]
          ),
      
          # 我觉得...
          (
              r"I think (.+)",
              [
                  "Why do you think {}?",
                  "What makes you believe {}?",
                  "Can you explain more about {}?"
              ]
          )
      ]
      
      # ===========================
      # 更新记忆
      # ===========================
      def update_memory(text):
      
          name = re.search(r"My name is (\w+)", text, re.IGNORECASE)
          if name:
              memory["name"] = name.group(1)
      
          age = re.search(r"I am (\d+) years old", text, re.IGNORECASE)
          if age:
              memory["age"] = age.group(1)
      
          job = re.search(r"I work as (.+)", text, re.IGNORECASE)
          if job:
              memory["job"] = job.group(1)
      
      # ===========================
      # 代词转换
      # ===========================
      def transform_pronouns(text):
      
          replacements = {
              " my ": " your ",
              " My ": " Your ",
              " i ": " you ",
              " I ": " You ",
              " me ": " you ",
              " am ": " are "
          }
      
          result = " " + text + " "
      
          for old, new in replacements.items():
              result = result.replace(old, new)
      
          return result.strip()
      
      # ===========================
      # 回答生成
      # ===========================
      def generate_response(user_input):
      
          update_memory(user_input)
      
          lower = user_input.lower()
      
          # ---------- 查询记忆 ----------
          if "who am i" in lower:
              if memory["name"]:
                  return f"Your name is {memory['name']}."
              return "I don't know your name yet."
      
          if "how old am i" in lower:
              if memory["age"]:
                  return f"You are {memory['age']} years old."
              return "You haven't told me your age."
      
          if "what is my job" in lower:
              if memory["job"]:
                  return f"You work as {memory['job']}."
              return "You haven't told me your job."
      
          # ---------- 规则匹配 ----------
          for pattern, responses in rules:
      
              match = re.match(pattern, user_input, re.IGNORECASE)
      
              if match:
      
                  groups = list(match.groups())
      
                  # 做代词转换
                  groups = [transform_pronouns(g) for g in groups]
      
                  response = random.choice(responses)
      
                  if groups:
                      return response.format(*groups)
                  else:
                      return response
      
          # ---------- 默认回复 ----------
          generic = [
              "Please tell me more.",
              "Can you explain that further?",
              "Why do you say that?",
              "How does that make you feel?",
              "That's interesting. Go on.",
              "Could you elaborate on that?"
          ]
      
          return random.choice(generic)
      
      # ===========================
      # 主程序
      # ===========================
      def main():
      
          print("=" * 50)
          print("      ELIZA Chatbot (Enhanced Version)")
          print("Type 'quit' to exit.")
          print("=" * 50)
      
          while True:
      
              user_input = input("\nYou: ")
      
              if user_input.lower() == "quit":
                  print("ELIZA: Goodbye! Have a nice day.")
                  break
      
              response = generate_response(user_input)
      
              print("ELIZA:", response)
      
      
      # ===========================
      # 运行
      # ===========================
      if __name__ == "__main__":
          main()


     ```

     - 虽然扩展后的 ELIZA 增加了工作、学习、爱好等规则，并实现了简单的上下文记忆，但它与 ChatGPT 在底层原理和能力上仍存在本质区别。
     - | 对比维度       | 扩展后的 ELIZA                     | ChatGPT                                         |
        | ---------- | ------------------------------ | ----------------------------------------------- |
        | **实现原理**   | 基于人工编写的规则和模板匹配，通过关键词匹配生成固定回复。  | 基于 Transformer 大语言模型，通过海量数据训练学习语言规律，利用神经网络生成回答。 |
        | **知识来源**   | 知识全部来自程序员编写的规则，知识范围有限。         | 知识来源于大规模训练数据，并可结合检索增强（RAG）等技术获取最新知识。            |
        | **语义理解能力** | 只能识别预设关键词，无法真正理解用户意图和语义。       | 能够理解上下文语义、隐含含义和复杂表达，具有较强的语言理解能力。                |
        | **上下文能力**  | 只能记住少量固定信息（如姓名、年龄、职业），上下文能力有限。 | 能够综合多轮对话内容进行连续推理，保持较好的上下文一致性。                   |
        | **泛化能力**   | 对未编写规则的问题通常无法回答，只能返回默认回复。      | 能处理大量未见过的新问题，具有较强的泛化能力。                         |
        | **学习能力**   | 不具备自主学习能力，新增知识需要人工修改规则。        | 模型通过训练学习知识，虽然不会在聊天过程中即时学习，但整体具有较强的学习和泛化能力。      |
        | **推理能力**   | 基本没有真正推理能力，仅执行规则匹配。            | 能完成逻辑推理、数学计算、代码生成、文本创作等复杂任务。                    |
       
     - 开放域对话具有高度复杂性，用户的一句话可能同时包含多个属性：
     - 假设需要考虑：

        职业：100种
        兴趣：100种
        城市：100种
        年龄：50种
        情绪：20种
        
        则需要覆盖的组合数量约为：
        
        100×100×100×50×20
        
        即：
        
        1e+9
        
        约10亿种组合。
        
        显然，不可能人工编写和维护如此庞大的规则库。
     - 即使系统已经建立完成，只增加一种新的属性值，也会带来很多规则更新的需求。
  4. - 如果 GRASP（抓取）智能体失效，整个系统将无法完成"抓取积木"这一关键步骤。虽然其他智能体仍能继续工作，但由于无法真正抓住积木，因此整个搭建任务最终会失败。系统不会完全崩溃，而是停留在抓取之前的阶段，表现为局部功能失效导致整体任务无法完成。这种去中心化架构具有明显的优点：**模块化程度高、易于扩展、具有一定容错能力、便于并行协作**，但也存在明显不足：**模块之间依赖较强、协调成本较高、系统调试更加复杂、整体效率可能受到通信开销影响**。
     - "心智社会"理论与现代多智能体系统有着明显的思想继承关系。两者都认为，复杂智能并非来源于一个万能个体，而是来源于多个不同角色之间的协作。
       - CAMEL-Workforce：通过多个具有不同身份和职责的大语言模型智能体（如产品经理、程序员、测试工程师等）共同完成复杂任务。
       - MetaGPT：模拟真实软件公司的组织结构，不同智能体分别承担需求分析、系统设计、代码开发、测试等职责。
       - CrewAI：允许开发者定义多个智能体及其角色，通过协作完成信息检索、数据分析、代码编写等复杂流程。
     - 这些系统与"心智社会"理论都采用了任务分解、角色分工、协同合作的思想，因此可以认为现代多智能体系统是"心智社会"理论在大语言模型时代的一种具体实现。现代多智能体系统（如 CAMEL-Workforce、MetaGPT、CrewAI）继承了"心智社会"关于分工协作的思想，但借助大语言模型，每个智能体本身已经具备较强的推理和规划能力，因此形成了"强智能体协作"的新模式。
     - 现在大模型和智能体的推理能力强大，并不意味着"心智社会"理论已经失效，相反，它仍然具有重要的指导意义，只是实现方式发生了变化。明斯基提出"无心智能体"的核心思想，并不是要求每个智能体必须能力弱，而是强调复杂智能可以由多个相对独立的功能模块协同产生。这一思想在今天仍然成立。过去强调的是"多个简单智能体组成复杂智能"，而今天更多体现为"多个具有较强能力的智能体通过协作实现更复杂、更可靠的智能"。
  5. - alphago首先利用大量人类棋谱进行监督学习，学习基本的围棋规则，得到初始策划网络，然后不再依赖人类数据，进行自我对弈，自己与自己下棋，当一盘结束后进行奖惩，赢棋就+1，输棋就-1，如果某些下法赢了，就提高这些策略被选择的概率，如果导致失败就降低其概率；因此，AlphaGo并不是程序员告诉它"哪一步一定最好"，而是在不断试错中逐渐找到最优策略，这正体现了强化学习的"试错学习"机制。
     - 序贯决策（Sequential Decision Making）是指当前的决策会影响未来状态和最终结果。具有两个特点：当前动作会改变未来环境，最终奖励往往很步之后才能获得，强化学习正是针对这种"延迟奖励（Delayed Reward）"设计的，它追求的是最大化长期累计奖励（Cumulative Reward），而不是只优化当前一步。
     - 强化学习与监督学习的数据需求，最大的区别在于训练数据来源不同。监督学习需要大量已经被标注好的数据，模型学习别人是怎么做的；强化学习没有标准答案，模型不断尝试，自己发现什么策略最好。
     - 训练马里奥：
       - 使用监督学习：需要大量人工示范数据：因此需要：大量高手游戏录像&每一帧对应按键标签。
       - 使用强化学习：不需要人工示范，只需要游戏环境与奖励函数：例如前进一步+1，获得金币＋50，通关+100
     - 对于超级马里奥，强化学习更加适合。
        - 不需要大量人工标注数据，降低了数据收集成本。
        - 能够探索新的策略，甚至发现人类没有使用过的玩法。
        - 适合长期奖励优化，例如为了最终通关，可以暂时放弃眼前的小奖励。
        - 具有较好的适应能力，面对不同关卡可以继续学习和优化。
     - 大语言模型的训练通常包括三个阶段：预训练、监督微调、强化学习优化。强化学习主要用于模型对齐，使模型生成的回答更加符合人类需求。强化学习人工标注发生在模型已经能够生成回答之后。
  6. - 符号主义时代的专家系统（如 MYCIN）主要依赖人工构建知识库。知识需要由领域专家总结经验，再由知识工程师将其编写成大量的规则（如 IF-THEN 规则），这一过程耗时耗力，且知识更新困难，因此被称为知识获取瓶颈（Knowledge Acquisition Bottleneck）。预训练模型则采用了完全不同的方式。它直接利用海量互联网文本、书籍、论文等数据进行自监督学习，不需要人工逐条编写规则，而是在训练过程中自动学习语言规律和知识表示。因此，知识获取从"人工录入"转变为"自动学习"，极大降低了知识构建成本，并能够学习到远超人工规则库规模的知识。
     - 虽然互联网提供了海量训练数据，但其质量参差不齐，因此也会带来一些问题。
       - 错误信息和幻觉
       - 数据偏见
       - 知识时效性不足
       - 隐私与版权问题
     - "预训练-微调"范式在未来仍将长期存在，但其具体形式可能不断演化，而不是被完全取代。一方面，预训练能够让模型学习通用语言知识，微调则可以针对医疗、法律、金融等具体领域快速适配，已经在实践中证明了其有效性。因此，这一范式仍然具有重要价值。另一方面，随着人工智能的发展，未来可能出现一些新的训练模式，例如检索增强生成（RAG）、智能体（Agent）、持续学习（Continual Learning）、多智能体协作（Multi-Agent），在保留预训练模型作为基础能力的同时，结合外部知识和工具，形成更加智能和灵活的系统，而不是完全放弃预训练。
  7. - 符号主义时代只能依赖人工规则，能够完成简单语法检查，但难以理解代码语义，因此智能代码审查几乎不可能实现。
     - 深度学习时代利用神经网络学习代码特征，在漏洞检测、代码分类等单一任务上取得一定进展，但仍缺乏整体理解和推理能力。
     - 大语言模型与智能体时代，预训练模型提供了强大的代码理解和自然语言生成能力，Agent 架构负责任务规划与分工，RAG 提供最新项目知识，工具调用实现真实验证，多种能力协同工作，使智能代码审查从过去的规则匹配发展为能够理解代码、发现问题、解释原因并提出改进建议的综合系统。

  
         用户提交 Pull Request
                   │
                   ▼
           任务规划（Planner）
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
代码理解Agent   Bug检测Agent   规范检查Agent
      │            │            │
      └────────────┼────────────┘
                   ▼
          检索增强（RAG）
    （项目文档/API/历史PR）
                   │
                   ▼
         工具调用（Tools）
Git、编译器、测试工具、静态分析器
                   │
                   ▼
         综合推理（LLM）
                   │
                   ▼
        自动生成代码审查报告




