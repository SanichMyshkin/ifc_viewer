shell:
	poetry shell

start:
	streamlit run Homepage.py

install:
	poetry install --no-root

envdel:
	poetry env list
	poetry env remove --all