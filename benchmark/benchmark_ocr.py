import argparse
import json
import time
from pathlib import Path

from app.ocr.azure_document_intelligence import extract_with_azure


def normalized_edit_distance(reference: str, prediction: str) -> float:
    reference, prediction = reference.strip(), prediction.strip()
    if not reference:
        return 0.0 if not prediction else 1.0
    prev = list(range(len(prediction) + 1))
    for i, a in enumerate(reference, 1):
        curr = [i]
        for j, b in enumerate(prediction, 1):
            curr.append(min(curr[-1] + 1, prev[j] + 1, prev[j - 1] + (a != b)))
        prev = curr
    return prev[-1] / max(1, len(reference))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', required=True)
    args = parser.parse_args()

    rows = json.loads(Path(args.dataset).read_text(encoding='utf-8'))
    results = []
    for row in rows:
        started = time.perf_counter()
        prediction = extract_with_azure(Path(row['path']).read_bytes())
        latency = time.perf_counter() - started
        results.append({
            'path': row['path'],
            'normalized_char_error': normalized_edit_distance(row['ground_truth'], prediction),
            'latency_seconds': latency,
        })

    if not results:
        print('No benchmark rows found.')
        return

    print(json.dumps({
        'engine': 'azure-document-intelligence',
        'documents': len(results),
        'mean_normalized_char_error': sum(x['normalized_char_error'] for x in results) / len(results),
        'mean_latency_seconds': sum(x['latency_seconds'] for x in results) / len(results),
    }, indent=2))


if __name__ == '__main__':
    main()
