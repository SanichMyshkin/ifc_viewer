venv:
	source .venv/bin/activate.fish

start:
	streamlit run Homepage.py

install:
	pip install --upgrade pip
	pip install -r requirements.txt