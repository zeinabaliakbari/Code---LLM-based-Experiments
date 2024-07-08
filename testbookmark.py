#########   this code detect if files inside of folder are stractured or not ,
#  and return un-stractured and stractured pdf  in separated directory
#### the next atep is remove unnecessary part manually ########
import PyPDF2
import os
import re
from pathlib import Path
import shutil

import os
from dotenv import load_dotenv
import paramiko
from PyPDF2 import PdfFileReader
from io import BytesIO
#
import fitz  # PyMuPDF
load_dotenv()

SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = int(os.getenv('SERVER_PORT', 22))
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
Englich_Book = os.getenv('Englich_Book')
print(Englich_Book)
print(f"Remote directory: {Englich_Book}")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, SERVER_PORT, USERNAME, PASSWORD)

# Open an SFTP session
sftp = client.open_sftp()

# Debugging: List intermediate directories to verify path
current_path = '/'
for part in Englich_Book.strip('/').split('/'):
    current_path = os.path.join(current_path, part)
    try:
        contents = sftp.listdir(current_path)
        print(f"Contents of {current_path}: {contents}")
    except FileNotFoundError:
        print(f"Cannot access directory: {current_path}")
        sftp.close()
        client.close()
        exit(1)

# List files in the remote directory
try:
    pdf_files = [file for file in sftp.listdir(Englich_Book) if file.endswith('.pdf')]
    print(f"PDF files in remote directory: {pdf_files}")
except FileNotFoundError:
    print(f"The specified remote directory does not exist: {Englich_Book}")
    sftp.close()
    client.close()
    exit(1)

categorized_dirs = ['WithBookmark', 'WithoutBookmark']
for dir in categorized_dirs:
    dir_path = os.path.join(Englich_Book, dir)
    try:
        sftp.mkdir(dir_path)
    except IOError:
        # Directory already exists
        pass




def extract_pdf_title(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        info = reader.metadata
        title = info.get('/Title', 'No title found')
        return title

def extract_titles_from_folder(folder_path):
    ListofFilenames=[]
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            ListofFilenames.append(pdf_path)
            #title = extract_pdf_title(pdf_path)
    print(f'List of pdfs"{ListofFilenames}"')
    return  ListofFilenames

 
def extract_level_1_bookmarks(pdf_path):
    output_pdf_path='/srv/public/raw_pdfs_for_llm_projekt/english_documents/books/test/hadid.pdf'
    try:
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)

        # Get table of contents (TOC) entries
        toc = pdf_document.get_toc()

        # Extract pages for level 1 bookmarks containing "Chapter"
        extracted_pages = []
        for entry in toc:
            level = entry[0]  # Bookmark level (nested depth)
            title = entry[1]  # Bookmark title
            page_num = entry[2]  # Page number (zero-based index)

            if level == 1 and 'Chapter' in title:
                extracted_pages.append(page_num)

        # Create a new PDF containing only the extracted pages
        new_pdf = fitz.open()
        for page_num in extracted_pages:
            page = pdf_document.load_page(page_num)
            new_pdf.insert_pdf(page)

        # Save the new PDF to the specified output path
        new_pdf.save(output_pdf_path)
        new_pdf.close()

        # Close the original PDF document
        pdf_document.close()
    
    except Exception as e:
        print(f"Error extracting bookmarks and creating new PDF: {e}")





    
def main():
    for pdf_file in pdf_files:
        remote_file_path = os.path.join(Englich_Book, pdf_file)
        print('the path of the file : '+ remote_file_path)
        with sftp.open(remote_file_path, 'rb') as pdffile:
            pdf_content = pdffile.read()
            extract_level_1_bookmarks(remote_file_path)
            #print(category)
            #destination_path = os.path.join(Englich_Book, category, pdf_file)
           # with sftp.open(destination_path, 'wb') as dest_file:
                
            #    dest_file.write(pdf_content)
            
           # sftp.remove(remote_file_path)

    



if __name__ == "__main__":
    main()
