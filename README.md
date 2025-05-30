## 安装依赖
安装mysql，在terminal运行：
`sudo apt install -y mysql-server-8.0`

安装Ollama，在terminal运行：
`curl -fsSL https://ollama.com/install.sh | sh`

安装UV，在terminal运行：
`curl -LsSf https://astral.sh/uv/install.sh | sh`

## Ollama Server
启动Ollama，在terminal运行：
`ollama start`
运行Qwen2.5，在terminal运行：
`ollama run qwen2.5:32b`
## RAG服务
#### 1.向量数据库的建立
在相应的文件夹下放入相应文件类型的文件，之后运行
`python dataloader.py`

#### 2.运行RAG API
`python rag_server.py`
## MCP服务

#### 1. MCP环境创建
```bash
# 创建项目目录
uv init project
cd project
4.# 创建虚拟环境
uv venv
# 激活环境
source .venv/bin/activate
# 安装所需的包
# client依赖
uv add mcp anthropic python-dotenv
#server依赖
uv add "mcp[cli]" httpx
```
#### 2.运行Server,  在myServer文件夹下
`uv run main.py`

#### 3.运行Client,  在mcp client文件夹下
`uv run client.py ../myServer/main.py `

## 后端服务
运行flask后端,  在flask_project文件夹下
`python flask.py `

