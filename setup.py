#!/usr/bin/env python
from setuptools import setup
from dynamic_sitemap import __about__ as about


with open('README.md', 'r') as f:
    long_description = f.read()


if __name__ == '__main__':
    setup(
        name=about['__title__'],
        version=about['__version__'],
        author=about['__author__'],
        author_email=about['__email__'],
        url=about['__url__'],
        license=about['__license__'],
        description='Sitemap generator for Python frameworks',
        long_description=long_description,
        long_description_content_type='text/markdown',
        keywords='sitemap',
        packages=[about['__module__']],
        package_data={
            about['__module__']: ['templates/*'],
        },
        install_requires=['pytz>=2020.1'],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Framework :: Flask',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Topic :: Internet',
        ],
        python_requires='>=3.6',
    )
