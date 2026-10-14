#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pybtex>=0.24", "pyyaml>=6"]
# ///
"""Update the publication lists in README.md from my website's data.

The website (https://espositoandrea.github.io) is the single source of truth:
- featured publications come from `_data/highlights.yml`;
- journal articles come from `_bibliography/references.bib`.

Run with `uv run publications.py`. Set WEBSITE_DIR to read a local checkout of
the website instead of downloading the files from GitHub.
"""

import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

import yaml
from pybtex.database import parse_string
from pybtex.richtext import Text

SITE = "https://espositoandrea.github.io"
RAW = "https://raw.githubusercontent.com/espositoandrea/espositoandrea.github.io/main"
README = Path(__file__).with_name("README.md")
ME = ("Esposito", "Andrea")
JOURNAL_ARTICLES = 10
MONTHS = {m: i for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}


def fetch(path):
    if local := os.environ.get("WEBSITE_DIR"):
        return Path(local, path).read_text(encoding="utf-8")
    with urllib.request.urlopen(f"{RAW}/{path}") as response:
        return response.read().decode("utf-8")


def latex_to_text(value):
    text = Text.from_latex(value).render_as("text")
    return re.sub(r"\s+", " ", text.replace("---", "—").replace("--", "–")).strip()


def sort_key(entry):
    month = str(entry.fields.get("month", "0")).lower()[:3]
    return int(entry.fields.get("year", 0)), MONTHS.get(month, int(month) if month.isdigit() else 0)


def format_authors(entry):
    names = []
    for person in entry.persons.get("author", []):
        last = latex_to_text(" ".join(person.prelast_names + person.last_names))
        first = latex_to_text(" ".join(person.first_names + person.middle_names))
        initials = " ".join(f"{part[0]}." for part in re.split(r"[\s-]+", first) if part)
        name = f"{initials} {last}".strip()
        names.append(f"**{name}**" if (last, first) == ME else name)
    if len(names) > 6:
        names = names[:5] + ["et al."]
    if len(names) > 1 and names[-1] != "et al.":
        return ", ".join(names[:-1]) + ", and " + names[-1]
    return ", ".join(names)


def doi_badge(doi):
    label = urllib.parse.quote(doi, safe="").replace("-", "--").replace("_", "__")
    return (
        f'<a href="https://doi.org/{doi}">'
        f'<img src="https://img.shields.io/badge/DOI-{label}-cfd8dc?labelColor=black&style=flat-square" '
        f'alt="DOI: {doi}" align="right"></a>'
    )


def format_entry(key, entry, blurb=None):
    fields = entry.fields
    title = latex_to_text(fields["title"])
    venue = latex_to_text(fields.get("journal") or fields.get("booktitle") or fields.get("publisher", ""))
    year = fields.get("year", "")
    lines = [
        (doi_badge(fields["doi"]) if "doi" in fields else "")
        + f"**[{title}]({SITE}/bibliography/{key}.html)**",
        f"  {format_authors(entry).removesuffix('.')}. *{venue}*, {year}."
        if venue
        else f"  {format_authors(entry)}, {year}.",
    ]
    if blurb:
        lines.append(f"  {' '.join(blurb.split())}")
    # Two trailing spaces force a line break within the same list item.
    return "- " + "  \n".join(lines) + "\n"


def replace_section(readme, tag, content):
    pattern = re.compile(rf"(<!-- {tag}:START -->\n).*?(<!-- {tag}:END -->)", re.DOTALL)
    if not pattern.search(readme):
        raise ValueError(f"Missing {tag} markers in README.md")
    return pattern.sub(lambda m: m.group(1) + content + m.group(2), readme)


def main():
    bib = parse_string(fetch("_bibliography/references.bib"), "bibtex").entries
    highlights = yaml.safe_load(fetch("_data/highlights.yml")).get("highlights") or []

    featured = "".join(format_entry(h["paper"], bib[h["paper"]], h.get("text")) for h in highlights)
    if featured:
        featured = (
            "### ⭐ Featured Publications\n\n"
            "A few papers I'm particularly proud of, with a short note on why they matter.\n\n"
            + featured
            + "\n"
        )

    articles = sorted(
        ((key, entry) for key, entry in bib.items() if entry.type.lower() == "article"),
        key=lambda item: sort_key(item[1]),
        reverse=True,
    )[:JOURNAL_ARTICLES]
    journal = "".join(format_entry(key, entry) for key, entry in articles)

    readme = README.read_text(encoding="utf-8")
    readme = replace_section(readme, "FEATURED-PUBLICATIONS", featured)
    readme = replace_section(readme, "JOURNAL-ARTICLES", journal)
    README.write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
