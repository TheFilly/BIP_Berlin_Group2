import argparse
import json
import mimetypes
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from google import genai

# INFO: Running Instructions
from google import genai

from helper.prompts import (
    TOP_CATEGORIES,
    PROMPT_CATEGORIZE,
    PROMPT_TELEPHONE,
    PROMPT_VIDEO_DEVICE,
    PROMPT_AUDIO_DEVICE,
    PROMPT_GENERIC
)
# Establish a Gemini client using the API key pulled from the environment.
def configure_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set the GEMINI_API_KEY environment variable.")
    return genai.Client(api_key=api_key)

# Read an image file and package it with MIME metadata for Gemini ingestion.
def load_image_part(path: Path) -> Dict[str, Dict[str, bytes]]:
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type is None:
        raise ValueError(f"Cannot determine MIME type for {path}")
    with path.open("rb") as stream:
        return {"inline_data": {"mime_type": mime_type, "data": stream.read()}}

# Split the flat image directory into groups keyed by the catalog item identifier.
def group_images(image_dir: Path) -> Dict[str, List[Path]]:
    groups: Dict[str, List[Path]] = defaultdict(list)
    for path in image_dir.iterdir():
        if not path.is_file():
            continue
        stem_parts = path.stem.split("-")
        if len(stem_parts) < 3:
            continue
        item_id = stem_parts[2]
        groups[item_id].append(path)
    return groups

# Send one grouped set of images to Gemini and return the predicted category labels.
def categorize_group(
    client: genai.Client, model_name: str, paths: List[Path]
) -> Dict[str, str]:
    parts = [{"text": PROMPT_CATEGORIZE}, *[load_image_part(p) for p in sorted(paths)]]
    response = client.models.generate_content(
        model=model_name,
        contents=[{"role": "user", "parts": parts}],
    )
    output_text = getattr(response, "text", "")
    if not output_text:
        raise ValueError("Model returned no text output.")
    try:
        payload = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model response is not valid JSON: {output_text}") from exc

    top_category = payload.get("top_category")
    subcategory = payload.get("subcategory")

    if not isinstance(top_category, str) or not top_category.strip():
        raise ValueError("Model response missing 'top_category'.")
    top_category = top_category.strip().lower()
    if top_category not in TOP_CATEGORIES:
        raise ValueError(
            f"Top category '{top_category}' is not in the allowed list: {TOP_CATEGORIES}."
        )

    if not isinstance(subcategory, str) or not subcategory.strip():
        raise ValueError("Model response missing 'subcategory'.")
    subcategory = subcategory.strip()

    return {"top_category": top_category, "subcategory": subcategory}

# Iterate over all image groups, categorize them, and persist the results as JSON.

def describe_group(client: genai.Client, model_name: str, prompt: str, paths: List[Path]) -> str:
    parts = [{"text": prompt}, *[load_image_part(p) for p in sorted(paths)]]
    response = client.models.generate_content(
        model=model_name,
        contents=[{"role": "user", "parts": parts}],
    )
    output_text = getattr(response, "text", "")
    if not output_text:
        raise ValueError("Model returned no text output for description.")
    return output_text.strip()

def run(image_dir: Path, output_path: Path, model_name: str) -> None:
    client = configure_client()
    print("[1] Gemini client configured.", flush=True)
    grouped = group_images(image_dir)
    # print(f"[2] Images grouped: {len(grouped)} group(s) found.", flush=True)
    for item_id, paths in grouped.items():
        print(f"[2] Sending categorization prompt for item {item_id} ...", flush=True)
        try:
            classification = categorize_group(client, model_name, paths)
            top_category = classification["top_category"]
            print(f"[3] Category received for item {item_id}: {top_category}", flush=True)
            # Prompt selection
            if top_category == "telephones":
                prompt = PROMPT_TELEPHONE
            elif top_category == "video devices":
                prompt = PROMPT_VIDEO_DEVICE
            elif top_category == "audio devices":
                prompt = PROMPT_AUDIO_DEVICE
            else:
                prompt = PROMPT_GENERIC
            print(f"[4] Sending description prompt for item {item_id} ...", flush=True)
            description = describe_group(client, model_name, prompt, paths)
            # Schöner formatieren: Item-Zeile fett, Beschreibung darunter
            print(f"<item>{item_id} ({top_category})</item>", flush=True)
            print(description, flush=True)
        except Exception as exc:
            print(f"Item {item_id}: Error - {exc}\n{'-'*40}", flush=True)

# Parse CLI arguments controlling input directory, output path, and model selection.
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Catalog museum items with Gemini vision models."
    )
    parser.add_argument(
        "--image-dir",
        type=Path,
        required=True,
        help="Directory containing item images.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("meta/catalog_results.json"),
        help="Path to write the JSON output.",
    )
    parser.add_argument(
        "--model",
        default="models/gemini-2.5-flash",
        help="Gemini vision-capable model name.",
    )
    return parser.parse_args()

# CLI entry point: parse arguments and drive the classification workflow.
def main() -> None:
    args = parse_args()
    run(args.image_dir, args.output, args.model)


if __name__ == "__main__":
    main()