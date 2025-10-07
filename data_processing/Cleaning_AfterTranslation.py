import os
import re
import nltk

def remove_invalid_words_from_files(input_directory):
    """
    Removes words not found in the NLTK English words corpus from all .txt files in the given directory.
    Writes cleaned content to new files with '_cleaned.txt' suffix.

    Args:
        input_directory (str): Path to the directory containing text files.
    """
    # Initialize the English language stopwords list from NLTK
    nltk.download('words', quiet=True)
    english_words = set(nltk.corpus.words.words())

    # Define a regular expression pattern to match valid words (only alphabetic characters)
    valid_word_pattern = re.compile(r'\b[a-zA-Z]+\b')

    # Iterate over all files in the input directory
    for filename in os.listdir(input_directory):
        # Check if the file is a text file
        if not filename.endswith(".txt"):
            continue

        input_file_path = os.path.join(input_directory, filename)
        output_file_path = os.path.join(
            input_directory, f"{os.path.splitext(filename)[0]}_cleaned.txt"
        )

        # Open the input file for reading
        with open(input_file_path, 'r', encoding='utf-8') as infile:
            # Read the content of the file
            content = infile.read()

            # Find all valid words in the text
            found_words = re.findall(valid_word_pattern, content)

            # Filter out words that are not in the English words list
            valid_words = [word for word in found_words if word.lower() in english_words]

            # Join the valid words back into a single string
            cleaned_text = ' '.join(valid_words)

        # Write the cleaned content to the output file
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            outfile.write(cleaned_text)

        print(f"Processed file: {filename}. Saved as {os.path.basename(output_file_path)}")

if __name__ == "__main__":
    input_directory = 'PythonApp/TranslatedPDFs'
    remove_invalid_words_from_files(input_directory)
