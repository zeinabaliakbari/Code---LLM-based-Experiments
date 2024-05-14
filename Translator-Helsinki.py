import PyPDF2
from transformers import MarianMTModel, MarianTokenizer
import os

# Initialize translation model and tokenizer
model_name = "Helsinki-NLP/opus-mt-de-en"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

def translate_text(text):
    # Tokenize input text
    inputs = tokenizer.prepare_seq2seq_batch([text], return_tensors="pt")

    # Translate text
    translated = model.generate(**inputs)
    translated_text = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]

    return translated_text

def split_pdf_and_translate(pdf_path):
    # Create an output directory to save translated pages
    translated_text=''
    # Open the PDF file
    with open(pdf_path, "rb") as file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)
        
        # Iterate over each page in the PDF
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            # Extract text from the page
            text = page.extract_text()
            
            # Translate the text
            translated_text += translate_text(text)            
           
    return translated_text 

def translate_pdfs_to_text(input_directory, output_directory):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Translate each PDF in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.pdf'):
            input_pdf_path = os.path.join(input_directory, filename)
            output_text_path = os.path.join(output_directory, os.path.splitext(filename)[0] + '_translated_Helsinki.txt')
            translated_text = split_pdf_and_translate(input_pdf_path)
            # Save translated text to a text file
            with open(output_text_path, 'w', encoding='utf-8') as output_file:
                output_file.write(translated_text)
# Example usage
def main():
    input_directory = 'documents'
    output_directory = 'TranslatedPDFs'
    translate_pdfs_to_text(input_directory, output_directory)

if __name__ == "__main__":
    main()
