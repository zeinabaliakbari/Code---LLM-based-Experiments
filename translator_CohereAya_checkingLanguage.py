import PyPDF2
import os
import re
from pathlib import Path
import shutil
from langdetect import detect
from langchain_community.llms import Ollama
#************split pdf **** based on section : bookmarks ************ self.output_directory
 
from langchain_community.llms import LlamaCpp
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import os
import tempfile
import PyPDF2
 
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import logging
from langchain_community.llms import LlamaCpp
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain import PromptTemplate
nltk.download('stopwords')
nltk.download('punkt')
class Translation_Pipeline:

    def __init__(self, file_path , splited_file_directory,translated_file_directory):
        self.original_file_path = file_path
        self.splited_file_directory = splited_file_directory # splited file will be saved here
        self.translated_file_directory = translated_file_directory
        # self.table_name = table_name
        self.bookmarks = []
        self.split_flag = False

    def extract_level_1_bookmarks(self):
        bookmarks = []

        with open(self.original_file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)

            # Get the root outline (bookmarks) object
            root = reader.outline
            print(root)
            # Extract level 1 bookmarks
            for item in root:
                if isinstance(item, dict) and '/Title' in item and '/Page' in item:
                # print( item['/Title'])
                    # Condition to check if title matches the specified pattern
                    if re.match(r'\d+\s+\w+', item['/Title']):
                        title = item['/Title']
                        page_num = None  # Initialize page number to None
                        try:
                            # Extract the actual page number from the PdfReader object
                            if title:
                                page_num = reader.get_page_number(item.page)
                        except AttributeError as e:
                            print(f"Error: {e} occurred while extracting page number for '{title}'")
                        if page_num is not None:
                            # Append only if page number extraction was successful
                            bookmarks.append((title, page_num))
                    else:
                      print("Tittle  are not match with bookmark standard")
        if len(bookmarks)>2:
            for title, page_num in bookmarks:
                print(f"Title: {title}, Page Number: {page_num}")
        else:
            
            print("there is no bookmark, the len of bookmark is : ", len(bookmarks) )
            
        return bookmarks

    def split_pdf_by_bookmarks(self):
        self.bookmarks = self.extract_level_1_bookmarks()
        if len(self.bookmarks)<2:
            # Specify the source PDF file path
            source_pdf =  self.original_file_path      
            # Specify the destination directory
            destination_directory =  self.splited_file_directory 
            # Check if the destination directory exists, if not, create it
            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)

            # Copy the PDF file to the destination directory
            shutil.copy(source_pdf, destination_directory)
            self.split_flag=True
        else:    

            with open(self.original_file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                num_pages = len(reader.pages)

                # Iterate through each bookmark (section)
                for i, (title, page) in enumerate(self.bookmarks):
                    # Extract pages for the section
                    writer = PyPDF2.PdfWriter()
                    writer.add_page(reader.pages[page])  # Page numbers are 0-indexed /getPage(page - 1)
                    if i + 1 < len(self.bookmarks):  # Check if it's not the last bookmark
                        next_page = self.bookmarks[i+1][1]
                        for j in range(page, min(next_page, num_pages)):
                            writer.add_page(reader.pages[j])
                    
                    else:
                        for j in range(page + 1, num_pages):
                            writer.add_page(reader.pages[j])        
                    # Save the section as a separate PDF Path(self.original_file_path).stem
                    pdf_filename = Path(self.original_file_path).stem
                    output_path = os.path.join( self.splited_file_directory , f"{pdf_filename}_Section_{i + 1}.pdf")
                    with open(output_path, 'wb') as out_f:
                        writer.write(out_f)
            self.split_flag=True            


    def preprocess_text(self,text):
        #text = re.sub('\s+', ' ', text)
        tokens = nltk.word_tokenize(text.lower())
        stemmer = PorterStemmer()
        stop_words = set(stopwords.words('german'))
        tokens = [stemmer.stem(token) for token in tokens if token not in stop_words]
        preprocessed_text = ' '.join(tokens)

        # Log preprocessed text
        logging.info(f"Preprocessed text: {preprocessed_text}")

        return preprocessed_text

    def Mixtral_translator(self, mytext):

        prompt = PromptTemplate(input_variables=["text"], template="you are a translator to translate {text} to english")



        # create the chat model
        llm =  Ollama(model="aya:35b", temperature=0.3)


 

        # Create the LLM chain
        chain: LLMChain = LLMChain(llm=llm, prompt=prompt)

        # make a call to the models
        prediction_msg: dict = chain.run(
            text=mytext)
        return  prediction_msg


# Translate PDF and save as text file
    def translate_pdf_to_text(self,pdf_path):
        translated_text = ''
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            pdf_filename = os.path.basename(pdf_path)  # Get the filename of the PDF
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                text = page.extract_text()
                # Preprocess text before translation
                preprocessed_text = self.preprocess_text(text)
                if preprocessed_text:  # Check if preprocessed text is not empty
                    # Split text into chunks of 5k characters
                    text_chunks = [preprocessed_text[i:i+5000] for i in range(0, len(preprocessed_text), 5000)]
                    for chunk_num, chunk in enumerate(text_chunks, start=1):
                        # Translate chunk to English
                        translated_chunk = self.Mixtral_translator(chunk)
                        translated_text += translated_chunk + '\n'
                        # Log the PDF filename and page number for each chunk
                        print(f"Processing PDF: {pdf_filename}, Page: {page_num}, Chunk: {chunk_num}")
                else:
                    print(f"Warning: Preprocessed text is empty for PDF: {pdf_filename}, Page: {page_num}.")
        return translated_text



# Translate German PDFs to English and save as text files, self.splited_file_directory,translated_file_directory
    def translate_pdfs_to_text(self):
        # Create output directory if it doesn't exist
        if not os.path.exists(self.translated_file_directory):
            os.makedirs(self.translated_file_directory)

        # Translate each PDF in the split directory
        for filename in os.listdir(self.splited_file_directory):
            if filename.endswith('.pdf'):
                input_pdf_path = os.path.join(self.splited_file_directory, filename)
                output_text_path = os.path.join(self.translated_file_directory, os.path.splitext(filename)[0] + '_translated_aya35b.txt')
                translated_text = self.translate_pdf_to_text(input_pdf_path)
                # Save translated text to a text file
                with open(output_text_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(translated_text)
                    
                    
                    
                    
                    
    def run_pipeline(self):

        self.split_pdf_by_bookmarks()

        if self.split_flag == True:
          print("look at the output directory")
          self.translate_pdfs_to_text()

def detect_language(text):
    # Detect language
    language = detect(text)
    return language

def split_pdf_and_detect_language(pdf_file):
    with open(pdf_file, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        num_pages = len(reader.pages)

        # Initialize variables
        start_page = 0
        end_page = min(50, num_pages)  # Initial end page
        # read at most 50 pages

        text = ''
        for page_num in range(start_page, end_page):
           text += reader.pages[page_num].extract_text()
        # Detect language for the current section
        language = detect_language(text)
       # Output section details
        print(f" Language: {language}")


    return language
def main():
    

    pdf_file = '/home/zeinab/Thesis_RAG_Optimization/documents/12407_154_Ruediger_Holzmann_web1.pdf'
    split_output_dir = 'Splited-Pdfs'
    translated_file_dir ='aya_translatedPDF'
    corpus_directory='corpus' 
    languages = split_pdf_and_detect_language(pdf_file)
    if languages!='en':
            pipeline = Translation_Pipeline(pdf_file, split_output_dir, translated_file_dir)
            pipeline.run_pipeline()
    else:
            if not os.path.exists(corpus_directory):
                os.makedirs(corpus_directory)

            # Copy the PDF file to the destination directory
            shutil.copy(pdf_file, corpus_directory)
                


#To do : CALL FUNCTION TO DETECT THE LANGUAGE OF THE PDF FILE 

if __name__ == "__main__":
    main()
