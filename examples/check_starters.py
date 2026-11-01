"""Check actual inputs, split separation, reproducibility and recorded baselines."""
import gzip,json,pathlib
from run_starters import run,partition
root=pathlib.Path(__file__).resolve().parents[1]
report,splits=run(root)
assert report==json.loads((root/'examples/baselines/results.json').read_text())
assert splits==json.loads(gzip.decompress((root/'examples/baselines/splits.json.gz').read_bytes()))
assert report['anomaly']['train_events']+report['anomaly']['test_events']==14124
assert report['anomaly']['train_traces']+report['anomaly']['test_traces']==27
assert 0<report['agents']['test_stop_prevalence']<1
assert report['agents']['continue_recall']==0
assert all(v==partition(k) for k,v in splits['graph'].items())
assert all(v==partition(k) for k,v in splits['operational'].items())
assert run(root)==(report,splits)
print('Starter results, fixed partitions, class coverage and repeatability verified.')
