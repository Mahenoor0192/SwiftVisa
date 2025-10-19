import os, re
from langchain_text_splitters import RecursiveCharacterTextSplitter

input_dir = "data/policies"
output_dir = "data/cleaned"

os.makedirs(output_dir, exist_ok=True)
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

for file in os.listdir(input_dir):
    if file.endswith(".txt"):
        text = open(os.path.join(input_dir, file), encoding="utf-8").read()
        cleaned = re.sub(r'\s+', ' ', text)
        chunks = splitter.split_text(cleaned)
        with open(os.path.join(output_dir, file), "w", encoding="utf-8") as f:
            for i, chunk in enumerate(chunks):
                f.write(f"### Chunk {i+1}\n{chunk}\n\n")
