"""Prompt slug and filename generator for Flow generations."""

import re
from pathlib import Path


def generate_prompt_filename(
    index: int,
    prompt: str,
    max_words: int = 6,
    max_slug_len: int = 40,
    style: str = "dot_space",  # "dot_space" (e.g. "1. Prompt words"), "dot_slug" (e.g. "1.Prompt_words"), "underscore" (e.g. "001_prompt_words")
    extension: str = ".png",
) -> str:
    """Generate a clean, filesystem-safe filename using prompt initial words and original index.

    Examples:
        generate_prompt_filename(1, "A cyberpunk hacker typing in neon lights")
        -> "1. A cyberpunk hacker typing.png"
    """
    # Clean whitespace and newlines
    cleaned_prompt = " ".join(prompt.split())

    # Remove illegal filename characters: < > : " / \\ | ? * and control chars
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', cleaned_prompt).strip()

    # Split into words
    words = sanitized.split()
    initial_words = words[:max_words] if words else ["image"]
    slug_text = " ".join(initial_words)

    if len(slug_text) > max_slug_len:
        slug_text = slug_text[:max_slug_len].rsplit(' ', 1)[0]
    slug_text = slug_text.strip(". ")

    if not slug_text:
        slug_text = "image"

    ext = extension if extension.startswith(".") else f".{extension}"

    if style == "dot_space":
        base_name = f"{index}. {slug_text}"
    elif style == "dot_slug":
        safe_slug = re.sub(r'\s+', '_', slug_text)
        base_name = f"{index}.{safe_slug}"
    elif style == "underscore":
        safe_slug = re.sub(r'\s+', '_', slug_text).lower()
        base_name = f"{index:03d}_{safe_slug}"
    else:
        base_name = f"{index}. {slug_text}"

    return f"{base_name}{ext}"


def get_unique_filepath(directory: Path, filename: str) -> Path:
    """Ensure filepath does not overwrite existing file by appending (1), (2) if needed."""
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / filename
    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix
    counter = 1
    while target.exists():
        target = directory / f"{stem} ({counter}){suffix}"
        counter += 1
    return target
