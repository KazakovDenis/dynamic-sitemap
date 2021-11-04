analyze:
	flake8

test:
	python -m coverage run

coverage:
	python -m coverage report
	python -m coverage html

build:
	python setup.py sdist bdist_wheel

release: build
	twine check dist/*
	twine upload --repository pypi dist/*

test_release: build
	twine check dist/*
	twine upload --repository testpypi dist/*
