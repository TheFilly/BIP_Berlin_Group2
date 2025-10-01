import argparse
import json
import mimetypes
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from google import genai

# TODO: Implement Top Categorization and Subcategorization; Edit Prompt accordingly
PROMPT = (
    "You are a museum cataloging assistant. "
    "Review the provided image group of one item and answer with a single concise category, "
    "such as 'rotary phone', 'hairdryer', etc. Avoid extra text."
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

# Send one grouped set of images to Gemini and return the predicted category label.
def categorize_group(
    client: genai.Client, model_name: str, paths: List[Path]
) -> str:
    parts = [{"text": PROMPT}, *[load_image_part(p) for p in sorted(paths)]]
    response = client.models.generate_content(
        model=model_name,
        contents=[{"role": "user", "parts": parts}],
    )
    output_text = getattr(response, "text", "")
    if not output_text:
        raise ValueError("Model returned no text output.")
    return output_text.strip()

# Iterate over all image groups, categorize them, and persist the results as JSON.
def run(image_dir: Path, output_path: Path, model_name: str) -> None:
    client = configure_client()
    grouped = group_images(image_dir)
    results = []
    for item_id, paths in grouped.items():
        try:
            category = categorize_group(client, model_name, paths)
        except Exception as exc:
            category = f"ERROR: {exc}"
        results.append(
            {
                "item_id": item_id,
                "file_count": len(paths),
                "files": [p.name for p in paths],
                "category": category,
            }
        )
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

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
        default=Path("catalog_results.json"),
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