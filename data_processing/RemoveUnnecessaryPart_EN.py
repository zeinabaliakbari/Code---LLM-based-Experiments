### best  english version 2  # #########################
import os
import re
import shutil
import fitz
import PyPDF2
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import paramiko

# Load environment variables
load_dotenv()

SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = int(os.getenv('SERVER_PORT', 22))
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
ENGLISH_REMOTE_DIR = os.getenv('English_REMOTE_DIR')

print(f"Remote directory: {ENGLISH_REMOTE_DIR}")

# Establish SSH and SFTP connection
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, SERVER_PORT, USERNAME, PASSWORD)
sftp = client.open_sftp()

# Debug: List intermediate directories to verify path
current_path = '/'
for part in ENGLISH_REMOTE_DIR.strip('/').split('/'):
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
    pdf_files = [file for file in sftp.listdir(ENGLISH_REMOTE_DIR) if file.endswith('.pdf')]
    print(f"PDF files in remote directory: {pdf_files}")
except FileNotFoundError:
    print(f"The specified remote directory does not exist: {ENGLISH_REMOTE_DIR}")
    sftp.close()
    client.close()
    exit(1)

subdirs = ['papers', 'books', 'dissertations', 'others']

def find_second_introduction(pdf_path):
    """
    Find the page number of the second occurrence of 'Introduction' in a PDF.
    Returns the page number (1-indexed) or None if not found or encrypted.
    """
    if PdfReader(pdf_path).is_encrypted:
        print("## This file is encrypted!  ##")
        return None

    pattern = re.compile(r'\d+\.\d+\s+\w+')
    pdf_document = fitz.open(pdf_path)
    introduction_count = 0
    second_introduction_page = None

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text = page.get_text()

        if "Introduction" in text:
            introduction_count += 1
            if introduction_count > 1:
                lines = text.splitlines()
                for line in lines:
                    if "Introduction" in line:
                        index = line.index("Introduction")
                        line_clean = line.strip()
                        if index + len("Introduction") < len(line_clean) and pattern.search(line_clean):
                            print(line_clean)
                            if not any(char.isdigit() for char in line_clean[-1]):
                                second_introduction_page = page_num + 1
                                print(f"second_introduction_page :  {second_introduction_page}")
                                break
        if second_introduction_page is not None:
            break

    pdf_document.close()
    return second_introduction_page

def find_conclusion_or_summary(pdf_path):
    """
    Find the first occurrence of 'conclusion' or 'summary' from the end of a PDF.
    Returns the page number (0-indexed) or None if not found.
    """
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages) - 1, -1, -1):
            page = reader.pages[page_num]
            text = page.extract_text()
            if not text:
                continue
            lines = reversed(text.splitlines())
            for line in lines:
                line_clean = line.strip().lower()
                if 'conclusion' in line_clean or 'summary' in line_clean or 'conclusions' in line_clean:
                    return page_num
    return None

def remove_pages_from_first(pdf_path, page_num_to_remove_before, output_path):
    """
    Remove pages before a given page number from a PDF and save the result.
    """
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()
        for page_num in range(page_num_to_remove_before, len(reader.pages)):
            page = reader.pages[page_num]
            writer.add_page(page)
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

def remove_pages_from_end(pdf_path, page_num_to_remove_after, output_path):
    """
    Remove pages after a given page number from a PDF and save the result.
    """
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()
        for page_num in range(page_num_to_remove_after):
            page = reader.pages[page_num]
            writer.add_page(page)
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

parent_dir = ENGLISH_REMOTE_DIR
middle_dir = '/srv/public/preprocessed_pdfs_for_llm_projekt/middle_folder'
encrypted_dir = "/srv/public/preprocessed_pdfs_for_llm_projekt/encrypted_pfds"
processed_dir = "/srv/public/preprocessed_pdfs_for_llm_projekt/english_documents"

# Process PDFs in each subdirectory
for subfolder in subdirs:
    pdf_path = os.path.join(parent_dir, subfolder)
    if not os.path.isdir(pdf_path):
        continue
    for filename in os.listdir(pdf_path):
        if filename.endswith('.pdf'):
            input_pdf_path = os.path.join(pdf_path, filename)
            print(input_pdf_path)
            middle_path = os.path.join(middle_dir, os.path.splitext(filename)[0] + '_introremoved.pdf')
            output_path = os.path.join(processed_dir, subfolder, os.path.splitext(filename)[0] + '_processed.pdf')
            encrypted_dirpath = os.path.join(encrypted_dir, subfolder, os.path.splitext(filename)[0] + '_processed.pdf')
            first_intro_page = find_second_introduction(input_pdf_path)
            if first_intro_page is None:
                shutil.copy(input_pdf_path, encrypted_dirpath)
                print('This file is encrypted and saved in a specific folder.')
                print(input_pdf_path)
                print('#####################')
            else:
                first_intro_page -= 1
                remove_pages_from_first(input_pdf_path, first_intro_page, middle_path)
                print(f"Pages removed successfully from the beginning up to page {first_intro_page}.")
                print(f"Updated PDF saved to '{middle_path}'.")
                first_conclusion_summary_page = find_conclusion_or_summary(middle_path)
                print(f"Updated PDF saved to '{middle_path}'.")
                if first_conclusion_summary_page is not None:
                    print(f"first_conclusion_summary_page {first_conclusion_summary_page}.")
                    remove_pages_from_end(middle_path, first_conclusion_summary_page, output_path)
                    print(f"Pages removed successfully from page {first_conclusion_summary_page} onwards.")
                else:
                    print("Could not find summary or conclusion section.")
                    shutil.copy(middle_path, output_path)










