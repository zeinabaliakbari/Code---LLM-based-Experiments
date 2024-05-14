#pip install python-decouple  langchain torch accelerate sentence_transformers streamlit_chat streamlit faiss-cpu tiktoken huggingface-hub pypdf llama-cpp-python

import os
import tempfile
import PyPDF2
from googletrans import Translator
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import logging
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
# Initialize NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

 
#
# Set up logging
logging.basicConfig(level=logging.INFO)

# Preprocessing function
def preprocess_text(text):
    """Preprocesses text (tokenization, lowercasing, optional stemming/lemmatization, stop word removal)"""
    #text = re.sub('\s+', ' ', text)
    tokens = nltk.word_tokenize(text.lower())
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('german'))
    tokens = [stemmer.stem(token) for token in tokens if token not in stop_words]
    preprocessed_text = ' '.join(tokens)

    # Log preprocessed text
    logging.info(f"Preprocessed text: {preprocessed_text}")

    return preprocessed_text

def Mixtral_translator(mytext):

    sys_prompt: PromptTemplate = PromptTemplate(
        input_variables=["original_sentence", "desired_language"],
        template="""You are a language translater, an German speaker wants to translate/
        {original_sentence} to English. Tell him the corrent answer."""
    )

    system_message_prompt = SystemMessagePromptTemplate(prompt=sys_prompt)

    student_prompt: PromptTemplate = PromptTemplate(
        input_variables=["original_sentence"],
        template="Translate {original_sentence} to English"
    )
    student_message_prompt = HumanMessagePromptTemplate(prompt=student_prompt)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt])


   
    # create the chat model
    llm =  Ollama(model="mixtral", temperature=0.4)
 

    # Create the LLM chain
    chain: LLMChain = LLMChain(llm=llm, prompt=chat_prompt)

    # make a call to the models
    prediction_msg: dict = chain.run(
        original_sentence=mytext) 
    return  prediction_msg    
    
 
# Translate PDF and save as text file
def translate_pdf_to_text(pdf_path):
    translated_text = ''
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        pdf_filename = os.path.basename(pdf_path)  # Get the filename of the PDF
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()
            # Preprocess text before translation
            preprocessed_text = preprocess_text(text)
            if preprocessed_text:  # Check if preprocessed text is not empty
                # Split text into chunks of 5k characters
                text_chunks = [preprocessed_text[i:i+5000] for i in range(0, len(preprocessed_text), 5000)]
                for chunk_num, chunk in enumerate(text_chunks, start=1):
                    # Translate chunk to English
                    translated_chunk = Mixtral_translator(chunk)
                    translated_text += translated_chunk + '\n'
                    # Log the PDF filename and page number for each chunk
                    print(f"Processing PDF: {pdf_filename}, Page: {page_num}, Chunk: {chunk_num}")
            else:
                print(f"Warning: Preprocessed text is empty for PDF: {pdf_filename}, Page: {page_num}.")
    return translated_text



# Translate German PDFs to English and save as text files
def translate_pdfs_to_text(input_directory, output_directory):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Translate each PDF in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.pdf'):
            input_pdf_path = os.path.join(input_directory, filename)
            output_text_path = os.path.join(output_directory, os.path.splitext(filename)[0] + '_translated_r_mixtral.txt')
            #translated_text = translate_pdf_to_text(input_pdf_path)
            translated_text = ''
            with open(input_pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pdf_filename = os.path.basename(input_pdf_path)  # Get the filename of the PDF
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    text = page.extract_text()
                    # Preprocess text before translation
                    preprocessed_text = preprocess_text(text)
                    if preprocessed_text:  # Check if preprocessed text is not empty
                        # Split text into chunks of 5k characters
                        text_chunks = [preprocessed_text[i:i+5000] for i in range(0, len(preprocessed_text), 5000)]
                        for chunk_num, chunk in enumerate(text_chunks, start=1):
                            # Translate chunk to English
                            translated_chunk = Mixtral_translator(chunk)
                            with open(output_text_path, 'a', encoding='utf-8') as output_file: # append each tanslated page to final txt file 
                                
                                output_file.write(translated_chunk)
 
                           # translated_text += translated_chunk + '\n'
                            # Log the PDF filename and page number for each chunk
                            print(f"Processing PDF: {pdf_filename}, Page: {page_num}, Chunk: {chunk_num}")
                    else:
                        print(f"Warning: Preprocessed text is empty for PDF: {pdf_filename}, Page: {page_num}.")
            #return translated_text
            
            
            
            
            # Save translated text to a text file


# Example usage

def main():
    input_directory = 'ReducedGermanPdf'
    output_directory = 'ResultOfTranslation'
    translate_pdfs_to_text(input_directory, output_directory)

if __name__ == "__main__":
    main()
