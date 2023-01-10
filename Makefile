# powershell:

override _deps = pip install undetected_chromedriver \
	pip install fastapi \
	pip install pydantic \
	# pip install flask \
	# pip install watchdog \
	# pip install flask-restful #TODO

i_deps:
	$(_deps)

dev_start: 
	# . ./venv/Scripts/activate
	$(_deps)
	uvicorn main:app --reload --port=3001

start:
	gunicorn main:app -k uvicorn.workers.UvicornWorker --port=3001

get_reqs:
	pipreqs --encoding=utf8 --force
