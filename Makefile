
all: venv deps

venv:
	virtualenv venv
	
deps: venv
	. venv/bin/activate && pip install Flask 
