# utils/cleaner.py
import re
from collections import Counter

def fix_hyphenation(text: str) -> str:
    # join words split by hyphen at line boundary: "warran-\nty" -> "warranty"
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    # also remove hyphen + space line splits: "exam-\n ple" -> "example"
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    return text

def normalize_whitespace(text: str) -> str:
    t = text.replace('\r\n', '\n').replace('\r', '\n')
    # collapse many blank lines to two
    t = re.sub(r'\n{3,}', '\n\n', t)
    # collapse multiple spaces / tabs
    t = re.sub(r'[ \t]{2,}', ' ', t)
    # trim trailing spaces on lines
    t = '\n'.join([ln.rstrip() for ln in t.splitlines()])
    return t.strip()

def fix_smart_quotes(text: str) -> str:
    return (text.replace('“', '"').replace('”', '"')
                .replace("’", "'").replace("‘", "'")
                .replace("—", "-").replace("–", "-"))

def remove_control_chars(text: str) -> str:
    return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', ' ', text)

def remove_repeated_headers(text: str, min_freq: int = 2) -> str:
    """
    Heuristic: find short lines that repeat across the doc (likely headers/footers)
    and remove them. min_freq = how many times a line must appear to be considered.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    counts = Counter(lines)
    # lines that appear >= min_freq and are short (<= 80 chars) are candidates
    to_remove = {ln for ln, c in counts.items() if c >= min_freq and len(ln) < 120}
    if not to_remove:
        return text
    out_lines = [ln for ln in lines if ln not in to_remove]
    return "\n".join(out_lines)

def clean_text(text: str) -> str:
    t = text
    t = fix_hyphenation(t)
    t = fix_smart_quotes(t)
    t = remove_control_chars(t)
    t = normalize_whitespace(t)
    # try to strip headers/footers heuristically
    t = remove_repeated_headers(t, min_freq=2)
    # final cleanup: remove multiple blank lines again
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip()
