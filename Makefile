analyze:
	isort -c dynamic_sitemap tests
	flake8
	mypy

test:
	python -m coverage run

coverage:
	python -m coverage report
	python -m coverage html

precommit: analyze test coverage

build:
	python setup.py sdist -d pypi bdist_wheel -d pypi
	rm -r *.egg-info build

release: build
	twine check pypi/*
	twine upload --repository pypi pypi/*

test_release: build
	twine check pypi/*
	twine upload --repository testpypi pypi/*

doc:
	sphinx-build -b html docs/ docs/_build/html
