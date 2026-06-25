# Convenience targets for the Pediatric Asthma Ventilation Simulator.
# Usage: make test | make reproduce | make figures | make scenarios | make clean

PYTHON ?= python
export PYTHONPATH := src

.PHONY: test reproduce scenarios figures sensitivity app clean

test:
	$(PYTHON) -m pytest -q

reproduce:
	$(PYTHON) scripts/reproduce_all.py

scenarios:
	$(PYTHON) src/run_all_scenarios.py

figures:
	$(PYTHON) src/generate_paper_figures.py

sensitivity:
	$(PYTHON) src/sensitivity_analysis.py

app:
	streamlit run app/streamlit_app.py

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -prune -exec rm -rf {} +
	find . -name '*.pyc' -delete
