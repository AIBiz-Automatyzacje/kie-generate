#!/usr/bin/env python3
"""
Kie.ai Image Generator - Nano Banana 2 / Nano Banana Pro

Usage:
    # Generate (text → image)
    python kie_image.py generate "prompt" output.png
    python kie_image.py generate "prompt" output.png --ratio 16:9 --resolution 2K

    # Edit (image + instruction → image)
    python kie_image.py edit "change background to sunset" output.png --image input.png

    # Compose (multiple images + instruction → image)
    python kie_image.py compose "combine these in collage style" output.png --image img1.png --image img2.png

    # Remove background
    python kie_image.py remove-bg input.png output.png

Examples:
    python kie_image.py generate "futuristic city at night, neon lights" city.png
    python kie_image.py edit "add orange glow effect" result.png --image photo.png --resolution 2K
    python kie_image.py compose "style transfer: apply style from first to second" out.png --image style.png --image content.png
    python kie_image.py remove-bg photo.png photo_nobg.png
"""

import argparse
import json
import os
import sys
import time

import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env_loader import find_workspace, load_env
WORKSPACE = find_workspace(script_path=__file__)
load_env(WORKSPACE)

# Kie.ai
KIE_API_KEY = os.environ.get("KIE_API_KEY")
BASE_URL = "https://api.kie.ai/api/v1"

# ImgBB (temporary public URL hosting for reference images)
IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY")
IMGBB_EXPIRATION = 3600  # 1h TTL, Kie.ai pobiera w sekundę
IMGBB_MAX_SIZE_MB = 32

ASPECT_RATIOS = ["1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9", "auto"]
MODELS = ["nano-banana-2", "nano-banana-pro", "gpt-image-2"]
RESOLUTIONS = ["1K", "2K", "4K"]
FORMATS = ["png", "jpg"]

GPT_RATIOS = {"auto", "1:1", "5:4", "9:16", "21:9", "16:9", "4:3", "3:2", "4:5", "3:4", "2:3"}


def upload_to_imgbb(local_path: str) -> str:
    """Upload pliku do ImgBB, zwróć publiczny URL (TTL 1h). Retry 3x na 5xx/network errors."""
    if not IMGBB_API_KEY:
        raise Exception("IMGBB_API_KEY not configured in .env")

    size_mb = os.path.getsize(local_path) / (1024 * 1024)
    if size_mb > IMGBB_MAX_SIZE_MB:
        raise Exception(f"File too large: {size_mb:.1f} MB (ImgBB limit: {IMGBB_MAX_SIZE_MB} MB)")

    filename = os.path.basename(local_path)
    print(f"  Uploading {filename} to ImgBB ({size_mb:.1f} MB)...")

    last_error = None
    for attempt in range(3):
        try:
            with open(local_path, "rb") as f:
                res = requests.post(
                    "https://api.imgbb.com/1/upload",
                    data={"key": IMGBB_API_KEY, "expiration": IMGBB_EXPIRATION},
                    files={"image": f},
                    timeout=60
                )
            if res.status_code == 200:
                url = res.json()["data"]["url"]
                print(f"  Uploaded: {url}")
                return url
            if res.status_code < 500:
                raise Exception(f"ImgBB upload failed {res.status_code}: {res.text}")
            last_error = f"{res.status_code}: {res.text}"
        except requests.RequestException as e:
            last_error = str(e)

        if attempt < 2:
            backoff = 2 ** attempt
            print(f"  Upload attempt {attempt + 1} failed ({last_error}), retrying in {backoff}s...")
            time.sleep(backoff)

    raise Exception(f"ImgBB upload failed after 3 attempts: {last_error}")


def resolve_model_id(model: str, has_images: bool) -> str:
    """User-facing 'gpt-image-2' rozgałęzia się na 2 wewnętrzne ID w zależności od trybu."""
    if model == "gpt-image-2":
        return "gpt-image-2-image-to-image" if has_images else "gpt-image-2-text-to-image"
    return model


