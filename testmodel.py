import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community import embeddings
from langchain_community.llms import Ollama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter 
from streamlit_chat import message
from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import PyPDFLoader
import os
import tempfile
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
import sys
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFDirectoryLoader




llm= Ollama(model="mixtral")
loader = PyPDFDirectoryLoader("GermanStories")
data = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=20)

text_chunks = text_splitter.split_documents(data)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")    
vector_store = FAISS.from_documents(text_chunks, embedding=embeddings)
vector_store.save_local("simpleDB") # save DB in local disk

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store1=FAISS.load_local("simpleDB" , embeddings, allow_dangerous_deserialization=True) #if you want to load db from disk, --- allow_dangerous_deserialization=True ---otherwise use vector_store in the nxt cell
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vector_store1.as_retriever(search_kwargs={"k": 2})) 

while True:
  user_input = input(f"Input Prompt: ")
  if user_input == 'exit':
    print('Exiting')
    sys.exit()
  if user_input == '':
    continue
  result = qa({'query': user_input})
  print(f"Answer: {result['result']}")