test:
	flake8 --exclude=migrations --ignore=E501,E225,E121,E123,E124,E125,E127,E128 --exit-zero gargoyle || exit 1
	python setup.py test
