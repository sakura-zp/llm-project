"""
测试Agent是否能正确调用12306工具
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

from hello_agents import HelloAgentsLLM, SimpleAgent
from hello_agents.tools import MCPTool

print("\n" + "="*60)
print("测试Agent调用12306工具")
print("="*60)

# 创建LLM - 使用魔塔千问
print("\n步骤1: 创建LLM")
print("-"*60)

# 测试不同的Qwen模型
test_models = [
    "Qwen/Qwen2.5-7B-Instruct",      # 小模型，可能更快
    "Qwen/Qwen2.5-14B-Instruct",     # 中等模型
    "qwen-plus",                      # 魔塔的plus版本
    "Qwen/Qwen2.5-72B-Instruct",     # 原来的大模型
]

print("\n可用模型列表:")
for i, model in enumerate(test_models, 1):
    print(f"  {i}. {model}")

# 选择要测试的模型（默认测试第1个）
selected_model = test_models[0]  # 先测试7B小模型

print(f"\n选择测试模型: {selected_model}")

llm = HelloAgentsLLM(
    provider="modelscope",
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    model=selected_model  # 使用选中的模型
)

print(f"✅ LLM创建成功")
print(f"   Provider: {llm.provider}")
print(f"   Model: {llm.model}")

# 创建MCP工具
print("\n步骤2: 创建MCP工具")
print("-"*60)

train_tool = MCPTool(
    name="train12306",
    description="12306列车票务服务",
    server_command=["npx", "-y", "12306-mcp"],
    auto_expand=True
)

print(f"✅ MCP工具创建成功")

# 创建Agent - 使用非常简单的Prompt
print("\n步骤3: 创建Agent")
print("-"*60)

# 测试1: 最简单的Prompt
simple_prompt = """你是列车查询助手。

你有以下工具:
- train12306_get-station-code-of-citys: 查询城市车站代码(参数: citys)
- train12306_get-tickets: 查询列车余票(参数: date, fromStation, toStation)

