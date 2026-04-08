# Examples

Runnable examples for the committed ECG/WFDB surface.

## Scripts

- `mitdb_compress.py`: load a staged MIT-BIH record, compress it, emit round-trip metrics
- `wfdb_bridge.py`: load a WFDB record object, bridge it into ZPE-Bio, verify integrity

## Run From A Clean Clone

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,validation]"
python examples/mitdb_compress.py --record-id 100 --samples 1024 --json
python examples/wfdb_bridge.py --record-id 100 --samples 1024 --json
```

## Dataset Commands

The default MIT-BIH path is already committed in `validation/datasets/mitdb/`.

Refresh one MIT-BIH record with `wfdb`:

```bash
python - <<'PY'
import wfdb
wfdb.dl_database("mitdb", "validation/datasets/mitdb", records=["100"])
PY
```

Acquire additional PhysioNet benchmark sets:

```bash
python scripts/benchmark_physionet.py --dataset ptb-xl --dataset nstdb --dataset edb --json
curl -fL -o validation/datasets/sleep-edfx/sleep-cassette/SC4001E0-PSG.edf \
  https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/SC4001E0-PSG.edf
```
