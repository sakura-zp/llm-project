"""
直接测试查询上海到广州的列车余票
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

from hello_agents import HelloAgentsLLM, SimpleAgent
from hello_agents.tools import MCPTool

print("\n" + "="*60)
print("测试直接查询列车余票")
print("="*60)

# 创建LLM
print("\n创建LLM...")
llm = HelloAgentsLLM(
    provider="modelscope",
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    model="Qwen/Qwen2.5-7B-Instruct"
)
print(f"✅ LLM: {llm.model}")

# 创建MCP工具
print("\n创建12306工具...")
train_tool = MCPTool(
    name="train12306",
    description="12306列车票务服务",
    server_command=["npx", "-y", "12306-mcp"],
    auto_expand=True
)
print("✅ 工具创建成功")

# 创建Agent
print("\n创建Agent...")
simple_prompt = """你是列车查询助手。

你有以下工具:
- train12306_get-stations-code-in-city: 查询城市所有车站(参数: city)
- train12306_get-tickets: 查询列车余票(参数: date, fromStation, toStation)

当用户要查询列车时，按以下步骤操作:
1. 调用 train12306_get-stations-code-in-city 查询出发城市所有车站
2. 调用 train12306_get-stations-code-in-city 查询目的地城市所有车站
3. 从车站列表中选择高铁站（优先选择包含"虹桥"或"南"的车站）
   - 上海优先: 上海虹桥(AOH)
   - 广州优先: 广州南(IZQ)
4. 调用 train12306_get-tickets 查询余票

返回时必须包含详细的车次、发车时间、到达时间、票价信息。
"""

agent = SimpleAgent(
    name="列车查询",
    llm=llm,
    system_prompt=simple_prompt
)
agent.add_tool(train_tool)
print(f"✅ Agent创建成功 (工具数: {len(agent.list_tools())})")

# 直接查询余票
print("\n" + "="*60)
print("查询: 2025-11-29 上海 → 广州 列车余票")
print("="*60)

query = "查询2025年11月29日从上海到广州的列车余票，包括车次、时间、票价等详细信息"

print(f"\n📤 Query: {query}")
print(f"⏳ 等待响应...\n")

import time
start_time = time.time()

try:
    import threading
    result_container = {"response": None, "error": None}
    
    def run_query():
        try:
            result_container["response"] = agent.run(query)
        except Exception as e:
            result_container["error"] = e
    
    thread = threading.Thread(target=run_query)
    thread.daemon = True
    thread.start()
    thread.join(timeout=90)  # 90秒超时
    
    elapsed = time.time() - start_time
    
    if thread.is_alive():
        print(f"❌ 查询超时 (90秒)")
    elif result_container["error"]:
        print(f"❌ 查询失败: {result_container['error']}")
    else:
        response = result_container["response"]
        print(f"✅ 查询完成 (用时: {elapsed:.1f}秒)")
        print(f"\n{'='*80}")
        print("📥 列车余票查询结果:")
        print(f"{'='*80}")
        print(response)
        print(f"{'='*80}")
        
        # 分析结果
        print(f"\n{'='*80}")
        print("结果分析:")
        print(f"{'='*80}")
        
        if "G" in response or "D" in response:
            print("✅ 包含高铁/动车车次")
        if "票价" in response or "¥" in response or "元" in response:
            print("✅ 包含票价信息")
        if ":" in response and ("时" in response or "分" in response):
            print("✅ 包含时刻信息")
        if "二等座" in response or "一等座" in response or "商务座" in response:
            print("✅ 包含座位等级信息")
            
        # 检查是否真的查询到了列车
        if any(keyword in response for keyword in ["G", "D", "车次", "票价", "二等座"]):
            print("\n🎉 查询成功！获取到详细的列车信息")
        else:
            print("\n⚠️  响应中可能没有实际的列车数据")
            
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80 + "\n")
