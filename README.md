# LLM-based Experiments

This repository contains scripts and utilities for automating PDF processing, translation, and retrieval-augmented generation (RAG) using LLMs. The code is organized into folders by functionality for clarity and maintainability.

---

## Suggested Folder Structure

```
LLM-based-Experiments/
│
├── data_processing/              # Scripts for PDF monitoring, cleaning, categorization, 
│   ├── AddNewFileTrigger.py
│   ├── CategorizePDF.py
│   ├── Cleaning_AfterTranslation.py
│   ├── CleaningTrigger.py
│   ├── RemoveUnnecessaryPart_EN.py
│   ├── testbookmark.py
│   ├── pre-processing.py
│
├── vector_db/                   # Scripts for vector DB creation and RAG pipelines
│   ├── CreateVectorDB.py
│
│
├── rag_apps/                    # Streamlit and CLI apps for conversational retrieval
│   ├── mistral7B-app.py
│   ├── MixtralWithoutGerman.py
│   ├── testMixtral.py
│   ├── testMixtralWithGerman.py
│   ├── TestLlama3-70B.py
│   ├── StepBack.py
│   ├── RewritingQuestion.py
│
├── translation/                 # Scripts for translation pipelines and translators
│   ├── Translator_pipeline.py
│   ├── Translator_pipeline01.py
│   ├── translator.py
│   ├── Translator-Mixtral.py
│   ├── Translator-Mixtral-2.py
│   ├── Translator-GoogleTranslator.py
│   ├── Translator-Helsinki.py
│   ├── translator_checkingLanguage.py
│   ├── translator_CohereAya_checkingLanguage.py
│
├── data/                        # (Recommended) Input/output data, PDFs, and processed files
│   ├── raw_pdfs/
│   ├── processed_pdfs/
│   ├── translated_texts/
│   └── vector_db/
│
├── requirements.txt
├── .env.example
├── README.md
└── LICENSE
```

---

## Folder Descriptions

- **pdf_processing/**  
  Scripts for monitoring directories, cleaning, categorizing, and splitting PDFs.

- **vector_db/**  
  Scripts for creating and managing vector databases (e.g., FAISS) and related utilities.

- **rag_apps/**  
  Streamlit and CLI applications for conversational retrieval and RAG workflows.

- **translation/**  
  Pipelines and utilities for translating documents using various models (Mixtral, Google, Helsinki, Aya, etc.).

- **data/**  
  (Recommended) Store your input PDFs, processed files, and vector DBs here.

---

## How to Use

- Move each script into its appropriate subfolder as shown above.
- Update import paths in your scripts if necessary (use relative imports or adjust `sys.path`).
- Update your documentation and workflow to reflect the new structure.

---

*Organizing your project this way makes it easier to scale, maintain, and collaborate!*

