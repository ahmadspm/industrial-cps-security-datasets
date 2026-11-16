"""Generate the browser dashboard's event counts from the public release."""
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path

here = Path(__file__).resolve().parent
source = here.parents[1] / "data/operational/event_features.jsonl.gz"
counts = defaultdict(Counter)
with gzip.open(source, "rt", encoding="utf-8") as records:
    for line in records:
        row = json.loads(line)
        second = row["relative_seconds"]
        bucket = int(second // 10) if second is not None else -1
        counts[row["trace_id"]][bucket, row["event_class"]] += 1

result = {
    trace: [[bucket, event, count] for (bucket, event), count in sorted(values.items())]
    for trace, values in sorted(counts.items())
}
(here / "app/trace-counts.json").write_text(
    json.dumps(result, indent=None, separators=(",", ":")) + "\n", encoding="utf-8"
)