def build_task_payload(prompt: str, image_urls: list, ratio: str, resolution: str, output_format: str, model: str) -> dict:
    """Zbuduj payload — GPT Image-2 ma inny schema niż Nano Banana."""
    if model == "gpt-image-2":
        if ratio not in GPT_RATIOS:
            raise Exception(f"GPT Image-2 nie wspiera proporcji '{ratio}'. Dozwolone: {sorted(GPT_RATIOS)}")
        actual_model = resolve_model_id(model, bool(image_urls))
        input_payload = {"prompt": prompt, "aspect_ratio": ratio}
        if image_urls:
            input_payload["input_urls"] = image_urls
        return {"model": actual_model, "input": input_payload}

    return {
        "model": model,
        "input": {
            "prompt": prompt,
            "image_input": image_urls,
            "aspect_ratio": ratio,
            "resolution": resolution,
            "output_format": output_format
        }
    }


def create_task(prompt: str, image_urls: list, ratio: str, resolution: str, output_format: str, model: str = "nano-banana-2") -> str:
    """Utwórz task generacji, zwróć taskId."""
    payload = build_task_payload(prompt, image_urls, ratio, resolution, output_format, model)

    response = requests.post(
        f"{BASE_URL}/jobs/createTask",
        headers={"Authorization": f"Bearer {KIE_API_KEY}"},
        json=payload
    )

    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")

    data = response.json()
    if "data" not in data or "taskId" not in data["data"]:
        raise Exception(f"Unexpected response: {data}")

    return data["data"]["taskId"]


def poll_task(task_id: str, max_attempts: int = 120) -> dict:
    """Polluj status aż zakończony, zwróć wynik."""
    for attempt in range(max_attempts):
        time.sleep(5)

        response = requests.get(
            f"{BASE_URL}/jobs/recordInfo",
            headers={"Authorization": f"Bearer {KIE_API_KEY}"},
            params={"taskId": task_id}
        )

        if response.status_code != 200:
            raise Exception(f"Poll error {response.status_code}: {response.text}")

        data = response.json()["data"]
        state = data.get("state", "unknown")

        if state == "success":
            result_json = data.get("resultJson", "{}")
            return json.loads(result_json)
        elif state == "fail":
            raise Exception(f"Generation failed: {data.get('failMsg', 'Unknown error')}")

        print(f"[{attempt + 1}/{max_attempts}] Generating... (status: {state})")

    raise Exception(f"Timeout after {max_attempts * 5} seconds")


def download_image(url: str, output_path: str):
    """Pobierz obrazek i zapisz lokalnie."""
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Download error {response.status_code}")

    with open(output_path, 'wb') as f:
        f.write(response.content)


def create_remove_bg_task(image_url: str) -> str:
    """Utwórz task usuwania tła, zwróć taskId."""
    response = requests.post(
        f"{BASE_URL}/jobs/createTask",
        headers={"Authorization": f"Bearer {KIE_API_KEY}"},
        json={
            "model": "recraft/remove-background",
            "input": {
                "image": image_url
            }
        }
    )

    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")

    data = response.json()
    if "data" not in data or "taskId" not in data["data"]:
        raise Exception(f"Unexpected response: {data}")

    return data["data"]["taskId"]


