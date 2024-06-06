from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community import embeddings
from langchain_community.llms import Ollama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter

from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings import HuggingFaceEmbeddings
import csv
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
from langchain_community.llms import LlamaCpp




rewrite_template = """Provide a better search query  \
 to answer the given question, end \
the queries with ’**’. Question: \
{x} Answer:"""
rewrite_prompt = ChatPromptTemplate.from_template(rewrite_template)




base_template = """Answer the users question based only on the following context:

<context>
{context}
</context>

Question: {question}
"""

rewriteqlist=[]
contextlist=[]


base_prompt = ChatPromptTemplate.from_template(base_template)
llm =  Ollama(model="mixtral")
model = llm
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store1=FAISS.load_local("simpleDB" , embeddings, allow_dangerous_deserialization=True)
#########
def retriever(question):
      myretriever = vector_store1.as_retriever(k=3)
      context = myretriever.invoke(question)
      return context
def save_retriever(docs):# to save related context
    contextlist.append("\n\n".join(doc.page_content for doc in docs))
    return docs
#############

def _parse(text):
    return text.strip("**")


##########
rewriter = rewrite_prompt | llm | StrOutputParser() | _parse
def save_rewriter(rewritedquestion):# to save related context
    rewriteqlist.append(rewritedquestion)
    return rewritedquestion




chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | base_prompt
    | model
    | StrOutputParser()
)

rewrite_retrieve_read_chain = (
    {
        "context": {"x": RunnablePassthrough()} | rewriter| save_rewriter | retriever | save_retriever,
        "question": RunnablePassthrough(),
    }
    | base_prompt
    | model
    | StrOutputParser()
)
def june_print(msg, res):
    print('-' * 100)
    print(msg)
    print(res)


qlist=[] # original quistions 
 #rewriteqlist
while True:
  question = input(f"Input Prompt: ")
  if question == 'exit':
    rows = zip(qlist, rewriteqlist, contextlist)

    # Define the CSV file name
    csv_file = 'RewriteQuestion_output.csv'

    # Define the header
    header = ['OriginalQuery', 'RewriteQuery', 'Context']

    # Write the rows to the CSV file
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)  # Write the header
        writer.writerows(rows)   # Write the rows

    print(f'Dataset saved to {csv_file}')

    print('Exiting, please look at the output CSV file')
 
    sys.exit()
  if question == '':
    continue
  
  qlist.append(question)
 
  june_print(
    'The result of the rewrite_retrieve_read_chain:',
    rewrite_retrieve_read_chain.invoke(question)
    )











