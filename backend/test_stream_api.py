#!/usr/bin/env python3
"""
测试流式API端点
"""
import asyncio
import aiohttp
import json

async def test_stream_api():
    """测试流式API端点"""
    url = "http://localhost:8000/api/v1/chat/stream"
    
    # 测试数据
    payload = {
        "message": "你好，请介绍一下劳动合同法",
        "session_id": None,
        "model_provider": "siliconflow"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                print(f"状态码: {response.status}")
                print(f"响应头: {dict(response.headers)}")
                
                if response.status == 200:
                    print("开始接收流式响应...")
                    async for line in response.content:
                        if line:
                            line_text = line.decode('utf-8').strip()
                            if line_text:
                                print(f"收到: {line_text}")
                                # 解析SSE格式
                                if line_text.startswith("data: "):
                                    data = line_text[6:]  # 移除"data: "前缀
                                    if data != "[DONE]":
                                        try:
                                            chunk = json.loads(data)
                                            print(f"解析数据: {chunk}")
                                        except json.JSONDecodeError:
                                            print(f"无法解析JSON: {data}")
                else:
                    text = await response.text()
                    print(f"错误响应: {text}")
                    
    except aiohttp.ClientConnectorError as e:
        print(f"连接错误: {e}")
        print("请确保后端服务正在运行 (端口 8000)")
    except Exception as e:
        print(f"测试失败: {e}")

async def test_regular_api():
    """测试常规API端点"""
    url = "http://localhost:8000/api/v1/chat"
    
    payload = {
        "message": "你好，请介绍一下劳动合同法",
        "session_id": None,
        "model_provider": "siliconflow"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                print(f"\n常规API状态码: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"常规API响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                else:
                    text = await response.text()
                    print(f"常规API错误: {text}")
    except Exception as e:
        print(f"常规API测试失败: {e}")

async def main():
    """主函数"""
    print("=== 测试流式聊天API ===")
    await test_stream_api()
    
    print("\n=== 测试常规聊天API ===")
    await test_regular_api()

if __name__ == "__main__":
    asyncio.run(main())