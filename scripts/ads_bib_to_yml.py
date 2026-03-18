#!/usr/bin/env python3
"""
ads_bib_to_yml.py
-----------------
Convert a BibTeX file exported from NASA ADS into _data/publications.yml.

Usage
-----
    python scripts/ads_bib_to_yml.py path/to/library.bib

The output is written (or overwritten) at:
    _data/publications.yml

Export instructions for NASA ADS
---------------------------------
1. Open your ADS library at https://ui.adsabs.harvard.edu/user/libraries
2. Select all papers (checkbox in the header row)
3. Click  Export  →  BibTeX
4. Save the downloaded file somewhere convenient, then run this script.
"""

import re
import sys
from pathlib import Path

# ── Output path (relative to repo root) ──────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_data" / "publications.yml"


# ── BibTeX parser ─────────────────────────────────────────────────────────────

def _strip_braces_and_quotes(value: str) -> str:
    """Remove outer braces/quotes and collapse internal braces."""
    value = value.strip()
    # Strip outer double-braces  {{…}}
    while value.startswith("{{") and value.endswith("}}"):
        value = value[2:-2].strip()
    # Strip outer single braces  {…}
    if value.startswith("{") and value.endswith("}"):
        value = value[1:-1].strip()
    # Strip outer quotes  "…"
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1].strip()
    # Remove any remaining LaTeX-brace wrappers around single characters/groups
    value = re.sub(r"\{([^{}]*)\}", r"\1", value)
    return value


def _parse_bibtex(text: str) -> list[dict]:
    """
    Parse BibTeX text into a list of dicts keyed by lowercase field name.
    Handles multi-line field values that ADS commonly produces.
    Also stores 'entry_type' (article, inproceedings, …) and 'cite_key'.
    """
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    entries = []

    # Match each @TYPE{key, … } block
    # We find start positions of each @entry, then carve the text between them.
    starts = [m.start() for m in re.finditer(r"@\w+\s*\{", text)]
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(text)
        block = text[start:end]

        # Header: @article{cite_key,
        header_m = re.match(r"@(\w+)\s*\{\s*([^,\n]+)\s*,", block)
        if not header_m:
            continue
        entry = {
            "entry_type": header_m.group(1).lower(),
            "cite_key": header_m.group(2).strip(),
        }

        # Fields: find  fieldname = {…}  or  fieldname = "…"  or  fieldname = bare
        # We need to handle values that span multiple lines and contain nested braces.
        body = block[header_m.end():]
        i = 0
        while i < len(body):
            # Skip whitespace / commas
            m = re.match(r"[\s,]+", body[i:])
            if m:
                i += m.end()
                continue
            # Try to match  fieldname =
            fm = re.match(r"(\w+)\s*=\s*", body[i:])
            if not fm:
                break
            field_name = fm.group(1).lower()
            i += fm.end()
            if i >= len(body):
                break
            # Read the value: brace-balanced or quoted string or bare token
            if body[i] == "{":
                # Read until matching closing brace
                depth = 0
                j = i
                while j < len(body):
                    if body[j] == "{":
                        depth += 1
                    elif body[j] == "}":
                        depth -= 1
                        if depth == 0:
                            j += 1
                            break
                    j += 1
                raw_value = body[i:j]
                i = j
            elif body[i] == '"':
                # Read until closing quote (ADS rarely uses this for long values)
                j = i + 1
                while j < len(body):
                    if body[j] == '"' and body[j - 1] != "\\":
                        j += 1
                        break
                    j += 1
                raw_value = body[i:j]
                i = j
            else:
                # Bare token (numbers, year, etc.)
                m2 = re.match(r"[^\s,}]+", body[i:])
                if m2:
                    raw_value = m2.group(0)
                    i += m2.end()
                else:
                    break

            entry[field_name] = _strip_braces_and_quotes(raw_value)

        entries.append(entry)

    return entries


# ── Field extraction helpers ──────────────────────────────────────────────────

def _parse_authors(author_field: str) -> list[str]:
    """
    Split ADS 'author' field on ' and ' (case-insensitive).
    Each author is kept as-is (already in "Surname, First" form from ADS).
    """
    parts = re.split(r"\s+and\s+", author_field, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]


