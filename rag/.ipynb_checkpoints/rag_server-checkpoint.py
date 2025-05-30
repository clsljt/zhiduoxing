from fastapi import FastAPI, Request
import json
import uvicorn
from langchain.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


app = FastAPI()


embeddings = HuggingFaceEmbeddings(model_name='/root/autodl-tmp/m3e-base', model_kwargs={'device': 'cuda'})
vectorstore = Chroma(persist_directory="./chroma_db/test_02", embedding_function=embeddings)
model = ChatOllama(
    model="qwen2.5:32b",
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)



RAG_TEMPLATE = """
你是“勤信智多星”，一个通过AI与流程自动化技术，构建覆盖“学生-教师-管理”三端的财务知识问答新系统

<context>
{context}
</context>

Answer the following question:

{question}"""

rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

chain = (
    RunnablePassthrough.assign(context=lambda input: format_docs(input["context"]))
    | rag_prompt
    | model
    | StrOutputParser()
)


# 处理POST请求的端点
@app.post("/")
async def create_item(request: Request):
    json_post_raw = await request.json()  # 获取POST请求的JSON数据
    json_post = json.dumps(json_post_raw)  # 将JSON数据转换为字符串
    json_post_list = json.loads(json_post)  # 将字符串转换为Python对象
    prompt = json_post_list.get('prompt')  # 获取请求中的提示

    docs = vectorstore.similarity_search(prompt)

    response = chain.invoke({"context": docs,"question": prompt})
    return {"response": response}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=1024, workers=1)