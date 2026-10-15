
import json
import re
from pathlib import Path

import pymupdf


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = PROJECT_ROOT / "data" / "BhagavadGita_org.pdf"
OUTPUT_PATH = PROJECT_ROOT / "data" / "full_gita_passages.json"

# Printed PDF pages 41–903, inclusive
START_PAGE_INDEX = 39
END_PAGE_INDEX = 902

# Recognize chapter headings such as CHAPTER THIRTEEN
CHAPTER_NAMES = (
    "ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE TEN "
    "ELEVEN TWELVE THIRTEEN FOURTEEN FIFTEEN SIXTEEN "
    "SEVENTEEN EIGHTEEN"
).split()

CHAPTER_PATTERN = re.compile(
    r"CHAPTER\s+(" + "|".join(CHAPTER_NAMES) + r")\s*!?",
    re.IGNORECASE,
)

# Recognize headings such as TEXT 4, TEXTS 6–7, TEXTS 8–12
VERSE_PATTERN = re.compile(
    r"TEXTS?\s+(\d+)(?:\s*[–—-]\s*(\d+))?",
    re.IGNORECASE,
)


def add_page_if_missing(page_list, page_number):
    if page_number not in page_list:
        page_list.append(page_number)


def main():
    doc = pymupdf.open(PDF_PATH)

    records = []
    current_record = None
    current_section = None
    current_chapter = None

    chapter_numbers = {
        name: number
        for number, name in enumerate(CHAPTER_NAMES, start=1)
    }

    for page_index in range(START_PAGE_INDEX, END_PAGE_INDEX + 1):
        printed_page = page_index + 1
        page_text = doc[page_index].get_text("text")

        for raw_line in page_text.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            # Detect the beginning of a new chapter.
            chapter_match = CHAPTER_PATTERN.fullmatch(line)

            if chapter_match:
                chapter_name = chapter_match.group(1).upper()
                current_chapter = chapter_numbers[chapter_name]
                current_record = None
                current_section = None
                continue

            # Stop collecting the current purport at its end marker.
            if re.search(
                r"Thus end the Bhaktivedanta Purports to the",
                line,
                re.IGNORECASE,
            ):
                current_record = None
                current_section = None
                continue

            # Detect the beginning of a new verse or grouped verses.
            verse_match = VERSE_PATTERN.fullmatch(line)

            if verse_match:
                if current_chapter is None:
                    continue

                verse_start = int(verse_match.group(1))
                verse_end = int(verse_match.group(2) or verse_start)

                verse_group = (
                    f"{verse_start}-{verse_end}"
                    if verse_start != verse_end
                    else str(verse_start)
                )

                current_record = {
                    "chapter": current_chapter,
                    "verse_start": verse_start,
                    "verse_end": verse_end,
                    "verse_group": verse_group,
                    "heading_page": printed_page,
                    "translation": [],
                    "translation_pages": [],
                    "purport": [],
                    "purport_pages": [],
                }

                records.append(current_record)
                current_section = None
                continue

            # Identify which part of the verse is being extracted.
            if line.upper() == "TRANSLATION":
                current_section = "translation"
                continue

            if line.upper() == "PURPORT":
                current_section = "purport"
                continue

            # Ignore text outside a recognized verse section.
            if current_record is None:
                continue

            # Collect the text across pages until another heading.
            if current_section == "translation":
                current_record["translation"].append(line)
                add_page_if_missing(
                    current_record["translation_pages"],
                    printed_page,
                )

            elif current_section == "purport":
                current_record["purport"].append(line)
                add_page_if_missing(
                    current_record["purport_pages"],
                    printed_page,
                )

    doc.close()

    # Convert lists of lines into readable text.
    for record in records:
        record["translation"] = "\n".join(
            record["translation"]
        ).strip()

        record["purport"] = "\n".join(
            record["purport"]
        ).strip()

    # Save the extracted passages.
    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)

    chapters_found = sorted({
        record["chapter"] for record in records
    })

    print("FULL BHAGAVAD GITA EXTRACTION COMPLETE")
    print("=" * 50)
    print(f"Printed pages processed: 41–903")
    print(f"Passages extracted: {len(records)}")
    print(f"Chapters found: {chapters_found}")
    print(f"Output saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
