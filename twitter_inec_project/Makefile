# .ONESHELL:

.DEFAULT_GOAL := install

PYTHON = $(shell which python3)
# PIP = ./venv/bin/pip 


venv/bin/activate: requirements.txt
	python3 -m venv venv
	chmod +x venv/bin/activate
	. ./venv/bin/activate 
	


# venv: venv/bin/activate
# 	. ./venv/bin/activate 

install: venv/bin/activate
	pip install -r requirements.txt

# start: run
# 	prefect config set PREFECT_API_URL=http://127.0.0.1:4980/api

clean:
	rm -rf __pycache__
	rm -rf venv