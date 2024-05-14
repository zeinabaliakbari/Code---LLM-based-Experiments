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
import tempfile
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
import sys

from langchain_community.vectorstores import FAISS
from langchain.document_loaders import PyPDFDirectoryLoader


from decouple import config

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

####################################read this ################################

### we are tesing that without mention Geman language , the model return correct answer but in English
llm= Ollama(model="mixtral")

sys_prompt: PromptTemplate = PromptTemplate(
    input_variables=["context","question" ],
    template="""You are an expert, and  speaker wants to ask you/Use the following pieces of context to answer the user's question
    {context}
    question: {question}. return corrent answer ."""
)

system_message_prompt = SystemMessagePromptTemplate(prompt=sys_prompt)

student_prompt: PromptTemplate = PromptTemplate(
    input_variables=["context", "question" ],
    template="use {context} and {question}"
)
student_message_prompt = HumanMessagePromptTemplate(prompt=student_prompt)

chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, student_message_prompt])

loader = PyPDFDirectoryLoader("pdf-German")
data = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=20)

text_chunks = text_splitter.split_documents(data)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")    
vector_store = FAISS.from_documents(text_chunks, embedding=embeddings)
vector_store.save_local("simpleDB") # save DB in local disk

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store1=FAISS.load_local("simpleDB" , embeddings, allow_dangerous_deserialization=True) #if you want to load db from disk, --- allow_dangerous_deserialization=True ---otherwise use vector_store in the nxt cell
#qa = ConversationalRetrievalChain.from_llm(llm=llm, chain_type="stuff", retriever=vector_store1.as_retriever(search_kwargs={"k": 2}) ,combine_docs_chain_kwargs={"prompt": chat_prompt}) 
qa = RetrievalQA.from_chain_type(
    llm, retriever=vector_store1.as_retriever(), chain_type_kwargs={"prompt": chat_prompt}
)
while True:
  user_input = input(f"Input Prompt: ")
  if user_input == 'exit':
    print('Exiting')
    sys.exit()
  if user_input == '':
    continue
  result = qa({'question': user_input, "query": user_input})
  print(f"Answer: {result['result']}")