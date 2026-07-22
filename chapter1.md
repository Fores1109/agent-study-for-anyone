
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
