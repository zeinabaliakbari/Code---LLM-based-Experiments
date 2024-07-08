### best  english version 2  # #########################
import shutil
import fitz
import PyPDF2
import os
import re
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from PyPDF2 import PdfReader
from Crypto.Cipher import AES
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

load_dotenv()

SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = int(os.getenv('SERVER_PORT', 22))
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
English_REMOTE_DIR = os.getenv('English_REMOTE_DIR')
print(English_REMOTE_DIR)
print(f"Remote directory: {English_REMOTE_DIR}")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, SERVER_PORT, USERNAME, PASSWORD)

# Open an SFTP session
sftp = client.open_sftp()

# Debugging: List intermediate directories to verify path
current_path = '/'
for part in English_REMOTE_DIR.strip('/').split('/'):
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
    pdf_files = [file for file in sftp.listdir(English_REMOTE_DIR) if file.endswith('.pdf')]
    print(f"PDF files in remote directory: {pdf_files}")
except FileNotFoundError:
    print(f"The specified remote directory does not exist: {English_REMOTE_DIR}")
    sftp.close()
    client.close()
    exit(1)

subdirs = ['papers', 'books', 'dissertations', 'others']






#########################################################################################

def find_second_introduction(pdf_path):
    if PdfReader(input_pdf_path).is_encrypted:
      print("## This file is encrypted!  ## ")
      #shutil.copy(input_pdf_path, encrypted_dir)
      return None
    pattern = re.compile(r'\d+\.\d+\s+\w+')

    pdf_document = fitz.open(pdf_path)
    introduction_count = 0
    second_introduction_page = None
    second_introduction_text = None

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text = page.get_text()

        if "Introduction" in text:
            introduction_count += 1

            # Check if it's the second occurrence and does not have ellipses afterwards
            if introduction_count >1:
                # Split text into lines and find the line containing "Introduction"
                lines = text.splitlines()
                for line in lines:
                    if "Introduction" in line:
                        print()
                        index = line.index("Introduction")
                        line_clean = line.strip()
                        if index + len("Introduction") < len(line_clean) and  pattern.search(line_clean) :
                          #print()
                          #line_clean = line.strip()
                          print(line_clean)
                          if not any(char.isdigit() for char in line_clean[-1]):
                            second_introduction_page = page_num + 1  # page_num is 0-indexed, so +1 for human readable format
                            print(f"second_introduction_page :  {second_introduction_page }")
                            break

        if second_introduction_page is not None:
            break

    pdf_document.close()
    #second_introduction_page=second_introduction_page-1 # we dont wan
    return second_introduction_page

def find_conclusion_or_summary(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        # Start searching from the last page towards the first page
        for page_num in range(len(reader.pages) - 1, -1, -1):
            page = reader.pages[page_num]
            text = page.extract_text()

            # Split text into lines and reverse the order to search from bottom to top
            lines = reversed(text.splitlines())

            for line in lines:
                line_clean = line.strip().lower()

                # Check if the line contains 'conclusion' or 'summary' References
                if 'conclusion' in line_clean or 'summary' in line_clean or 'conclusions' in line_clean:
                #if 'References' in line_clean or 'Reference' in line_clean:
                    # Return the page number and the line containing the term
                    return page_num

    return None

def remove_pages_FromFirst(pdf_path, page_num_to_remove_before, output_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()

        # Add pages from page_num_to_remove_before onwards to the writer
        for page_num in range(page_num_to_remove_before, len(reader.pages)):
            page = reader.pages[page_num]
            writer.add_page(page)

        # Write the updated PDF to the output path
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)



def remove_pages_FromEnd(pdf_path, page_num_to_remove_after, output_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()

        # Add pages up to the page before page_num_to_remove_after to the writer
        for page_num in range(page_num_to_remove_after):
            page = reader.pages[page_num]
            writer.add_page(page)

        # Write the updated PDF to the output path
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

parent_dir= English_REMOTE_DIR 
middle_Dir='/srv/public/preprocessed_pdfs_for_llm_projekt/middle_folder'
encrypted_Dir="/srv/public/preprocessed_pdfs_for_llm_projekt/encrypted_pfds"
processedDir="/srv/public/preprocessed_pdfs_for_llm_projekt/english_documents"

#for subfolder in subdirs : # uncomment this
subfolder='papers' # remove that
if subfolder!=None:    #remove that
    pdf_path= os.path.join(parent_dir, subfolder)
    for filename in os.listdir(pdf_path):
      if filename.endswith('.pdf'):
          
            input_pdf_path = os.path.join(pdf_path, filename)
            print( input_pdf_path)
            middel_path = os.path.join(middle_Dir, os.path.splitext(filename)[0] + '_introremoved.pdf')
            output_path = os.path.join(processedDir,subfolder, os.path.splitext(filename)[0] + '_processed.pdf')
            encrypted_dirpath= os.path.join(encrypted_Dir ,subfolder, os.path.splitext(filename)[0] + '_processed.pdf')
            first_intro_page = find_second_introduction(input_pdf_path)
            if first_intro_page==None:
                shutil.copy(input_pdf_path, encrypted_dirpath)
                print('this file is encrypted and saved in specific folder ')
                print(input_pdf_path)
                print('#####################')

            else :
                first_intro_page=first_intro_page-1
                remove_pages_FromFirst(input_pdf_path, first_intro_page, middel_path)
                print(f"Pages removed successfully from the beginning up to page {first_intro_page}.")
                print(f"Updated PDF saved to '{middel_path}'.")
                #Summery_page=find_conclusion_or_summary(middel_path)
                first_conclusion_summary_page = find_conclusion_or_summary(middel_path)
                print(f"Updated PDF saved to '{middel_path}'.")
                if first_conclusion_summary_page:
                    
                    print(f"first_conclusion_summary_page {first_conclusion_summary_page}.")

                    remove_pages_FromEnd(middel_path, first_conclusion_summary_page, output_path)
                    print(f"Pages removed successfully from page {first_conclusion_summary_page} onwards.")
                else:
                    print( "we can not find summery")
                    shutil.copy(middel_path, output_path)










