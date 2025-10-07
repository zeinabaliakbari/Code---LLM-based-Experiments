import os
import PyPDF2
from transformers import MarianMTModel, MarianTokenizer

# Initialize translation model and tokenizer
model_name = "Helsinki-NLP/opus-mt-de-en"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

def translate_text(text):
    """
    Translates German text to English using Helsinki-NLP MarianMT.
    """
    if not text:
        return ""
    inputs = tokenizer.prepare_seq2seq_batch([text], return_tensors="pt")
    translated = model.generate(**inputs)
    translated_text = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
    return translated_text

def split_pdf_and_translate(pdf_path):
    """
    Extracts text from each page of a PDF and translates it to English.
    Returns the concatenated translated text.
    """
    translated_text = ''
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()
            if text:
                translated_text += translate_text(text) + "\n"
            else:
                print(f"Warning: No text found on page {page_num} of {pdf_path}")
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
                os.path.splitext(filename)[0] + '_translated_Helsinki.txt'
            )
            translated_text = split_pdf_and_translate(input_pdf_path)
            with open(output_text_path, 'w', encoding='utf-8') as output_file:
                output_file.write(translated_text)

def main():
    input_directory = 'documents'
    output_directory = 'TranslatedPDFs'
    translate_pdfs_to_text(input_directory, output_directory)

if __name__ == "__main__":
    main()
