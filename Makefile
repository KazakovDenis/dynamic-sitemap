analyze:
	flake8

test:
	python -m coverage run

coverage:
	python -m coverage report
	python -m coverage html

release:
	python setup.py sdist bdist_wheel
	twine upload --repository pypi dist/*

test_release:
	python setup.py sdist bdist_wheel
	twine upload --repository testpypi dist/*
