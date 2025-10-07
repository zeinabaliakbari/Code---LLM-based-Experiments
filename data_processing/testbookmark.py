"""
This script detects if PDF files inside a remote folder are structured (with bookmarks)
or unstructured, and returns unstructured and structured PDFs in separate directories.
The next step is to remove unnecessary parts manually.
"""

import os
from dotenv import load_dotenv
import paramiko
import fitz  # PyMuPDF

load_dotenv()

SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = int(os.getenv('SERVER_PORT', 22))
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
ENGLISH_BOOK = os.getenv('Englich_Book')

print(f"Remote directory: {ENGLISH_BOOK}")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, SERVER_PORT, USERNAME, PASSWORD)
sftp = client.open_sftp()

# Debug: List intermediate directories to verify path
current_path = '/'
for part in ENGLISH_BOOK.strip('/').split('/'):
    current_path = os.path.join(current_path, part)
    try:
        contents = sftp.listdir(current_path)
        print(f"Contents of {current_path}: {contents}")
    except FileNotFoundError:
        print(f"Cannot access directory: {current_path}")
        sftp.close()
        client.close()
        exit(1)

# List PDF files in the remote directory
try:
    pdf_files = [file for file in sftp.listdir(ENGLISH_BOOK) if file.lower().endswith('.pdf')]
    print(f"PDF files in remote directory: {pdf_files}")
except FileNotFoundError:
    print(f"The specified remote directory does not exist: {ENGLISH_BOOK}")
    sftp.close()
    client.close()
    exit(1)

categorized_dirs = ['WithBookmark', 'WithoutBookmark']
for dir_name in categorized_dirs:
    dir_path = os.path.join(ENGLISH_BOOK, dir_name)
    try:
        sftp.mkdir(dir_path)
    except IOError:
        # Directory already exists
        pass

def extract_level_1_bookmarks(pdf_path):
    """
    Extracts pages for level 1 bookmarks containing 'Chapter' and saves them as a new PDF.
    """
    output_pdf_path = '/srv/public/raw_pdfs_for_llm_projekt/english_documents/books/test/hadid.pdf'
    try:
        pdf_document = fitz.open(pdf_path)
        toc = pdf_document.get_toc()
        extracted_pages = [entry[2] for entry in toc if entry[0] == 1 and 'Chapter' in entry[1]]

        if not extracted_pages:
            print(f"No level 1 bookmarks with 'Chapter' found in {pdf_path}")
            pdf_document.close()
            return

        new_pdf = fitz.open()
        for page_num in extracted_pages:
            page = pdf_document.load_page(page_num)
            new_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
        new_pdf.save(output_pdf_path)
        new_pdf.close()
        pdf_document.close()
        print(f"Extracted pages saved to {output_pdf_path}")

    except Exception as e:
        print(f"Error extracting bookmarks and creating new PDF: {e}")

def main():
    for pdf_file in pdf_files:
        remote_file_path = os.path.join(ENGLISH_BOOK, pdf_file)
        print(f'Processing file: {remote_file_path}')
        with sftp.open(remote_file_path, 'rb') as pdffile:
            # Download the file to a temporary local path for processing
            temp_local_path = f"/tmp/{pdf_file}"
            with open(temp_local_path, 'wb') as local_file:
                local_file.write(pdffile.read())
            extract_level_1_bookmarks(temp_local_path)
            os.remove(temp_local_path)

if __name__ == "__main__":
    main()
