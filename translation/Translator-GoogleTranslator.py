import os
import PyPDF2
from googletrans import Translator
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import logging

# Initialize NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize Google Translator
translator = Translator()

def preprocess_text(text):
    """
    Preprocesses text: tokenization, lowercasing, stemming, and stop word removal.
    """
    tokens = nltk.word_tokenize(text.lower())
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('german'))
    tokens = [stemmer.stem(token) for token in tokens if token not in stop_words]
    preprocessed_text = ' '.join(tokens)
    logging.info(f"Preprocessed text: {preprocessed_text}")
    return preprocessed_text

def translate_pdf_to_text(pdf_path):
    """
    Translates the content of a PDF file from German to English and returns the translated text.
    """
    translated_text = ''
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        pdf_filename = os.path.basename(pdf_path)
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()
            preprocessed_text = preprocess_text(text)
            if preprocessed_text:
                text_chunks = [preprocessed_text[i:i+5000] for i in range(0, len(preprocessed_text), 5000)]
                for chunk_num, chunk in enumerate(text_chunks, start=1):
                    translated_chunk = translator.translate(chunk, src='de', dest='en')
                    translated_text += translated_chunk.text + '\n'
                    print(f"Processing PDF: {pdf_filename}, Page: {page_num}, Chunk: {chunk_num}")
            else:
                print(f"Warning: Preprocessed text is empty for PDF: {pdf_filename}, Page: {page_num}.")
    return translated_text

def translate_pdfs_to_text(input_directory, output_directory):
    """
    Translates all PDF files in the input directory and saves the results as text files in the output directory.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith('.pdf'):
            input_pdf_path = os.path.join(input_directory, filename)
            output_text_path = os.path.join(
                output_directory,
                os.path.splitext(filename)[0] + '_translated2_googletranslate.txt'
            )
            translated_text = translate_pdf_to_text(input_pdf_path)
            with open(output_text_path, 'w', encoding='utf-8') as output_file:
                output_file.write(translated_text)

def main():
    input_directory = 'documents'
    output_directory = 'TranslatedPDFs'
    translate_pdfs_to_text(input_directory, output_directory)

if __name__ == "__main__":
    main()
