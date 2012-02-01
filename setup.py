#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

tests_require = [
    'Django>=1.1',
    'South',
    'nose',
    'django-nose',
]

setup(
    name='gargoyle',
    version='0.7.2',
    author='DISQUS',
    author_email='opensource@disqus.com',
    url='http://github.com/disqus/gargoyle',
    description = 'Gargoyle is a platform built on top of Django which allows you to switch functionality of your application on and off based on conditions.',
    packages=find_packages(exclude=["example_project", "tests"]),
    zip_safe=False,
    install_requires=[
        'django-modeldict>=1.1.6',
        'nexus>=0.2.3',
        'django-jsonfield==0.6',
    ],
    license='Apache License 2.0',
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='runtests.runtests',
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)