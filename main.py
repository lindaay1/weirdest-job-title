#!/usr/bin/env python3
"""Title press: stamp one weird job title onto the entry card.

The press holds a single job title and stamps it to /output/entry.txt
(or a path given as the first argument). Before stamping, the title is
proofed against the sealed gate: 1-60 characters of UTF-8 text, a single
line, more than whitespace.
"""

import hashlib
import os
import sys
from dataclasses import dataclass

TITLE = "Senior Vice President of Waiting for the Microwave"

LIMIT = 60


def fingerprint(text: str) -> str:
    """Short sha256 of the title, so a reviewer can pin the exact text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class JobTitle:
    text: str
    department: str = "Department of Household Appliances"

    def proof(self) -> str | None:
        """Return an error string, or None when the title passes the gate."""
        if not self.text.strip():
            return "title is blank"
        if self.text != self.text.strip():
            return "title has surrounding whitespace"
        if any(ch in self.text for ch in "\n\r"):
            return "title spans more than one line"
        if len(self.text) > LIMIT:
            return f"title is {len(self.text)} chars, over the {LIMIT} limit"
        try:
            self.text.encode("utf-8")
        except UnicodeEncodeError:
            return "title is not valid UTF-8"
        return None


class TitlePress:
    """A press that stamps a proofed title onto a card file."""

    def __init__(self, title: JobTitle) -> None:
        self.title = title

    def stamp(self, card_path: str) -> int:
        flaw = self.title.proof()
        if flaw is not None:
            print(f"press refused: {flaw}", file=sys.stderr)
            return 2
        folder = os.path.dirname(card_path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(card_path, "w", encoding="utf-8", newline="\n") as card:
            card.write(self.title.text + "\n")
        print(
            f"stamped {len(self.title.text)} chars onto {card_path} "
            f"(sha256 {fingerprint(self.title.text)})"
        )
        return 0


def main(argv: list[str]) -> int:
    if len(argv) > 1 and argv[1] == "--proof":
        title = JobTitle(TITLE)
        flaw = title.proof()
        print(
            f"{'pass' if flaw is None else 'fail: ' + flaw} "
            f"({len(title.text)} chars, sha256 {fingerprint(title.text)})"
        )
        return 0 if flaw is None else 2
    card = argv[1] if len(argv) > 1 else "/output/entry.txt"
    return TitlePress(JobTitle(TITLE)).stamp(card)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
