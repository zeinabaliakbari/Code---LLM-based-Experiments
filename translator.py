#### Chat models with Prompts #### 
###  ran this commanad : pip install python-decouple
from langchain_community.llms import Ollama
from decouple import config
from langchain_community.llms import LlamaCpp
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain import PromptTemplate

# Create the first prompt template
sys_prompt: PromptTemplate = PromptTemplate(
    input_variables=["original_sentence", "desired_language"],
    template="""You are a language translater, an English speaker wants to translate/
    {original_sentence} to {desired_language}. Tell him the corrent answer."""
)

system_message_prompt = SystemMessagePromptTemplate(prompt=sys_prompt)

student_prompt: PromptTemplate = PromptTemplate(
    input_variables=["original_sentence", "desired_language"],
    template="Translate {original_sentence} to {desired_language}"
)
student_message_prompt = HumanMessagePromptTemplate(prompt=student_prompt)

chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, student_message_prompt])

# create the chat model
llm =  Ollama(model="mixtral")


# Create the LLM chain
chain: LLMChain = LLMChain(llm=llm, prompt=chat_prompt)

# make a call to the models
prediction_msg: dict = chain.run(
    original_sentence="I want to create a translator !", desired_language="German")

print("#######################################")
print(prediction_msg)
print("#######################################")