import os
import asyncio
from typing import Optional
from contextlib import AsyncExitStack
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import OpenAI
from dotenv import load_dotenv

from fastapi import FastAPI, Request
import uvicorn

load_dotenv()  # 加载环境变量从 .env

class MCPClient:
    def __init__(self):
        # 初始化会话和客户端对象
        self.session: Optional[ClientSession] = None # 会话对象
        self.exit_stack = AsyncExitStack() # 退出堆栈
        self.openai = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1") # OpenAI 客户端
        self.model="qwen2.5:32b"

    def get_response(self, messages: list,tools: list):
        response = self.openai.chat.completions.create(
            model=self.model,
            max_tokens=1000,
            messages=messages,
            tools=tools,
            temperature=1,
        )
        return response
    
    async def get_tools(self):
        # 列出可用工具
        response = await self.session.list_tools()
        available_tools = [{ 
            "type":"function",
            "function":{
                "name": tool.name,
                "description": tool.description, # 工具描述
                "parameters": tool.inputSchema  # 工具输入模式
            }
        } for tool in response.tools]
        
        return available_tools
        
    
    async def connect_to_server(self, server_script_path: str):
        """连接到 MCP 服务器
    
        参数:
            server_script_path: 服务器脚本路径 (.py 或 .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("服务器脚本必须是 .py 或 .js 文件")
            
        command = "python" if is_python else "node"
        # 创建 StdioServerParameters 对象
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        
        # 使用 stdio_client 创建与服务器的 stdio 传输
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        
        # 解包 stdio_transport，获取读取和写入句柄
        self.stdio, self.write = stdio_transport
        
        # 创建 ClientSession 对象，用于与服务器通信
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        # 初始化会话
        await self.session.initialize()
        # 列出可用工具
        response = await self.session.list_tools()
        tools = response.tools
        print("\\n连接到服务器，工具列表:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """使用 OpenAI 和可用工具处理查询"""
        
        # 创建消息列表
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        
        # 列出可用工具
        available_tools = await self.get_tools()
        # 处理消息
        response = self.get_response(messages, available_tools)

        # 处理LLM响应和工具调用
        tool_results = []
        final_text = []
        for choice in response.choices:
            message = choice.message
            # 如果有消息内容，先添加到结果中
            if message.content:
                final_text.append(message.content)
                
            is_function_call = message.tool_calls
            # 如果是工具调用
            if is_function_call:
                tool_name = message.tool_calls[0].function.name
                tool_args = json.loads(message.tool_calls[0].function.arguments)
                print(f"准备调用工具: {tool_name}")
                print(f"参数: {json.dumps(tool_args, ensure_ascii=False, indent=2)}")
                
                # 执行工具调用，获取结果
                result = await self.session.call_tool(tool_name, tool_args)
                tool_results.append({"call": tool_name, "result": result})
                
                # 将助手的回应添加到消息历史
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": message.tool_calls
                })
                
                # 将工具调用结果添加到消息历史
                messages.append({
                    "role": "tool",
                    "tool_call_id": message.tool_calls[0].id,
                    "name": tool_name,
                    "content": result.content
                })
                
                # 获取下一个LLM响应
                response = self.get_response(messages, available_tools)
                # 将新的响应添加到最终结果
                if response.choices[0].message.content:
                    final_text.append(response.choices[0].message.content)

        # 确保返回非空结果
        if not final_text:
            return "抱歉，没有得到有效的响应。"
            
        return "\n".join(final_text)

    async def chat_loop(self):
        """运行交互式聊天循环（没有记忆）"""
        print("\\nMCP Client 启动!")
        print("输入您的查询或 'quit' 退出.")
        
        while True:
            try:
                query = input("\\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    break
                    
                response = await self.process_query(query)
                print("\\n" + response)
                    
            except Exception as e:
                print(f"\\n错误: {str(e)}")

    async def api_chat(self):

        response = self.process_query(query)

    
    async def cleanup(self):
        """清理资源"""
        await self.exit_stack.aclose() 


app = FastAPI()

@app.post("/")
async def chat(request: Request):
    """处理聊天请求的API端点"""
    data = await request.json()
    query = data.get("prompt")
    
    if not query:
        return {"error": "请提供查询内容"}
        
    client = MCPClient()
    try:
        # 连接到服务器
        await client.connect_to_server(sys.argv[1])  # 需要替换为实际的服务器脚本路径
        # 处理查询
        response = await client.process_query(query)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}
    finally:
        await client.cleanup()

async def start_server():
    """启动FastAPI服务器"""
    config = uvicorn.Config(app, host="0.0.0.0", port=2048)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)
    
    asyncio.run(start_server())
