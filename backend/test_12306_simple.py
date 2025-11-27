"""
简化版12306测试 - 不使用Agent，直接调用工具
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

print("\n" + "="*60)
print("简化版12306工具测试")
print("="*60)

# 测试1: 直接调用12306 npx命令
print("\n测试1: 直接调用npx 12306-mcp")
print("-"*60)

import subprocess
import json

# 启动MCP服务器（Windows需要shell=True）
process = subprocess.Popen(
    ["npx", "-y", "12306-mcp"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8",  # 明确指定编码
    shell=True  # Windows需要
)

print("✅ MCP进程已启动")

# 发送初始化请求
init_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    }
}

print(f"\n📤 发送初始化请求...")
process.stdin.write(json.dumps(init_request) + "\n")
process.stdin.flush()

# 读取响应
import time
time.sleep(2)

try:
    response_line = process.stdout.readline()
    print(f"📥 收到响应: {response_line[:200]}")
    
    response = json.loads(response_line)
    
    if "result" in response:
        print(f"\n✅ 初始化成功!")
        print(f"   服务器名称: {response['result'].get('serverInfo', {}).get('name', 'unknown')}")
        
        # 需要单独请求工具列表
        print(f"\n步骤2: 请求工具列表")
        print("-"*60)
        
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(list_tools_request) + "\n")
        process.stdin.flush()
        time.sleep(1)
        
        tools_response_line = process.stdout.readline()
        print(f"📥 工具列表响应: {tools_response_line[:300]}...")
        
        tools_response = json.loads(tools_response_line)
        tools = tools_response.get('result', {}).get('tools', [])
        
        print(f"\n可用工具列表 ({len(tools)}个):")
        for i, tool in enumerate(tools, 1):
            print(f"   {i}. {tool.get('name', 'unknown')}")
            schema = tool.get('inputSchema', {})
            if 'properties' in schema:
                print(f"      参数: {', '.join(schema['properties'].keys())}")
        
        # 测试调用get-station-code-of-citys工具
        print(f"\n步骤3: 调用get-station-code-of-citys工具")
        print("-"*60)
        
        # 测试上海
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get-station-code-of-citys",
                "arguments": {
                    "citys": "上海"  # 修正为citys
                }
            }
        }
        
        print(f"📤 调用工具: get-station-code-of-citys(citys='上海')")
        process.stdin.write(json.dumps(call_request) + "\n")
        process.stdin.flush()
        
        time.sleep(2)
        tool_response = process.stdout.readline()
        print(f"📥 工具响应: {tool_response}")
        
        tool_result = json.loads(tool_response)
        if "result" in tool_result:
            print(f"\n✅ 工具调用成功!")
            print(f"   结果: {tool_result['result']}")
            shanghai_code = tool_result['result']['content'][0]['text']
        else:
            print(f"\n❌ 工具调用失败: {tool_result.get('error', 'unknown error')}")
            shanghai_code = None
        
        # 测试广州
        print(f"\n步骤4: 查询广州车站代码")
        print("-"*60)
        
        call_request2 = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get-station-code-of-citys",
                "arguments": {
                    "citys": "广州"
                }
            }
        }
        
        print(f"📤 调用工具: get-station-code-of-citys(citys='广州')")
        process.stdin.write(json.dumps(call_request2) + "\n")
        process.stdin.flush()
        
        time.sleep(2)
        tool_response2 = process.stdout.readline()
        print(f"📥 工具响应: {tool_response2}")
        
        tool_result2 = json.loads(tool_response2)
        if "result" in tool_result2:
            print(f"\n✅ 工具调用成功!")
            print(f"   结果: {tool_result2['result']}")
            guangzhou_code = tool_result2['result']['content'][0]['text']
        else:
            print(f"\n❌ 工具调用失败: {tool_result2.get('error', 'unknown error')}")
            guangzhou_code = None
        
        # 测试查询余票（如果获取到车站代码）
        if shanghai_code and guangzhou_code:
            print(f"\n步骤5: 查询列车余票")
            print("-"*60)
            
            # 从JSON中提取实际的代码
            import re
            sh_match = re.search(r'"station_code":\s*"([A-Z]+)"', shanghai_code)
            gz_match = re.search(r'"station_code":\s*"([A-Z]+)"', guangzhou_code)
            
            if sh_match and gz_match:
                sh_code = sh_match.group(1)
                gz_code = gz_match.group(1)
                
                print(f"上海车站代码: {sh_code}")
                print(f"广州车站代码: {gz_code}")
                
                call_request3 = {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "get-tickets",
                        "arguments": {
                            "date": "2025-11-29",
                            "fromStation": sh_code,
                            "toStation": gz_code
                        }
                    }
                }
                
                print(f"\n📤 调用工具: get-tickets(date='2025-11-29', fromStation='{sh_code}', toStation='{gz_code}')")
                process.stdin.write(json.dumps(call_request3) + "\n")
                process.stdin.flush()
                
                time.sleep(3)
                tickets_response = process.stdout.readline()
                print(f"\n📥 余票查询响应: {tickets_response[:500]}...")
                
                tickets_result = json.loads(tickets_response)
                if "result" in tickets_result:
                    print(f"\n✅ 余票查询成功!")
                    print(f"\n{'='*80}")
                    print("列车余票详细信息:")
                    print(f"{'='*80}")
                    print(tickets_result['result']['content'][0]['text'][:1000])
                    print(f"{'='*80}")
                else:
                    print(f"\n❌ 余票查询失败: {tickets_result.get('error', 'unknown error')}")
    else:
        print(f"\n❌ 初始化失败: {response.get('error', 'unknown error')}")
        
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    process.terminate()
    print(f"\n🔌 MCP进程已终止")
    print("="*60 + "\n")
