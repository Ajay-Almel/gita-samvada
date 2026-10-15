
import json
import re
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

ROOT = Path(__file__).resolve().parent.parent

INPUT_PATH = ROOT / "data" / "full_gita_combined.json"
OUTPUT_PATH = ROOT / "data" / "full_gita_chunks.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def split_long_sentence(text, max_size=1000, overlap=150):
    """Split a long sentence when it exceeds the chunk size."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_size,
        chunk_overlap=overlap,
        separators=["\n", " ", ""],
        length_function=len,
    )
    return splitter.split_text(text)


def split_purport(text, max_size=1000, overlap=150):
    """Group sentences into chunks and retain recent sentences as overlap."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    chunks = []
    current_sentences = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        # A single sentence may be longer than the chunk limit.
        if len(sentence) > max_size:
            if current_sentences:
                chunks.append(" ".join(current_sentences))
                current_sentences = []
                current_length = 0

            chunks.extend(
                split_long_sentence(sentence, max_size, overlap)
            )
            continue

        extra_length = len(sentence) + (
            1 if current_sentences else 0
        )

        if current_length + extra_length <= max_size:
            current_sentences.append(sentence)
            current_length += extra_length

        else:
            if current_sentences:
                chunks.append(" ".join(current_sentences))

            # Carry recent complete sentences into the next chunk.
            overlap_sentences = []
            overlap_length = 0

            for previous in reversed(current_sentences):
                extra = len(previous) + (
                    1 if overlap_sentences else 0
                )

                if overlap_length + extra > overlap:
                    break

                overlap_sentences.insert(0, previous)
                overlap_length += extra

            current_sentences = overlap_sentences
            current_length = overlap_length

            extra_length = len(sentence) + (
                1 if current_sentences else 0
            )

            if current_length + extra_length <= max_size:
                current_sentences.append(sentence)
                current_length += extra_length
            else:
                if current_sentences:
                    chunks.append(" ".join(current_sentences))

                current_sentences = [sentence]
                current_length = len(sentence)

    if current_sentences:
        chunks.append(" ".join(current_sentences))

    return chunks


def main():
    passages = load_json(INPUT_PATH)
    chunks = []

    for passage in passages:
        chapter = passage["chapter"]
        verse_group = passage["verse_group"]

        source_id = f"chapter_{chapter}_verses_{verse_group}"
        source = passage.get("source", {})

        # Combine all Romanized verses in this source passage.
        romanized_text = "\n".join(
            f"Verse {verse['verse_number']}:\n"
            f"{verse['transliteration']}"
            for verse in passage["romanized_verses"]
        )

        # Type 1: keep the verse and translation together.
        verse_translation_text = (
            f"BHAGAVAD GITA — CHAPTER {chapter}\n"
            f"VERSE GROUP: {verse_group}\n\n"
            f"ROMANIZED VERSE(S):\n{romanized_text}\n\n"
            f"TRANSLATION:\n{passage['translation']}"
        )

        common_metadata = {
            "chapter": chapter,
            "verse_start": passage["verse_start"],
            "verse_end": passage["verse_end"],
            "verse_group": verse_group,
            "source_document_id": source_id,
            "heading_page": source.get("heading_page", -1),
            "translation_pages": source.get(
                "translation_pages", []
            ),
            "purport_pages": source.get("purport_pages", []),
        }

        chunks.append({
            "id": f"{source_id}_verse_translation",
            "kind": "verse_translation",
            "text": verse_translation_text,
            "romanized_text": romanized_text,
            "translation": passage["translation"],
            "metadata": {
                **common_metadata,
                "kind": "verse_translation",
            },
        })

        # Type 2: split the purport only when one exists.
        purport = passage["purport"].strip()

        if purport:
            purport_parts = split_purport(
                purport,
                max_size=1000,
                overlap=150,
            )

            for number, part in enumerate(purport_parts, start=1):
                chunks.append({
                    "id": f"{source_id}_purport_{number}",
                    "kind": "purport",
                    "text": part,
                    "romanized_text": romanized_text,
                    "translation": passage["translation"],
                    "metadata": {
                        **common_metadata,
                        "kind": "purport",
                        "chunk_number": number,
                    },
                })

    save_json(chunks, OUTPUT_PATH)

    counts = {}

    for chunk in chunks:
        counts[chunk["kind"]] = (
            counts.get(chunk["kind"], 0) + 1
        )

    lengths = [len(chunk["text"]) for chunk in chunks]

    print("FULL GITA CHUNKING COMPLETE")
    print("=" * 45)
    print("Source passages:", len(passages))
    print("Record types:", counts)
    print("Total records:", len(chunks))
    print("Shortest record:", min(lengths), "characters")
    print("Longest record:", max(lengths), "characters")
    print("Saved to:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
