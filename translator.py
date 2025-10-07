# Chat models with Prompts
# pip install python-decouple langchain

from langchain_community.llms import Ollama
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain import PromptTemplate

# Create the system and human prompt templates
sys_prompt = PromptTemplate(
    input_variables=["original_sentence", "desired_language"],
    template=(
        "You are a language translator. An English speaker wants to translate "
        "{original_sentence} to {desired_language}. Tell him the correct answer."
    )
)
system_message_prompt = SystemMessagePromptTemplate(prompt=sys_prompt)

student_prompt = PromptTemplate(
    input_variables=["original_sentence", "desired_language"],
    template="Translate {original_sentence} to {desired_language}"
)
student_message_prompt = HumanMessagePromptTemplate(prompt=student_prompt)

chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, student_message_prompt])

# Create the chat model
llm = Ollama(model="mixtral")

# Create the LLM chain
chain = LLMChain(llm=llm, prompt=chat_prompt)

if __name__ == "__main__":
    prediction_msg = chain.run(
        original_sentence="I want to create a translator!", desired_language="German"
    )
    print("#######################################")
    print(prediction_msg)
    print("#######################################")