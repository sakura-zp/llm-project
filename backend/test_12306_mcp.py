"""
12306 MCP工具调用测试脚本
独立测试12306工具是否能正常调用
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent

# 尝试导入，如果失败则提示
try:
    from hello_agents import HelloAgentsLLM, SimpleAgent
    from hello_agents.tools import MCPTool
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("\n请确保:")
    print("1. 已激活虚拟环境")
    print("2. 已安装helloagents: pip install helloagents")
    print("\n使用方法:")
    print("  cd f:\\大模型项目\\hello-agents-main\\code\\chapter13\\helloagents-trip-planner")
    print("  .\\venv\\Scripts\\activate")
    print("  python backend\\test_12306_mcp.py")
    sys.exit(1)

def test_12306_basic():
    """测试基本的12306 MCP连接"""
    print("\n" + "="*60)
    print("测试1: 基本MCP连接")
    print("="*60)
    
    try:
        train_tool = MCPTool(
            name="train12306",
            description="12306列车票务服务",
            server_command=["npx", "-y", "12306-mcp"],
            auto_expand=True
        )
        print("✅ MCP工具创建成功")
        return train_tool
    except Exception as e:
        print(f"❌ MCP工具创建失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_12306_with_agent():
    """测试Agent调用12306工具"""
    print("\n" + "="*60)
    print("测试2: Agent调用12306工具")
    print("="*60)
    
    # 从.env加载配置
    from dotenv import load_dotenv
    env_path = project_root / ".env"
    load_dotenv(env_path)
    
    print(f"\n[配置信息]")
    print(f"LLM_API_KEY: {os.getenv('LLM_API_KEY', 'not set')[:20]}...")
    print(f"LLM_BASE_URL: {os.getenv('LLM_BASE_URL', 'not set')}")
    print(f"LLM_MODEL: {os.getenv('LLM_MODEL', 'not set')}")
    
    # 创建LLM
    try:
        llm = HelloAgentsLLM(
            provider="modelscope",
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            model=os.getenv("LLM_MODEL")
        )
        print(f"\n✅ LLM创建成功")
        print(f"   Provider: {llm.provider}")
        print(f"   Model: {llm.model}")
        print(f"   Base URL: {llm.base_url}")
    except Exception as e:
        print(f"❌ LLM创建失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 创建MCP工具
    try:
        train_tool = MCPTool(
            name="train12306",
            description="12306列车票务服务",
            server_command=["npx", "-y", "12306-mcp"],
            auto_expand=True
        )
        print(f"✅ MCP工具创建成功")
    except Exception as e:
        print(f"❌ MCP工具创建失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 简化的Prompt
    simple_prompt = """你是列车查询助手。

可用工具:
- train12306_get-station-code-of-city: 查询城市车站代码
- train12306_get-tickets: 查询列车余票

示例:
1. train12306_get-station-code-of-city(city="上海") -> "AOH"
2. train12306_get-station-code-of-city(city="广州") -> "IZQ"
3. train12306_get-tickets(date="2025-11-28", fromStation="AOH", toStation="IZQ")
"""
    
    # 创建Agent
    try:
        agent = SimpleAgent(
            name="列车查询测试",
            llm=llm,
            system_prompt=simple_prompt
        )
        agent.add_tool(train_tool)
        print(f"✅ Agent创建成功")
        print(f"   工具数量: {len(agent.list_tools())}")
        print(f"   工具列表: {agent.list_tools()}")
    except Exception as e:
        print(f"❌ Agent创建失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 测试简单查询
    print("\n" + "-"*60)
    print("执行查询: 查询上海车站代码")
    print("-"*60)
    
    query = "请使用工具查询上海的车站代码"
    
    try:
        print(f"\n📤 发送Query: {query}")
        print(f"⏳ 等待响应...")
        
        import time
        start_time = time.time()
        
        response = agent.run(query)
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ 查询完成 (用时: {elapsed:.1f}秒)")
        print(f"\n{'='*60}")
        print("📥 Agent响应:")
        print(f"{'='*60}")
        print(response)
        print(f"{'='*60}\n")
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ 查询失败 (用时: {elapsed:.1f}秒)")
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

def test_12306_full_query():
    """测试完整的列车查询流程"""
    print("\n" + "="*60)
    print("测试3: 完整列车查询流程")
    print("="*60)
    
    from dotenv import load_dotenv
    env_path = project_root / ".env"
    load_dotenv(env_path)
    
    # 创建LLM
    llm = HelloAgentsLLM(
        provider="modelscope",
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        model=os.getenv("LLM_MODEL")
    )
    
    # 创建MCP工具
    train_tool = MCPTool(
        name="train12306",
        description="12306列车票务服务",
        server_command=["npx", "-y", "12306-mcp"],
        auto_expand=True
    )
    
    # 创建Agent
    simple_prompt = """你是列车查询助手。必须使用工具查询。

工具:
- train12306_get-station-code-of-city(city)
- train12306_get-tickets(date, fromStation, toStation)
"""
    
    agent = SimpleAgent(
        name="列车查询",
        llm=llm,
        system_prompt=simple_prompt
    )
    agent.add_tool(train_tool)
    
    # 执行完整查询
    print("\n执行完整查询: 2025-11-28 上海->广州")
    
    query = """查询2025-11-28从上海到广州的列车。

步骤:
1. 查上海车站代码
2. 查广州车站代码
3. 查询余票
"""
    
    try:
        import time
        start_time = time.time()
        
        print(f"\n📤 Query: {query}")
        response = agent.run(query)
        
        elapsed = time.time() - start_time
        print(f"\n✅ 完成 (用时: {elapsed:.1f}秒)")
        print(f"\n{'='*60}")
        print("📥 响应:")
        print(f"{'='*60}")
        print(response)
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ 失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "🚆"*30)
    print("12306 MCP工具调用测试")
    print("🚆"*30)
    
    # 测试1: 基本连接
    tool = test_12306_basic()
    
    if tool:
        # 测试2: Agent调用
        test_12306_with_agent()
        
        # 测试3: 完整查询流程
        # test_12306_full_query()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60 + "\n")
