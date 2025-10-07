import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community import embeddings
from langchain_community.llms import Ollama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
 
from streamlit_chat import message
from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import LLMChain
from langchain import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
 
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import PyPDFLoader
import os
import sys
import tempfile
from decouple import config
from langchain_community.llms import Ollama
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.chains import RetrievalQA

def build_qa_chain(pdf_dir="pdf-German", db_dir="simpleDB", model_name="mixtral", embedding_model="sentence-transformers/all-MiniLM-L6-v2"):
    """
    Loads PDFs, creates a vector store, and builds a QA chain.
    """
    llm = Ollama(model=model_name)

    sys_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "You are an expert. Use the following pieces of context to answer the user's question.\n"
            "{context}\n"
            "question: {question}. Return correct answer."
        )
    )
    system_message_prompt = SystemMessagePromptTemplate(prompt=sys_prompt)

    student_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="use {context} and {question}"
    )
    student_message_prompt = HumanMessagePromptTemplate(prompt=student_prompt)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, student_message_prompt]
    )

    loader = PyPDFDirectoryLoader(pdf_dir)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=20)
    text_chunks = text_splitter.split_documents(data)

    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    vector_store = FAISS.from_documents(text_chunks, embedding=embeddings)
    vector_store.save_local(db_dir)

    vector_store1 = FAISS.load_local(
        db_dir,
        embeddings,
        allow_dangerous_deserialization=True
    )

    qa = RetrievalQA.from_chain_type(
        llm,
        retriever=vector_store1.as_retriever(),
        chain_type_kwargs={"prompt": chat_prompt}
    )
    return qa

def main():
    """Simple CLI for querying the QA chain."""
    qa = build_qa_chain()
    while True:
        user_input = input("Input Prompt: ")
        if user_input.lower() == 'exit':
            print('Exiting')
            sys.exit()
        if not user_input.strip():
            continue
        result = qa({'question': user_input, "query": user_input})
        print(f"Answer: {result['result']}")

if __name__ == "__main__":
    main()