######################################
from langchain_community.llms import LlamaCpp
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda
import os
import csv
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community import embeddings
from langchain_community.llms import Ollima
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter

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
from langchain_community.llms import LlamaCpp
######################################
normal_context=[]
stepback_context=[]
stepback_question=[]
qlist = []
llm =  Ollima(model="mixtral")
#####################################

def _parse(text):
    """Remove trailing '**' from step-back question."""
    return text.strip("**").strip()

def june_print(msg, res):
    print('-' * 100)
    print(msg)
    print(res)
######################################
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = FAISS.load_local("simpleDB" , embeddings, allow_dangerous_deserialization=True)
######################################
# step back section


step_back_question_template = """You are an expert at world knowledge. Your task is to step back and paraphrase a question to a more generic step-back question, which is easier to answer.\
, end \
the queries with ’**’. question: \
{question} Answer:"""
step_back_question_prompt = ChatPromptTemplate.from_template(step_back_question_template)
step_back_question_chain = step_back_question_prompt | llm | StrOutputParser() | _parse




######################################

response_prompt_template = """You are an expert of world knowledge. I am going to ask you a question. Your response should be comprehensive and not contradicted with the following context if they are relevant. Otherwise, ignore them if they are not relevant.

{normal_context}
{step_back_context}

Original Question: {question}
Answer:"""
response_prompt = ChatPromptTemplate.from_template(response_prompt_template)

#################################################################################
def retriever(question):
    """Retrieve relevant documents for a question."""
    myretriever = vector_store.as_retriever(k=2)
    docs = myretriever.invoke(question)
    return docs
 ###########################################################################
def save_retriever(docs):# to save related context
   # contextlist.append("\n\n".join(doc.page_content for doc in docs))
    return docs
#############

def _parse(text):
    return text.strip("**")


##########
#rewriter = rewrite_prompt | llm | StrOutputParser() | _parse
def save_stepback(stepbackquestion):# to save related context
    stepback_question.append(stepbackquestion)
    return stepbackquestion


def save_step_back_retriever(step_back_docs):# to save related context
    stepback_context.append("\n\n".join(doc.page_content for doc in step_back_docs))
    return step_back_docs
def save_origin_query_retriever(query_docs):# to save related context
    normal_context.append("\n\n".join(doc.page_content for doc in query_docs))
    return query_docs
########################################################################
step_back_chain = (
    {
        # Retrieve context using the normal question
        "normal_context": RunnableLambda(lambda x: x["question"]) | retriever | save_origin_query_retriever,
        # Retrieve context using the step-back question
        "step_back_context": step_back_question_chain | save_stepback | retriever | save_step_back_retriever,
        # Pass on the question
        "question": lambda x: x["question"],
    }
    | response_prompt
    |llm
    | StrOutputParser()
)
qlist=[] # original quistions 
while True:
  question = input(f"Input Prompt: ")
  if question == 'exit':
    rows = zip(qlist, stepback_question, normal_context,stepback_context)

    # Define the CSV file name
    csv_file = 'StepBack_output.csv'

    # Define the header
    header = ['OriginalQuery', 'Stepback_Query', 'normal_Context', 'Stepback_context']

    # Write the rows to the CSV file
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)  # Write the header
        writer.writerows(rows)   # Write the rows

    print(f'Dataset saved to {csv_file}')

    print('Exiting, please look at the output CSV file')
   
    print('Exiting')
    #stepback_question
    #normal_context
    #stepback_context
    sys.exit()
  if question == '':
    continue
   
  qlist.append(question)

  june_print('The result of step_back_chain:', step_back_chain.invoke({"question": question}) )



######################################

