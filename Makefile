SHELL := /bin/bash

debug-python:
	APIKEY=apikey123 \
	DEV=true \
	python3 -m server

