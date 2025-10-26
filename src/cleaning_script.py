# import os, re
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# input_dir = "../data/policies"
# output_dir = "../data/cleaned_policies"

# os.makedirs(output_dir, exist_ok=True)
# splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

# for file in os.listdir(input_dir):
#     if file.endswith(".txt"):
#         text = open(os.path.join(input_dir, file), encoding="utf-8").read()
#         cleaned = re.sub(r'\s+', ' ', text)
#         chunks = splitter.split_text(cleaned)
#         with open(os.path.join(output_dir, file), "w", encoding="utf-8") as f:
#             for i, chunk in enumerate(chunks):
#                 f.write(f"### Chunk {i+1}\n{chunk}\n\n")


import os, re
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter

input_dir = "../data/policies"
output_dir = "../data/cleaned_policies"
os.makedirs(output_dir, exist_ok=True)

splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

for file in os.listdir(input_dir):
    if file.lower().endswith(".pdf"):
        file_path = os.path.join(input_dir, file)
        text = ""

        # Extract text from PDF
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"

        # Clean text
        cleaned = re.sub(r'\s+', ' ', text.strip())

        # Split into chunks
        chunks = splitter.split_text(cleaned)

        # Save to output folder as .txt
        out_file = os.path.join(output_dir, file.replace(".pdf", ".txt"))
        with open(out_file, "w", encoding="utf-8") as f:
            for i, chunk in enumerate(chunks):
                f.write(f"### Chunk {i+1}\n{chunk}\n\n")

print("PDF cleaning and chunking done!")
