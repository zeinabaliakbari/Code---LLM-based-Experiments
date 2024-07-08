import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
#from dotenv import load_dotenv
import shutil
import fitz
import PyPDF2
import os
import re
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from PyPDF2 import PdfReader
from Crypto.Cipher import AES

    
    
    
def find_second_introduction( pdf_path):
        if PdfReader(pdf_path).is_encrypted:   
            print("## This file is encrypted!  ## ")
            #shutil.copy(input_pdf_path, encrypted_dir)
            return None
        pattern = re.compile(r'\d+\.\d+\s+\w+')

        pdf_document = fitz.open(pdf_path)
        introduction_count = 0
        second_introduction_page = None
        #second_introduction_text = None

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
                            index = line.index("Introduction")
                            if index + len("Introduction") < len(line) and not pattern.search(line) :
                                     
                                line_clean = line.strip()
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
    
    
          
def find_conclusion_or_summary( pdf_path):
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


def remove_pages_FromEnd( pdf_path, page_num_to_remove_after, output_path):
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
            
                        
def run_function( file_path):
        parent_directory = '/home/zeinab/testtrigger'  # C:\Users\zeina\processedDir
        middle_Dir='/home/zeinab/middel_path'
        encrypted_Dir="/home/zeinab/encrypted_Dir"
        processedDir="/home/zeinab/processedDir"
        relative_path = os.path.relpath(file_path, parent_directory)
        directory, file_name = os.path.split(relative_path)
        print(f'New file created: {file_name} in directory: {directory}')
        
        #file_path = os.path.normpath(file_path1)
        
        print(f'the compelete file path :  {file_path}') 
        
        #file_path='C:\\Users\\zeina\\testtrigger\\2\\4\\Han_Chunfen_Fall-202009.pdf'
        
        
        middel_path = os.path.join(middle_Dir, os.path.splitext(file_name)[0] + '_introremoved.pdf')
        output_path = os.path.join(processedDir, os.path.splitext(file_name)[0] + '_processed.pdf')
        first_intro_page = find_second_introduction(file_path)
        if first_intro_page==None:
            shutil.copy(file_path, encrypted_Dir) # encrypter
            print('this file is encrypted and saved in specific folder ')
            print(file_path)
            print('#####################')
        else :
            first_intro_page=first_intro_page-1
            remove_pages_FromFirst(file_path, first_intro_page, middel_path)
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
                

class MyHandler(FileSystemEventHandler):

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        if filepath.endswith(".pdf"):
            # Add a delay to ensure the file is completely written
            time.sleep(4)  # Adjust the delay as needed

            try:
                with open(filepath, 'rb') as f:
                    reader = PdfReader(f)
                    if len(reader.pages) == 0:
                        print(f"File {filepath} is empty.")
                    else:
                      #  print(f"File {filepath} has {reader.numPages} pages.")
                        # Call the Melod function after verifying the file
                        run_function(filepath)
            except PyPDF2.errors.EmptyFileError:
                print(f"Cannot read an empty file: {filepath}")
            except PyPDF2.errors.PdfReadError as e:
                print(f"Error reading {filepath}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while reading {filepath}: {e}")                
if __name__ == "__main__":
    parent_directory = '/home/zeinab/testtrigger'  # C:\Users\zeina\processedDir
    middle_Dir='/home/zeinab/middel_path'
    encrypted_Dir="/home/zeinab/encrypted_Dir"
    processedDir="/home/zeinab/processedDir"
    parent_directory = parent_directory
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
