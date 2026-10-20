import argparse
import json
import time
from pathlib import Path

from jiwer import cer, wer

from app.ocr.tesseract_engine import TesseractEngine

ENGINES = {"tesseract": lambda: TesseractEngine()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="JSON manifest with path and ground_truth")
    parser.add_argument("--engine", default="tesseract", choices=ENGINES.keys())
    args = parser.parse_args()

    rows = json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    engine = ENGINES[args.engine]()
    results = []
    for row in rows:
        started = time.perf_counter()
        prediction = engine.extract(Path(row["path"]))
        latency = time.perf_counter() - started
        truth = row["ground_truth"]
        results.append({"path": row["path"], "cer": cer(truth, prediction), "wer": wer(truth, prediction), "latency_seconds": latency})

    if not results:
        print("No benchmark rows found.")
        return

    summary = {
        "engine": args.engine,
        "documents": len(results),
        "mean_cer": sum(x["cer"] for x in results) / len(results),
        "mean_wer": sum(x["wer"] for x in results) / len(results),
        "mean_latency_seconds": sum(x["latency_seconds"] for x in results) / len(results),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
