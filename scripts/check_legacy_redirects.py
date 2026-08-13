#!/usr/bin/env python3

import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"


def build(*args: str) -> None:
    subprocess.run(["hugo", *args], cwd=ROOT, check=True)


def refresh_target(html: str) -> str | None:
    match = re.search(
        r'<meta\s+http-equiv="refresh"\s+content="0;\s*url=([^"]+)"', html
    )
    return match.group(1) if match else None


build("--cleanDestinationDir")

posts = list((ROOT / "content" / "posts").rglob("*.md"))
punctuation_url = re.compile(r"https?://[^\s<>()]+[，。、）：]")
punctuation_matches = [
    f"{post.relative_to(ROOT)}:{line_number}"
    for post in posts
    for line_number, line in enumerate(post.read_text().splitlines(), 1)
    if punctuation_url.search(line)
]
assert not punctuation_matches, f"URLs include full-width punctuation: {punctuation_matches}"

funding_html = (PUBLIC / "posts" / "资金费率" / "index.html").read_text()
okx_href = 'href="https://www.okx.com/zh-hans/markets/index/btc-usdt"'
assert okx_href in funding_html, "rendered OKX URL is missing or malformed"
assert "%EF%BC%8C" not in funding_html, "rendered URL still includes the full-width comma"

pagination_files = sorted((PUBLIC / "posts" / "page").glob("*/index.html"))
assert pagination_files, "Hugo did not render any posts pagination pages"
pagination_targets = {
    page.relative_to(ROOT).as_posix(): refresh_target(page.read_text())
    for page in pagination_files
}
assert all(target == "https://stometa.dev/posts" for target in pagination_targets.values()), (
    f"pagination redirects do not target /posts: {pagination_targets}"
)

canonical_pairs = []
for source in ROOT.joinpath("content").rglob("*.md"):
    match = re.search(r'^canonicalURL:\s*"([^"]+)"\s*$', source.read_text(), re.MULTILINE)
    if match:
        canonical_pairs.append((source.relative_to(ROOT).as_posix(), match.group(1)))

rendered_html = [(path, path.read_text()) for path in PUBLIC.rglob("*.html")]
missing_canonicals = []
canonical_refresh_mismatches = []
for source, canonical in canonical_pairs:
    matches = [
        (path, html)
        for path, html in rendered_html
        if f'<link rel="canonical" href="{canonical}">' in html
    ]
    if not matches:
        missing_canonicals.append((source, canonical))
        continue
    for output, html in matches:
        target = refresh_target(html)
        if target != canonical:
            canonical_refresh_mismatches.append(
                (source, output.relative_to(ROOT).as_posix(), canonical, target)
            )

assert not missing_canonicals, f"explicit canonicals not rendered: {missing_canonicals}"
assert not canonical_refresh_mismatches, (
    f"canonical/refresh mismatches: {canonical_refresh_mismatches}"
)

with tempfile.TemporaryDirectory() as temp_dir:
    temp = Path(temp_dir)
    synthetic_content = temp / "content" / "posts" / "page"
    synthetic_content.mkdir(parents=True)
    synthetic_content.joinpath("99.md").write_text(
        '---\ntitle: "Synthetic pagination route"\nurl: "/posts/page/99/"\n---\n'
    )
    synthetic_public = temp / "public"
    build(
        "--contentDir",
        str(temp / "content"),
        "--destination",
        str(synthetic_public),
    )
    synthetic_html = synthetic_public.joinpath("posts/page/99/index.html").read_text()
    assert refresh_target(synthetic_html) == "https://stometa.dev/posts", (
        "the redirect partial does not map an arbitrary /posts/page/... path to /posts"
    )

print("full_width_punctuation_url_matches=0")
print("okx_href=https://www.okx.com/zh-hans/markets/index/btc-usdt")
print("encoded_full_width_comma=absent")
for page, target in pagination_targets.items():
    print(f"pagination_refresh {page}={target}")
print("pagination_refresh_mismatches=0")
print(f"explicit_canonical_frontmatter={len(canonical_pairs)}")
print(f"explicit_canonical_seen={len(canonical_pairs) - len(missing_canonicals)}")
print(f"canonical_refresh_mismatches={len(canonical_refresh_mismatches)}")
print(f"missing_explicit_canonicals={len(missing_canonicals)}")
print("synthetic_pagination_refresh=https://stometa.dev/posts")
