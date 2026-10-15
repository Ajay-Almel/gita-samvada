
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

VERSE_JSON = PROJECT_ROOT / "data" / "verse.json"
PASSAGES_JSON = PROJECT_ROOT / "data" / "full_gita_passages.json"
OUTPUT_JSON = PROJECT_ROOT / "data" / "full_gita_combined.json"


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    # Load Romanized verses and extracted PDF passages.
    all_verses = load_json(VERSE_JSON)
    passages = load_json(PASSAGES_JSON)

    # Index verses by BOTH chapter and verse number.
    # Example: (1, 1) is Chapter 1, Verse 1.
    verses_by_key = {
        (verse["chapter_number"], verse["verse_number"]): verse
        for verse in all_verses
    }

    combined_records = []
    missing_verses = []

    for passage in passages:
        chapter = passage["chapter"]
        verse_start = passage["verse_start"]
        verse_end = passage["verse_end"]

        romanized_verses = []

        # Some PDF passages contain a group of verses.
        for verse_number in range(verse_start, verse_end + 1):
            key = (chapter, verse_number)
            verse = verses_by_key.get(key)

            if verse is None:
                missing_verses.append(key)
                print(
                    f"WARNING: Chapter {chapter}, "
                    f"Verse {verse_number} not found in verse.json."
                )
                continue

            romanized_verses.append({
                "verse_number": verse_number,
                "transliteration": verse["transliteration"].strip(),
            })

        combined_records.append({
            "chapter": chapter,
            "verse_start": verse_start,
            "verse_end": verse_end,
            "verse_group": passage["verse_group"],
            "romanized_verses": romanized_verses,
            "translation": passage["translation"],
            "purport": passage["purport"],
            "source": {
                "heading_page": passage["heading_page"],
                "translation_pages": passage["translation_pages"],
                "purport_pages": passage["purport_pages"],
            },
        })

    # Save to a new file; source files remain unchanged.
    with open(OUTPUT_JSON, "w", encoding="utf-8") as file:
        json.dump(
            combined_records,
            file,
            ensure_ascii=False,
            indent=2,
        )

    total_romanized = sum(
        len(record["romanized_verses"])
        for record in combined_records
    )

    print("\nFULL GITA COMBINATION COMPLETE")
    print("=" * 45)
    print(f"Source passages: {len(passages)}")
    print(f"Combined records: {len(combined_records)}")
    print(f"Romanized verse entries linked: {total_romanized}")
    print(f"Missing verse matches: {len(missing_verses)}")
    print(f"Output saved to: {OUTPUT_JSON}")

    if combined_records:
        print("\nFirst combined record:")
        print(json.dumps(
            combined_records[0],
            ensure_ascii=False,
            indent=2,
        ))


if __name__ == "__main__":
    main()