def run_generation(prompt: str, output: str, image_urls: list, ratio: str, resolution: str, fmt: str, model: str = "nano-banana-2"):
    """Wspólna logika dla wszystkich trybów."""
    print(f"Creating task...")
    print(f"  Model: {resolve_model_id(model, bool(image_urls))}")
    print(f"  Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print(f"  Ratio: {ratio}, Resolution: {resolution}, Format: {fmt}")
    if image_urls:
        print(f"  Reference images: {len(image_urls)}")

    task_id = create_task(prompt, image_urls, ratio, resolution, fmt, model)
    print(f"  Task ID: {task_id}")

    print(f"Polling for result...")
    result = poll_task(task_id)

    if "resultUrls" not in result or not result["resultUrls"]:
        raise Exception(f"No result URLs in response: {result}")

    image_url = result["resultUrls"][0]
    print(f"Downloading image...")
    download_image(image_url, output)

    print(f"Image saved to: {output}")


def main():
    if not KIE_API_KEY:
        print("Error: KIE_API_KEY environment variable not set")
        sys.exit(1)
    if not IMGBB_API_KEY:
        print("Error: IMGBB_API_KEY environment variable not set")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Kie.ai Image Generator")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # generate subcommand
    gen = subparsers.add_parser("generate", help="Generate image from text prompt")
    gen.add_argument("prompt", help="Text prompt for image generation")
    gen.add_argument("output", help="Output file path (e.g., output.png)")
    gen.add_argument("--model", default="gpt-image-2", choices=MODELS, help="Model (default: gpt-image-2)")
    gen.add_argument("--ratio", default="1:1", choices=ASPECT_RATIOS, help="Aspect ratio (default: 1:1)")
    gen.add_argument("--resolution", default="1K", choices=RESOLUTIONS, help="Resolution (default: 1K)")
    gen.add_argument("--format", default="png", choices=FORMATS, help="Output format (default: png)")

    # edit subcommand
    edit = subparsers.add_parser("edit", help="Edit image with instruction")
    edit.add_argument("instruction", help="Edit instruction (e.g., 'change background to sunset')")
    edit.add_argument("output", help="Output file path")
    edit.add_argument("--image", required=True, help="Input image to edit")
    edit.add_argument("--model", default="gpt-image-2", choices=MODELS, help="Model (default: gpt-image-2)")
    edit.add_argument("--ratio", default="auto", choices=ASPECT_RATIOS, help="Aspect ratio (default: auto)")
    edit.add_argument("--resolution", default="1K", choices=RESOLUTIONS, help="Resolution (default: 1K)")
    edit.add_argument("--format", default="png", choices=FORMATS, help="Output format (default: png)")

    # compose subcommand
    comp = subparsers.add_parser("compose", help="Compose multiple images")
    comp.add_argument("instruction", help="Composition instruction")
    comp.add_argument("output", help="Output file path")
    comp.add_argument("--image", action="append", required=True, dest="images", help="Input images (use multiple times)")
    comp.add_argument("--model", default="gpt-image-2", choices=MODELS, help="Model (default: gpt-image-2)")
    comp.add_argument("--ratio", default="1:1", choices=ASPECT_RATIOS, help="Aspect ratio (default: 1:1)")
    comp.add_argument("--resolution", default="1K", choices=RESOLUTIONS, help="Resolution (default: 1K)")
    comp.add_argument("--format", default="png", choices=FORMATS, help="Output format (default: png)")

    # remove-bg subcommand
    rmbg = subparsers.add_parser("remove-bg", help="Remove background from image")
    rmbg.add_argument("input", help="Input image path")
    rmbg.add_argument("output", help="Output file path (PNG with transparent background)")

    args = parser.parse_args()

    if args.mode == "remove-bg":
        if not os.path.exists(args.input):
            raise Exception(f"Image not found: {args.input}")

        print(f"Removing background from: {args.input}")
        image_url = upload_to_imgbb(args.input)

        print(f"Creating remove-bg task...")
        task_id = create_remove_bg_task(image_url)
        print(f"  Task ID: {task_id}")

        print(f"Polling for result...")
        result = poll_task(task_id)

        if "resultUrls" not in result or not result["resultUrls"]:
            raise Exception(f"No result URLs in response: {result}")

        print(f"Downloading image...")
        download_image(result["resultUrls"][0], args.output)
        print(f"Done! Saved to: {args.output}")
        return

    # Upload images to ImgBB if needed
    image_urls = []

    if args.mode == "edit":
        if not os.path.exists(args.image):
            raise Exception(f"Image not found: {args.image}")
        image_urls.append(upload_to_imgbb(args.image))
        prompt = args.instruction

    elif args.mode == "compose":
        for img_path in args.images:
            if not os.path.exists(img_path):
                raise Exception(f"Image not found: {img_path}")
            image_urls.append(upload_to_imgbb(img_path))
        prompt = args.instruction

    else:  # generate
        prompt = args.prompt

    run_generation(prompt, args.output, image_urls, args.ratio, args.resolution, args.format, args.model)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
