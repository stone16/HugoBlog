#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


TARGET_SLUGS = {
    "/posts/cloudflare-resend-unlimited-email-setup/",
    "/posts/from-em-to-ai-agent-manager-career-reflection/",
    "/posts/openclaw-sessions-json-performance-optimization/",
}


class HomeCoverParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.current_article_class: str | None = None
        self.current_link: str | None = None
        self.current_figure: dict[str, str] | None = None
        self.matches: dict[str, dict[str, str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        if tag == "article":
            self.current_article_class = attr_map.get("class")
            self.current_link = None
            self.current_figure = None
            return
        if self.current_article_class is None:
            return
        if tag == "a" and attr_map.get("class") == "entry-link":
            self.current_link = attr_map.get("href")
            return
        if tag == "figure" and attr_map.get("class", "").startswith("entry-cover"):
            self.current_figure = attr_map

    def handle_endtag(self, tag: str) -> None:
        if tag == "article":
            if (
                self.current_link is not None
                and self.current_figure is not None
                and self.current_article_class is not None
            ):
                link_path = urlparse(self.current_link).path or self.current_link
                if link_path not in TARGET_SLUGS:
                    self.current_article_class = None
                    self.current_link = None
                    self.current_figure = None
                    return
                self.matches[link_path] = {
                    "article_class": self.current_article_class,
                    "figure_class": self.current_figure.get("class", ""),
                    "cover_render": self.current_figure.get("data-cover-render", ""),
                    "cover_kind": self.current_figure.get("data-cover-kind", ""),
                }
            self.current_article_class = None
            self.current_link = None
            self.current_figure = None


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="hugo-cover-check-") as tmpdir:
        subprocess.run(
            [
                "hugo",
                "--source",
                str(repo_root),
                "--destination",
                tmpdir,
                "--environment",
                "production",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        homepage = Path(tmpdir) / "index.html"
        parser = HomeCoverParser()
        parser.feed(homepage.read_text(encoding="utf-8"))

    missing = TARGET_SLUGS.difference(parser.matches)
    if missing:
        raise SystemExit(f"Missing homepage entries for: {sorted(missing)}")

    bad = {
        slug: attrs
        for slug, attrs in parser.matches.items()
        if attrs["cover_render"] != "contain"
        or attrs["cover_kind"] != "generated-card"
        or "entry-cover--contain" not in attrs["figure_class"]
    }
    if bad:
        raise SystemExit(f"Unexpected cover attributes: {bad}")

    for slug in sorted(parser.matches):
        attrs = parser.matches[slug]
        print(
            f"{slug}\t{attrs['article_class']}\t{attrs['figure_class']}\t"
            f"{attrs['cover_render']}\t{attrs['cover_kind']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
