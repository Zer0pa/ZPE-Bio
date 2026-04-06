.PHONY: install verify-core test-destruct benchmark clean

install:
	python -m pip install -e ".[dev,validation]"

verify-core:
	python -m pytest tests/ -v -k "not nrf and not embedded and not hardware"

test-destruct:
	python -m pytest validation/destruct_tests/ -v

benchmark:
	python scripts/benchmark_mitdb.py

clean:
	rm -rf dist/ build/ *.egg-info
