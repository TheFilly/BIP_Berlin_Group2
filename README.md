# BIP Berlin Group 2 – Museum Cataloging Assistant

This project supports automatic categorization and description of museum objects based on image data using the Google Gemini Vision API. It provides a Python pipeline and a modern web interface for interactive use.

## Features
- Automatic grouping and categorization of images
- AI-based object description
- Modular prompt management (all prompts in `helper/prompts.py`)
- Webapp with live output and image preview
- Loading animation and appealing design
- Results can be saved as JSON in the `meta` folder

## Project Structure
```
├── helper/                # Helper functions and prompts (prompts.py)
├── meta/                  # Metadata and result files (JSON)
├── Pictures/              # Image directories
├── geminiScript.py        # Pipeline for categorization and description (imports prompts)
├── extendedPipelineGemini.py # Extended pipeline with live output (imports prompts)
├── webapp.py              # Flask webapp
├── requirements.txt       # Python dependencies
└── README.md              # This guide
```

## Setup
1. Install Python 3.10+
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set your Google Gemini API key as an environment variable:
   ```sh
   export GEMINI_API_KEY="<your_api_key>"
   ```

## Pipeline Usage
- Categorization and description:
  ```sh
  python geminiScript.py --image-dir Pictures/List2 --output meta/catalog_results-list2-cat.json
  ```
- Extended pipeline with live status:
  ```sh
  python extendedPipelineGemini.py --image-dir Pictures/List2 --output meta/catalog_results-list2-cat.json
  ```

## Webapp
1. Start the webapp:
   ```sh
   python webapp.py
   ```
2. Open in your browser: [http://localhost:5000](http://localhost:5000)
3. Select images, upload them, and start the AI analysis. Steps and the final description appear live in the interface.

## Result Files
- JSON results are stored in the `meta/` folder, e.g.:
  - `meta/catalog_results-list2-cat.json`
  - `meta/catalog_results-list3-cat.json`
  - `meta/catalog_results-list2.json`
  - `meta/catalog_results-list3.json`

## Notes
- All prompts are managed in `helper/prompts.py` and imported in the main scripts for easy modification and extension.
- The webapp displays each processing step with delay and loading animation.
- The final description is visually highlighted.
- A valid Google Gemini API key is required for usage.

---

Feel free to reach out for questions or improvements!
