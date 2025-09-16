# utils/parser.py
def parse_llm_response(text: str) -> dict:
    data = {
        "title": None,
        "expiry_date": None,
        "attachments": [],
        "claimable_items": [],
        "non_claimable_items": []
    }

    lines = text.splitlines()
    current = None
    capture_description = ""

    for line in lines:
        line = line.strip()

        if line.lower().startswith("1. title"):
            data["title"] = line.split(":", 1)[-1].strip()

        elif line.lower().startswith("2. expiry"):
            data["expiry_date"] = line.split(":", 1)[-1].strip()

        elif line.lower().startswith("3. list"):
            att = line.split(":", 1)[-1].strip()
            data["attachments"] = [] if "not" in att.lower() else [att]

        elif line.lower().startswith("4. claimable"):
            current = "claimable_items"
            capture_description = line.split(":", 1)[-1].strip()
            if capture_description:
                data[current].append(capture_description)

        elif line.lower().startswith("5. non-claimable"):
            current = "non_claimable_items"
            capture_description = line.split(":", 1)[-1].strip()
            if capture_description:
                data[current].append(capture_description)

        elif current and line.startswith("-"):
            data[current].append(line.strip("- ").strip())

        elif current and line:
            # Line continuation for multi-line sentence
            data[current][-1] += " " + line.strip()

    return data