当用户要查询列车时，你必须:
1. 先调用 train12306_get-station-code-of-citys 查询出发城市代码
2. 再调用 train12306_get-station-code-of-citys 查询目的地城市代码
3. 最后调用 train12306_get-tickets 查询余票
"""

agent = SimpleAgent(
    name="列车查询测试",
    llm=llm,
    system_prompt=simple_prompt
)
agent.add_tool(train_tool)

print(f"✅ Agent创建成功")
print(f"   工具数量: {len(agent.list_tools())}")

# 测试查询 - 减少超时时间到30秒
print("\n步骤4: 测试完整的列车查询流程")
print("-"*60)

# 测试1: 查询车站代码
print("\n[测试1] 查询上海车站代码")
query1 = "查询上海的车站代码"
print(f"📤 Query: {query1}")

import time
start_time = time.time()

try:
    import threading
    result_container = {"response": None, "error": None}
    
    def run_agent():
        try:
            result_container["response"] = agent.run(query1)
        except Exception as e:
            result_container["error"] = e
    
    thread = threading.Thread(target=run_agent)
    thread.daemon = True
    thread.start()
    thread.join(timeout=30)
    
    elapsed = time.time() - start_time
    
    if thread.is_alive():
        print(f"❌ 查询超时30秒")
        shanghai_code = None
    elif result_container["error"]:
        print(f"❌ 查询失败: {result_container['error']}")
        shanghai_code = None
    else:
        response = result_container["response"]
        print(f"✅ 完成 (用时: {elapsed:.1f}秒)")
        print(f"📥 响应: {response}")
        
        # 提取车站代码
        if "SHH" in response:
            shanghai_code = "SHH"
            print(f"✅ 成功获取上海车站代码: {shanghai_code}")
        else:
            shanghai_code = None
            print(f"⚠️  未找到车站代码")
            
except Exception as e:
    print(f"❌ 测试失败: {e}")
    shanghai_code = None

# 测试2: 查询广州车站代码
print("\n" + "-"*60)
print("[测试2] 查询广州车站代码")
query2 = "查询广州的车站代码"
print(f"📤 Query: {query2}")

start_time = time.time()

try:
    result_container = {"response": None, "error": None}
    
    thread = threading.Thread(target=lambda: result_container.update({"response": agent.run(query2)}))
    thread.daemon = True
    thread.start()
    thread.join(timeout=30)
    
    elapsed = time.time() - start_time
    
    if thread.is_alive():
        print(f"❌ 查询超时30秒")
        guangzhou_code = None
    elif result_container["error"]:
        print(f"❌ 查询失败: {result_container['error']}")
        guangzhou_code = None
    else:
        response = result_container["response"]
        print(f"✅ 完成 (用时: {elapsed:.1f}秒)")
        print(f"📥 响应: {response}")
        
        # 提取车站代码
        if "GZQ" in response or "IZQ" in response:
            guangzhou_code = "GZQ" if "GZQ" in response else "IZQ"
            print(f"✅ 成功获取广州车站代码: {guangzhou_code}")
        else:
            guangzhou_code = None
            print(f"⚠️  未找到车站代码")
            
except Exception as e:
    print(f"❌ 测试失败: {e}")
    guangzhou_code = None

# 测试3: 查询列车余票（只有前两步成功才执行）
if shanghai_code and guangzhou_code:
    print("\n" + "-"*60)
    print("[测试3] 查询列车余票")
    query3 = f"查询2025-11-29从上海到广州的列车余票"
    print(f"📤 Query: {query3}")
    
    start_time = time.time()
    
    try:
        result_container = {"response": None, "error": None}
        
        def run_tickets_query():
            try:
                result_container["response"] = agent.run(query3)
            except Exception as e:
                result_container["error"] = e
        
        thread = threading.Thread(target=run_tickets_query)
        thread.daemon = True
        thread.start()
        thread.join(timeout=60)  # 查询余票给更多时间
        
        elapsed = time.time() - start_time
        
        if thread.is_alive():
            print(f"❌ 查询超时60秒")
            tickets_success = False
        elif result_container["error"]:
            print(f"❌ 查询失败: {result_container['error']}")
            tickets_success = False
        else:
            response = result_container["response"]
            print(f"✅ 完成 (用时: {elapsed:.1f}秒)")
            print(f"\n{'='*60}")
            print("📥 列车余票查询结果:")
            print(f"{'='*60}")
            print(response)
            print(f"{'='*60}")
            
            # 检查是否包含列车信息
            if "G" in response or "D" in response or "车次" in response or "票价" in response:
                tickets_success = True
                print(f"\n✅ 成功查询到列车余票信息!")
            else:
                tickets_success = False
                print(f"\n⚠️  响应中未找到列车信息")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        tickets_success = False
else:
    print("\n⚠️  跳过余票查询（车站代码获取失败）")
    tickets_success = False

print("\n" + "="*60)
print("测试完成")
print("="*60)
print("\n测试结果总结:")
if 'shanghai_code' in locals() and shanghai_code:
    print(f"  ✅ 测试1 - 查询上海车站代码: 成功 ({shanghai_code})")
else:
    print(f"  ❌ 测试1 - 查询上海车站代码: 失败")
    
if 'guangzhou_code' in locals() and guangzhou_code:
    print(f"  ✅ 测试2 - 查询广州车站代码: 成功 ({guangzhou_code})")
else:
    print(f"  ❌ 测试2 - 查询广州车站代码: 失败")
    
if 'tickets_success' in locals() and tickets_success:
    print(f"  ✅ 测试3 - 查询列车余票: 成功")
else:
    print(f"  ❌ 测试3 - 查询列车余票: 失败或未执行")

print("\n结论:")
if 'tickets_success' in locals() and tickets_success:
    print("✅ 所有测试通过！Agent可以正常调用12306工具")
    print("\n下一步: 可以将该模型配置集成到主项目")
    print(f"  1. 确认.env中LLM_MODEL_ID={selected_model}")
    print(f"  2. 确认config.py中llm_model={selected_model}")
    print(f"  3. 重启后端服务")
else:
    print("❌ 测试未完全通过")
    print("\n建议:")
    print("  1. 尝试其他Qwen模型（修改selected_model的索引）")
    print(f"     selected_model = test_models[0]  # 0=7B, 1=14B, 2=qwen-plus, 3=72B")
    print("  2. 或者换用OpenAI/DeepSeek等其他LLM提供商")
    print("  3. 或者不使用Agent，直接在后端调用12306 API")
print("="*60 + "\n")
