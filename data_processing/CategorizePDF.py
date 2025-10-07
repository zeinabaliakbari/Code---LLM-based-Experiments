"""
This script detects whether PDF files in a remote folder are structured (with bookmarks)
or unstructured (without bookmarks), and moves them into separate directories accordingly.
"""

import os
import re
from dotenv import load_dotenv
import paramiko
import PyPDF2

load_dotenv()

SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = int(os.getenv('SERVER_PORT', 22))
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
ENGLISH_BOOK_DIR = os.getenv('Englich_Book')

print(f"Remote directory: {ENGLISH_BOOK_DIR}")

# Establish SSH and SFTP connection
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, SERVER_PORT, USERNAME, PASSWORD)
sftp = client.open_sftp()

# Verify remote directory structure
current_path = '/'
for part in ENGLISH_BOOK_DIR.strip('/').split('/'):
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
    pdf_files = [file for file in sftp.listdir(ENGLISH_BOOK_DIR) if file.lower().endswith('.pdf')]
    print(f"PDF files in remote directory: {pdf_files}")
except FileNotFoundError:
    print(f"The specified remote directory does not exist: {ENGLISH_BOOK_DIR}")
    sftp.close()
    client.close()
    exit(1)

# Ensure categorized directories exist
categorized_dirs = ['WithBookmark', 'WithoutBookmark']
for dir_name in categorized_dirs:
    dir_path = os.path.join(ENGLISH_BOOK_DIR, dir_name)
    try:
        sftp.mkdir(dir_path)
    except IOError:
        # Directory already exists
        pass

def extract_level_1_bookmarks(pdf_file_obj):
    """
    Determines if a PDF has a sufficient number of level 1 bookmarks to be considered structured.

    Args:
        pdf_file_obj: File-like object of the PDF.

    Returns:
        str: 'WithBookmark' if structured, 'WithoutBookmark' otherwise.
    """
    reader = PyPDF2.PdfReader(pdf_file_obj)
    bookmarks = []

    try:
        root = reader.outline
    except Exception as e:
        print(f"Error reading outline: {e}")
        return "WithoutBookmark"

    for item in root:
        if isinstance(item, dict) and '/Title' in item and '/Page' in item:
            if re.match(r'\d+\s+\w+', item['/Title']):
                title = item['/Title']
                try:
                    page_num = reader.get_page_number(item.page)
                    bookmarks.append((title, page_num))
                except Exception as e:
                    print(f"Error extracting page number for '{title}': {e}")
            else:
                print("Title does not match bookmark standard")
    if len(bookmarks) > 3:
        print(f"PDF is structured. Bookmarks found: {len(bookmarks)}")
        return "WithBookmark"
    else:
        print(f"No sufficient bookmarks found. Count: {len(bookmarks)}")
        return "WithoutBookmark"

def main():
    """
    Main function to categorize PDFs in the remote directory.
    """
    for pdf_file in pdf_files:
        remote_file_path = os.path.join(ENGLISH_BOOK_DIR, pdf_file)
        print(f'Processing file: {remote_file_path}')
        with sftp.open(remote_file_path, 'rb') as pdffile:
            category = extract_level_1_bookmarks(pdffile)
            destination_path = os.path.join(ENGLISH_BOOK_DIR, category, pdf_file)
            pdffile.seek(0)
            with sftp.open(destination_path, 'wb') as dest_file:
                dest_file.write(pdffile.read())
            # Optionally remove the original file after moving
            # sftp.remove(remote_file_path)

if __name__ == "__main__":
    main()