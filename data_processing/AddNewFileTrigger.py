import os
import re
import time
import shutil
from pathlib import Path
from io import BytesIO

import fitz
import PyPDF2
from PyPDF2 import PdfReader, PdfFileReader
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
import paramiko

load_dotenv()

# Server connection details from environment variables
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


def find_second_introduction(pdf_path):
    """
    Find the page number of the second occurrence of 'Introduction' in a PDF.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        int or None: Page number (1-indexed) of the second 'Introduction', or None if not found or encrypted.
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
                        if index + len("Introduction") < len(line) and not pattern.search(line):
                            line_clean = line.strip()
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
    Find the page number of the first occurrence of 'conclusion' or 'summary' from the end of a PDF.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        int or None: Page number (0-indexed) of the found section, or None if not found.
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

    Args:
        pdf_path (str): Path to the input PDF.
        page_num_to_remove_before (int): Number of pages to remove from the start.
        output_path (str): Path to save the output PDF.
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

    Args:
        pdf_path (str): Path to the input PDF.
        page_num_to_remove_after (int): Number of pages to keep from the start.
        output_path (str): Path to save the output PDF.
    """
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()
        for page_num in range(page_num_to_remove_after):
            page = reader.pages[page_num]
            writer.add_page(page)
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)


def run_function(file_path):
    """
    Process a new PDF file: remove introduction and conclusion/summary pages, or handle encrypted files.

    Args:
        file_path (str): Path to the new PDF file.
    """
    parent_directory = ENGLISH_REMOTE_DIR
    middle_dir = '/srv/public/preprocessed_pdfs_for_llm_projekt/middle_folder'
    encrypted_dir = "/srv/public/preprocessed_pdfs_for_llm_projekt/encrypted_pfds"
    processed_dir = "/srv/public/preprocessed_pdfs_for_llm_projekt/english_documents"

    relative_path = os.path.relpath(file_path, parent_directory)
    directory, file_name = os.path.split(relative_path)
    print(f'New file created: {file_name} in directory: {directory}')
    print(f'The complete file path: {file_path}')

    middle_path = os.path.join(middle_dir, os.path.splitext(file_name)[0] + '_introremoved.pdf')
    output_path = os.path.join(processed_dir, directory, os.path.splitext(file_name)[0] + '_processed.pdf')
    first_intro_page = find_second_introduction(file_path)

    if first_intro_page is None:
        encrypted_file_path = os.path.join(encrypted_dir, directory, os.path.splitext(file_name)[0] + 'encrypted.pdf')
        shutil.copy(file_path, encrypted_file_path)
        print('This file is encrypted and saved in a specific folder.')
        print(file_path)
        print('#####################')
    else:
        first_intro_page -= 1
        remove_pages_from_first(file_path, first_intro_page, middle_path)
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


class MyHandler(FileSystemEventHandler):
    """
    Custom event handler for monitoring new PDF files.
    """

    def on_created(self, event):
        """
        Called when a file or directory is created.

        Args:
            event: The event object containing event information.
        """
        if event.is_directory:
            return

        filepath = event.src_path
        if filepath.endswith(".pdf"):
            # Add a delay to ensure the file is completely written
            time.sleep(4)
            try:
                with open(filepath, 'rb') as f:
                    reader = PdfReader(f)
                    if len(reader.pages) == 0:
                        print(f"File {filepath} is empty.")
                    else:
                        run_function(filepath)
            except PyPDF2.errors.EmptyFileError:
                print(f"Cannot read an empty file: {filepath}")
            except PyPDF2.errors.PdfReadError as e:
                print(f"Error reading {filepath}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while reading {filepath}: {e}")


if __name__ == "__main__":
    parent_directory = ENGLISH_REMOTE_DIR
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, parent_directory, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()