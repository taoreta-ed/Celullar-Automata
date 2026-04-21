import fitz  # PyMuPDF
import sys

try:
    doc = fitz.open(sys.argv[1])
    text = ""
    for page in doc:
         text += page.get_text()
    with open("pdf_text.txt", "w", encoding="utf-8") as f:
         f.write(text)
    print("Extracted successfully using PyMuPDF (fitz)")
except Exception as e:
    print(f"Failed with fitz: {e}")
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(sys.argv[1])
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        with open("pdf_text.txt", "w", encoding="utf-8") as f:
             f.write(text)
        print("Extracted successfully using PyPDF2")
    except Exception as e2:
        print(f"Failed with PyPDF2: {e2}")