def _extract_doi(entry: dict) -> str | None:
    """Pull DOI, stripping any leading 'https://doi.org/' prefix."""
    doi = entry.get("doi", "").strip()
    if not doi:
        return None
    doi = re.sub(r"^https?://doi\.org/", "", doi)
    return doi or None


def _extract_year(entry: dict) -> int | None:
    raw = entry.get("year", "").strip()
    if re.fullmatch(r"\d{4}", raw):
        return int(raw)
    return None


# ── YAML serialization (no external deps) ────────────────────────────────────

def _yaml_str(value: str, indent: int = 0) -> str:
    """
    Return a safely quoted YAML scalar for a string value.
    Uses double-quote style if the string contains special characters.
    """
    needs_quotes = any(c in value for c in ':#{}[]|>&*!,?@`\'"') or value.startswith(" ") or value.endswith(" ")
    prefix = " " * indent
    if needs_quotes:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'{prefix}"{escaped}"'
    return f"{prefix}{value}"


def entry_to_yml_block(entry: dict) -> str:
    lines = []

    year = _extract_year(entry)
    title = entry.get("title", "").replace("\n", " ").strip()
    doi = _extract_doi(entry)
    journal = entry.get("journal", "").strip()
    volume = entry.get("volume", "").strip()
    number = entry.get("number", "").strip()
    pages = entry.get("pages", "").strip()
    abstract = entry.get("abstract", "").replace("\n", " ").strip()
    authors = _parse_authors(entry.get("author", "")) if "author" in entry else []

    if not title:
        return ""  # skip malformed entries

    lines.append(f"- year: {year if year else 'null'}")
    lines.append(f"  title: {_yaml_str(title)}")

    if doi:
        lines.append(f"  doi: {_yaml_str(doi)}")

    if authors:
        lines.append("  authors:")
        for a in authors:
            lines.append(f"    - {_yaml_str(a)}")

    if journal:
        lines.append(f"  journal: {_yaml_str(journal)}")
    if volume:
        lines.append(f"  volume: {_yaml_str(volume)}")
    if number:
        lines.append(f"  issue: {_yaml_str(number)}")
    if pages:
        lines.append(f"  pages: {_yaml_str(pages)}")
    if abstract:
        # Write abstract as a block scalar to keep lines manageable
        wrapped = "    " + abstract
        lines.append(f"  abstract: |-")
        # Wrap at ~100 chars
        words = abstract.split()
        line_buf = []
        col = 0
        abs_lines = []
        for word in words:
            if col + len(word) + 1 > 100 and line_buf:
                abs_lines.append("    " + " ".join(line_buf))
                line_buf = [word]
                col = len(word)
            else:
                line_buf.append(word)
                col += len(word) + 1
        if line_buf:
            abs_lines.append("    " + " ".join(line_buf))
        lines.extend(abs_lines)

    return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────────────────────

HEADER = """\
# Related Publications — generated by scripts/ads_bib_to_yml.py
# DO NOT EDIT BY HAND if you manage this via BibTeX export.
# Fields used now:   year, title, doi
# Fields ready to display later (just uncomment in _layouts/home.html / resources.md):
#   authors (list), journal, volume, issue, pages, abstract
#
# Sort order on the page: newest first (by year, then order within year).
"""


def main(bib_path: str) -> None:
    bib_file = Path(bib_path)
    if not bib_file.exists():
        print(f"Error: file not found: {bib_file}", file=sys.stderr)
        sys.exit(1)

    text = bib_file.read_text(encoding="utf-8", errors="replace")
    entries = _parse_bibtex(text)

    if not entries:
        print("No BibTeX entries found. Check the file path and format.", file=sys.stderr)
        sys.exit(1)

    # Sort: newest first; entries without a year go last
    entries.sort(key=lambda e: _extract_year(e) or 0, reverse=True)

    blocks = []
    for entry in entries:
        block = entry_to_yml_block(entry)
        if block:
            blocks.append(block)

    output = HEADER + "\n" + "\n\n".join(blocks) + "\n"
    OUTPUT.write_text(output, encoding="utf-8")
    print(f"Written {len(blocks)} publication(s) to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {Path(__file__).name} <path/to/library.bib>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
