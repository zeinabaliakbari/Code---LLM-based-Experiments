import os
import re
import nltk

def remove_invalid_words_from_files(input_directory):
    # Initialize the English language stopwords list from NLTK
    nltk.download('words')
    english_words = set(nltk.corpus.words.words())

    # Define a regular expression pattern to match valid words (only alphabetic characters)
    valid_word_pattern = re.compile(r'\b[a-zA-Z]+\b')

    # Iterate over all files in the input directory
    for filename in os.listdir(input_directory):
        # Check if the file is a text file
        if filename.endswith(".txt"):
            input_file_path = os.path.join(input_directory, filename)
            output_file_path = os.path.join(input_directory, filename.split('.')[0] + '_cleaned.txt')

            # Open the input file for reading
            with open(input_file_path, 'r', encoding='utf-8') as infile:
                # Read the content of the file
                content = infile.read()

                # Find all valid words in the text
                valid_words = re.findall(valid_word_pattern, content)

                # Filter out words that are not in the English words list
                valid_words = [word.lower() for word in valid_words if word.lower() in english_words]

                # Join the valid words back into a single string
                cleaned_text = ' '.join(valid_words)

            # Write the cleaned content to the output file
            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                outfile.write(cleaned_text)

            print(f"Processed file: {filename}. Saved as {filename.split('.')[0] + '_cleaned.txt'}")

# Example usage:
input_directory = 'PythonApp/TranslatedPDFs'
remove_invalid_words_from_files(input_directory)
