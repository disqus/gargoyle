test:
	pep8 --exclude=gargoyle --ignore=E501,E225 gargoyle || exit 1
	pyflakes -x W gargoyle || exit 1
	coverage run --include=gargoyle/* setup.py test && \
	coverage html --omit=*/migrations/* -d cover
