import os
import sys
import csv
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Prompt templates
rewrite_template = (
    "Provide a better search query to answer the given question, end the queries with '**'. "
    "Question: {x} Answer:"
)
rewrite_prompt = ChatPromptTemplate.from_template(rewrite_template)

base_template = """Answer the user's question based only on the following context:

<context>
{context}
</context>

Question: {question}
"""
base_prompt = ChatPromptTemplate.from_template(base_template)

# Model and vector store setup
llm = Ollama(model="mixtral")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = FAISS.load_local("simpleDB", embeddings, allow_dangerous_deserialization=True)

# Data storage lists
qlist = []            # Original questions
rewriteqlist = []     # Rewritten questions
contextlist = []      # Retrieved contexts

def retriever(question):
    """Retrieve relevant documents for a question."""
    myretriever = vector_store.as_retriever(k=3)
    docs = myretriever.invoke(question)
    return docs

def save_retriever(docs):
    """Save retrieved context to contextlist."""
    contextlist.append("\n\n".join(doc.page_content for doc in docs))
    return docs

def _parse(text):
    """Remove trailing '**' from rewritten query."""
    return text.rstrip("**").strip()

def save_rewriter(rewritten_question):
    """Save rewritten question to rewriteqlist."""
    rewriteqlist.append(rewritten_question)
    return rewritten_question

rewriter = rewrite_prompt | llm | StrOutputParser() | _parse

# Chains
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | base_prompt
    | llm
    | StrOutputParser()
)

rewrite_retrieve_read_chain = (
    {
        "context": {"x": RunnablePassthrough()} | rewriter | save_rewriter | retriever | save_retriever,
        "question": RunnablePassthrough(),
    }
    | base_prompt
    | llm
    | StrOutputParser()
)

def june_print(msg, res):
    print('-' * 100)
    print(msg)
    print(res)

def save_to_csv(qlist, rewriteqlist, contextlist, filename='RewriteQuestion_output.csv'):
    """Save the original, rewritten queries and contexts to a CSV file."""
    rows = zip(qlist, rewriteqlist, contextlist)
    header = ['OriginalQuery', 'RewriteQuery', 'Context']
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)
    print(f'Dataset saved to {filename}')

if __name__ == "__main__":
    while True:
        question = input("Input Prompt: ")
        if question.lower() == 'exit':
            save_to_csv(qlist, rewriteqlist, contextlist)
            print('Exiting, please look at the output CSV file')
            sys.exit()
        if not question.strip():
            continue
        qlist.append(question)
        result = rewrite_retrieve_read_chain.invoke(question)
        june_print('The result of the rewrite_retrieve_read_chain:', result)











