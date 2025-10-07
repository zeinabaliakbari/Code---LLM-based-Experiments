import os
import re
import shutil
import logging
from pathlib import Path
import PyPDF2
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from langdetect import detect
from langchain_community.llms import Ollama
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain import PromptTemplate

nltk.download('stopwords')
nltk.download('punkt')

class TranslationPipeline:
    def __init__(self, file_path, splited_file_directory, translated_file_directory):
        self.original_file_path = file_path
        self.splited_file_directory = splited_file_directory
        self.translated_file_directory = translated_file_directory
        self.bookmarks = []
        self.split_flag = False

    def extract_level_1_bookmarks(self):
        """
        Extracts level 1 bookmarks from the PDF.
        Returns a list of (title, page_num) tuples.
        """
        bookmarks = []
        with open(self.original_file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            root = reader.outline
            for item in root:
                if isinstance(item, dict) and '/Title' in item and '/Page' in item:
                    if re.match(r'\d+\s+\w+', item['/Title']):
                        title = item['/Title']
                        page_num = None
                        try:
                            if title:
                                page_num = reader.get_page_number(item.page)
                        except AttributeError as e:
                            print(f"Error: {e} occurred while extracting page number for '{title}'")
                        if page_num is not None:
                            bookmarks.append((title, page_num))
                    else:
                        print("Title does not match bookmark standard")
        if len(bookmarks) > 2:
            for title, page_num in bookmarks:
                print(f"Title: {title}, Page Number: {page_num}")
        else:
            print("There is no bookmark, the len of bookmark is:", len(bookmarks))
        return bookmarks

    def split_pdf_by_bookmarks(self):
        """
        Splits the PDF by bookmarks or copies the file if not enough bookmarks.
        """
        self.bookmarks = self.extract_level_1_bookmarks()
        if len(self.bookmarks) < 2:
            source_pdf = self.original_file_path
            destination_directory = self.splited_file_directory
            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)
            shutil.copy(source_pdf, destination_directory)
            self.split_flag = True
        else:
            with open(self.original_file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                num_pages = len(reader.pages)
                for i, (title, page) in enumerate(self.bookmarks):
                    writer = PyPDF2.PdfWriter()
                    writer.add_page(reader.pages[page])
                    if i + 1 < len(self.bookmarks):
                        next_page = self.bookmarks[i + 1][1]
                        for j in range(page, min(next_page, num_pages)):
                            writer.add_page(reader.pages[j])
                    else:
                        for j in range(page + 1, num_pages):
                            writer.add_page(reader.pages[j])
                    pdf_filename = Path(self.original_file_path).stem
                    output_path = os.path.join(self.splited_file_directory, f"{pdf_filename}_Section_{i + 1}.pdf")
                    with open(output_path, 'wb') as out_f:
                        writer.write(out_f)
            self.split_flag = True

    def preprocess_text(self, text):
        """
        Preprocesses text: tokenizes, stems, and removes German stopwords.
        """
        tokens = nltk.word_tokenize(text.lower())
        stemmer = PorterStemmer()
        stop_words = set(stopwords.words('german'))
        tokens = [stemmer.stem(token) for token in tokens if token not in stop_words]
        preprocessed_text = ' '.join(tokens)
        logging.info(f"Preprocessed text: {preprocessed_text}")
        return preprocessed_text

    def mixtral_translator(self, mytext):
        """
        Translates text to English using Mixtral LLM.
        """
        prompt = PromptTemplate(input_variables=["text"], template="you are a translator to translate {text} to english")
        llm = Ollama(model="mixtral", temperature=0.3)
        chain = LLMChain(llm=llm, prompt=prompt)
        prediction_msg = chain.run(text=mytext)
        return prediction_msg

    def translate_pdf_to_text(self, pdf_path):
        """
        Translates a PDF to English text, page by page.
        """
        translated_text = ''
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            pdf_filename = os.path.basename(pdf_path)
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                text = page.extract_text()
                preprocessed_text = self.preprocess_text(text)
                if preprocessed_text:
                    text_chunks = [preprocessed_text[i:i+5000] for i in range(0, len(preprocessed_text), 5000)]
                    for chunk_num, chunk in enumerate(text_chunks, start=1):
                        translated_chunk = self.mixtral_translator(chunk)
                        translated_text += translated_chunk + '\n'
                        print(f"Processing PDF: {pdf_filename}, Page: {page_num}, Chunk: {chunk_num}")
                else:
                    print(f"Warning: Preprocessed text is empty for PDF: {pdf_filename}, Page: {page_num}.")
        return translated_text

    def translate_pdfs_to_text(self):
        """
        Translates all PDFs in the split directory and saves as text files.
        """
        if not os.path.exists(self.translated_file_directory):
            os.makedirs(self.translated_file_directory)
        for filename in os.listdir(self.splited_file_directory):
            if filename.endswith('.pdf'):
                input_pdf_path = os.path.join(self.splited_file_directory, filename)
                output_text_path = os.path.join(
                    self.translated_file_directory,
                    os.path.splitext(filename)[0] + '_translated_mixtral.txt'
                )
                translated_text = self.translate_pdf_to_text(input_pdf_path)
                with open(output_text_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(translated_text)

    def run_pipeline(self):
        """
        Runs the full translation pipeline: split and translate.
        """
        self.split_pdf_by_bookmarks()
        if self.split_flag:
            print("Look at the output directory")
            self.translate_pdfs_to_text()

def detect_language(text):
    """
    Detects the language of the given text.
    """
    return detect(text)

def split_pdf_and_detect_language(pdf_file):
    """
    Reads up to 50 pages from a PDF and detects the language.
    """
    with open(pdf_file, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        num_pages = len(reader.pages)
        start_page = 0
        end_page = min(50, num_pages)
        text = ''
        for page_num in range(start_page, end_page):
            text += reader.pages[page_num].extract_text()
        language = detect_language(text)
        print(f"Language: {language}")
    return language

def main():
    pdf_file = 'documents/Roesch_PotenzialeUndStrategienZurOptimierungDesSchablonendruckprozesses.pdf'
    split_output_dir = 'Splited-Pdfs'
    translated_file_dir = 'translatedPDF'
    corpus_directory = 'corpus'
    language = split_pdf_and_detect_language(pdf_file)
    if language != 'en':
        pipeline = TranslationPipeline(pdf_file, split_output_dir, translated_file_dir)
        pipeline.run_pipeline()
    else:
        if not os.path.exists(corpus_directory):
            os.makedirs(corpus_directory)
        shutil.copy(pdf_file, corpus_directory)

if __name__ == "__main__":
    main()
