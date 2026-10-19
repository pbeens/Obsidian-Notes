"""
Build and validate the distributable ChatGPT Skill archive.
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "obsidian-notes"
SKILL_DIR = ROOT / "skill" / SKILL_NAME
DIST_DIR = ROOT / "dist"
ARCHIVE = DIST_DIR / "skill.zip"
MAX_ZIP_BYTES = 50 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 25 * 1024 * 1024


def fail(message: str) -> None:
    """
    Print an error and stop the build.
    """
    raise SystemExit(f"ERROR: {message}")


def parse_frontmatter(path: Path) -> tuple[str, str]:
    """
    Read and validate the required SKILL.md frontmatter.
    """
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        fail("SKILL.md must start with YAML frontmatter delimited by ---.")

    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip().strip('"\'')

    name = values.get("name", "")
    description = values.get("description", "")
    if not name or not description:
        fail("SKILL.md frontmatter requires name and description.")
    if name != SKILL_NAME or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        fail(f"Skill name must be lowercase kebab-case and equal {SKILL_NAME!r}.")
    if len(description) < 20:
        fail("Skill description is too short.")
    return name, description


def validate_source() -> tuple[str, str]:
    """
    Validate the source Skill before packaging.
    """
    manifest = SKILL_DIR / "SKILL.md"
    metadata = SKILL_DIR / "agents" / "openai.yaml"
    plugin_manifest = SKILL_DIR / ".codex-plugin" / "plugin.json"
    if not manifest.is_file():
        fail(f"Missing {manifest.relative_to(ROOT)}.")
    if not metadata.is_file():
        fail(f"Missing {metadata.relative_to(ROOT)}.")
    if not plugin_manifest.is_file():
        fail(f"Missing {plugin_manifest.relative_to(ROOT)}.")

    metadata_text = metadata.read_text(encoding="utf-8")
    required_metadata = (
        "interface:",
        "display_name:",
        "short_description:",
        "default_prompt:",
    )
    if any(field not in metadata_text for field in required_metadata):
        fail("agents/openai.yaml is missing required interface metadata.")

    plugin_text = plugin_manifest.read_text(encoding="utf-8")
    required_plugin_fields = ('"name"', '"version"', '"description"', '"skills"', '"interface"')
    if any(field not in plugin_text for field in required_plugin_fields):
        fail(".codex-plugin/plugin.json is missing required plugin metadata.")

    name, description = parse_frontmatter(manifest)
    body = manifest.read_text(encoding="utf-8").lower()
    placeholders = ("[add purpose here]", "[paste or write instructions here]", "provisional skill")
    if any(marker in body for marker in placeholders):
        fail("SKILL.md still contains provisional or placeholder instructions.")

    for path in SKILL_DIR.rglob("*"):
        if path.is_file() and ("__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}):
            fail(f"Development cache file found: {path.relative_to(ROOT)}")
    return name, description


def files_to_package() -> list[Path]:
    """
    Return only files needed by the distributable Skill.
    """
    files = []
    for path in sorted(SKILL_DIR.rglob("*")):
        if not path.is_file():
            continue
        if path.name == ".DS_Store" or (path.name == "README.md" and path.parent.name == "references"):
            continue
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        files.append(path)
    return files


def build_archive(files: list[Path]) -> None:
    """
    Create and validate the clean single-folder ZIP archive.
    """
    DIST_DIR.mkdir(exist_ok=True)
    if ARCHIVE.exists():
        ARCHIVE.unlink()
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            relative = path.relative_to(SKILL_DIR).as_posix()
            if relative == ".codex-plugin/plugin.json":
                archive_name = f"{SKILL_NAME}/{relative}"
            elif relative == "SKILL.md":
                archive_name = f"{SKILL_NAME}/skills/{SKILL_NAME}/SKILL.md"
            elif relative.startswith("agents/"):
                archive_name = f"{SKILL_NAME}/skills/{SKILL_NAME}/{relative}"
            elif relative.startswith("references/"):
                archive_name = f"{SKILL_NAME}/skills/{SKILL_NAME}/{relative}"
            else:
                fail(f"Unsupported package path: {relative}")
            archive.write(path, archive_name)

    if ARCHIVE.stat().st_size > MAX_ZIP_BYTES:
        fail("ZIP exceeds the 50 MB upload limit.")
    with zipfile.ZipFile(ARCHIVE) as archive:
        names = archive.namelist()
        if not names or any(not name.startswith(f"{SKILL_NAME}/") for name in names):
            fail("ZIP must contain exactly one top-level Skill folder.")
        if sum(info.file_size for info in archive.infolist()) > MAX_UNCOMPRESSED_BYTES:
            fail("Uncompressed Skill contents exceed the 25 MB limit.")
        skill_manifest = f"{SKILL_NAME}/skills/{SKILL_NAME}/SKILL.md"
        if names.count(skill_manifest) != 1:
            fail("ZIP must contain exactly one skill SKILL.md.")
        if f"{SKILL_NAME}/.codex-plugin/plugin.json" not in names:
            fail("ZIP must contain a .codex-plugin/plugin.json manifest.")
        forbidden = ("README.md", "tasks.md", "AGENTS.md", "source/", ".git/", ".DS_Store")
        if any(any(part in name for part in forbidden) for name in names):
            fail("ZIP contains repository development files.")


def main() -> int:
    """
    Build the Skill archive and report validation results.
    """
    name, _ = validate_source()
    build_archive(files_to_package())
    with zipfile.ZipFile(ARCHIVE) as archive:
        count = len(archive.namelist())
    print("Build status: success")
    print(f"Skill name: {name}")
    print(f"Archive location: {ARCHIVE.relative_to(ROOT)}")
    print(f"Archive size: {ARCHIVE.stat().st_size} bytes")
    print(f"Validation result: passed ({count} files, one top-level folder)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
