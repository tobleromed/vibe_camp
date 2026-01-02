import base64
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List

from openai import OpenAI

# Hardcode the local image path here:
IMAGE_PATH = "IMG_0290.jpeg"

MODEL = "gpt-4o"


@dataclass
class DetectedObject:
    label: str
    description: str
    confidence: float
    x: float
    y: float
    w: float
    h: float


def make_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key)


def jpeg_file_to_data_url(path: str) -> str:
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


def build_instruction() -> str:
    return """
Return ONLY valid JSON (no markdown) with this exact shape:

{
  "objects": [
    {
      "label": "string",
      "description": "string",
      "confidence": 0.0,
      "box": {"x": 0.0, "y": 0.0, "w": 0.0, "h": 0.0}
    }
  ],
  "warnings": ["string"]
}

Rules:
- box coordinates are normalized to [0,1] relative to image width/height.
- x,y are top-left; w,h are width/height.
- Include 8–25 objects max.
- Be specific about each item, to build a detailed inventory of the visible items.
- If unsure, omit the object or add a warning.
""".strip()


def call_vision_api(client: OpenAI, data_url: str, instruction: str) -> Dict[str, Any]:
    resp = client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": instruction},
                    {"type": "input_image", "image_url": data_url},
                ],
            }
        ],
        text={"format": {"type": "json_object"}},
    )
    return json.loads(resp.output_text)


def parse_objects(payload: Dict[str, Any]) -> List[DetectedObject]:
    objs = []
    for o in payload.get("objects", []) or []:
        box = o.get("box") or {}
        objs.append(
            DetectedObject(
                label=str(o.get("label", "unknown")),
                description=str(o.get("description", "unknown")),
                confidence=float(o.get("confidence", 0.0) or 0.0),
                x=float(box.get("x", 0.0) or 0.0),
                y=float(box.get("y", 0.0) or 0.0),
                w=float(box.get("w", 0.0) or 0.0),
                h=float(box.get("h", 0.0) or 0.0),
            )
        )
    return objs


def print_results(objects: List[DetectedObject], warnings: List[str]) -> None:
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"- {w}")
        print()

    if not objects:
        print("No objects returned.")
        return

    objects = sorted(objects, key=lambda o: o.confidence, reverse=True)

    print(f"Detected {len(objects)} objects:")
    for o in objects:
        print(
            f"- {o.label:20s} {o.description:50s} conf={o.confidence:.2f}  "
            f"box=[x={o.x:.3f}, y={o.y:.3f}, w={o.w:.3f}, h={o.h:.3f}]"
        )


def run() -> None:
    client = make_client()
    data_url = jpeg_file_to_data_url(IMAGE_PATH)
    instruction = build_instruction()
    payload = call_vision_api(client, data_url, instruction)

    warnings = payload.get("warnings", []) or []
    objects = parse_objects(payload)
    print_results(objects, warnings)


if __name__ == "__main__":
    run()
