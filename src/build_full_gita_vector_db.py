
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

# 1. Define project paths.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "full_gita_chunks.json"

# Use a separate database directory to protect Chapter 13.
DB_PATH = PROJECT_ROOT / "chroma_db_full_gita"

# 2. Load the validated chunks.
with open(INPUT_PATH, "r", encoding="utf-8") as file:
    chunks = json.load(file)

print("Chunks loaded:", len(chunks))

if not chunks:
    raise ValueError("No chunks found. Check the input JSON file.")

# 3. Load the embedding model.
model = SentenceTransformer("all-MiniLM-L6-v2")

# 4. Create a persistent ChromaDB client.
chroma_client = chromadb.PersistentClient(path=str(DB_PATH))

# 5. Create or open a separate collection.
collection = chroma_client.get_or_create_collection(
    name="gita_full"
)

# 6. Generate embeddings and store records in batches.
batch_size = 32

for start in range(0, len(chunks), batch_size):
    batch = chunks[start:start + batch_size]

    ids = [chunk["id"] for chunk in batch]
    documents = [chunk["text"] for chunk in batch]
    metadatas = []

    for chunk in batch:
        metadata = chunk["metadata"].copy()

        # Convert page lists into JSON strings because ChromaDB
        # metadata values must be supported scalar types.
        for key in ("translation_pages", "purport_pages"):
            if key in metadata:
                metadata[key] = json.dumps(metadata[key])

        # Preserve the record type for filtering.
        metadata["kind"] = chunk["kind"]
        metadatas.append(metadata)

    # Convert each text document into a numerical vector.
    embeddings = model.encode(documents).tolist()

    # Insert new records or update existing records with the same IDs.
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(
        f"Stored records: "
        f"{min(start + batch_size, len(chunks))}/{len(chunks)}"
    )

# 7. Verify the database.
print("\nDatabase location:", DB_PATH)
print("Collection name:", collection.name)
print("Records in collection:", collection.count())

# 8. Inspect one stored record.
sample = collection.get(
    ids=[chunks[0]["id"]],
    include=["documents", "metadatas"],
)

print("\nSample record ID:", sample["ids"][0])
print("Sample metadata:", sample["metadatas"][0])
print("Sample text:", sample["documents"][0][:300])
