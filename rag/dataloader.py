# Import necessary modules
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import UnstructuredExcelLoader

import os
import threading

# Define paths
pdf_dir = '/root/rag/rag_data/dataPDF'
chroma_db = './chroma_db/test_02'

# Function to create a vector database
def create_vector_db():
    embeddings = HuggingFaceEmbeddings(model_name='/root/autodl-tmp/m3e-base',
                                        model_kwargs={'device': 'cuda'})
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    # Check if the directory exists, if not, create it
    if not os.path.exists(pdf_dir):
        os.makedirs(chroma_db)
    
    # Create a DirectoryLoader instance to load PDF documents
    print('.....PDF_document_loaded.....')
    loader = DirectoryLoader(pdf_dir,
                            glob='*.pdf',
                            loader_cls=PyPDFLoader,
                            use_multithreading=True)
    document = loader.load()

    texts = text_splitter.split_documents(document)
    db = Chroma.from_documents(texts, embeddings, persist_directory=chroma_db)

    print('.....Word_document_loaded.....')
    dir_word = "/root/rag/rag_data/dataDOC/"
    word_lis = os.listdir(dir_word)
    for i in word_lis:
        try:
            loader = Docx2txtLoader(dir_word+i)
            data = loader.load()
            texts = text_splitter.split_documents(data)
            db.add_documents(documents=texts)
        except:
            print("Word error:"+i)

    
    print('.....Excel_document_loaded.....')
    dir_excel = "/root/rag/rag_data/dataEXCEL/"
    excel_list = os.listdir(dir_excel)
    for i in excel_list:
        try:
            loader = UnstructuredExcelLoader(dir_excel+i, mode="elements")
            data = loader.load()
            # texts = text_splitter.split_documents(data)
            db.add_documents(documents=texts)
        except:
            print("excel error:"+i)

if __name__ == "__main__":
    # Create a new thread to execute the function
    document_thread = threading.Thread(target=create_vector_db)
    document_thread.start()
    document_thread.join()