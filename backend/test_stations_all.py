"""
查询城市的所有车站代码
"""
import subprocess
import json
import time

process = subprocess.Popen(
    ["npx", "-y", "12306-mcp"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8",
    shell=True
)

print("✅ MCP进程已启动\n")

# 初始化
init_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1.0.0"}
    }
}

process.stdin.write(json.dumps(init_request) + "\n")
process.stdin.flush()
time.sleep(2)
process.stdout.readline()

print("="*60)
print("查询上海所有车站")
print("="*60)

# 查询上海所有车站
request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "get-stations-code-in-city",
        "arguments": {"city": "上海"}
    }
}

process.stdin.write(json.dumps(request) + "\n")
process.stdin.flush()
time.sleep(2)

response = json.loads(process.stdout.readline())
print(response['result']['content'][0]['text'])

print("\n" + "="*60)
print("查询广州所有车站")
print("="*60)

# 查询广州所有车站
request2 = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "get-stations-code-in-city",
        "arguments": {"city": "广州"}
    }
}

process.stdin.write(json.dumps(request2) + "\n")
process.stdin.flush()
time.sleep(2)

response2 = json.loads(process.stdout.readline())
print(response2['result']['content'][0]['text'])

process.terminate()
print("\n✅ 测试完成\n")
