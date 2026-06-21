import json
from pathlib import Path
from typing import Any


SOURCE_PATH = Path("data/stackoverflow_2025/20250101_to_20250103/qa_merged.jsonl")
TARGET_PATH = Path("data/processed/knowledge_units.jsonl")


def build_knowledge_unit(item: dict[str, Any]) -> dict[str, Any]:
    answers = item.get("answers", [])
    selected_answer = answers[0].get("body", "") if answers else ""
    return {
        "doc_id": f"so_{item.get('question_id')}_chunk_0",
        "question_id": item.get("question_id"),
        "answer_id": item.get("accepted_answer_id"),
        "doc_type": "question_answer_unit",
        "title": item.get("title", ""),
        "content": "\n".join(
            part for part in [item.get("question_body", ""), selected_answer] if part
        ).strip(),
        "tags": item.get("tags", []),
        "score": item.get("score", 0),
        "is_accepted": bool(item.get("accepted_answer_id")),
        "source_url": item.get("link", ""),
        "language": "en",
    }


def main() -> None:
    TARGET_PATH.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with SOURCE_PATH.open("r", encoding="utf-8-sig") as reader, TARGET_PATH.open("w", encoding="utf-8") as writer:
        for line in reader:
            if not line.strip():
                continue
            item = json.loads(line)
            writer.write(json.dumps(build_knowledge_unit(item), ensure_ascii=False) + "\n")
            count += 1
    print(f"ingested {count} knowledge units into {TARGET_PATH}")


if __name__ == "__main__":
    main()
