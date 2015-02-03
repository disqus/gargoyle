#!/usr/bin/env python

from setuptools import setup, find_packages

try:
    import multiprocessing
except:
    pass

tests_require = [
    'Django>=1.4,<1.8',
    'django-nose',
    'nose',
    'South',
]

install_requires = [
    'django-modeldict>=1.2.0',
    'nexus>=0.2.3',
    'django-jsonfield>=0.9.2,<0.9.13',
]


setup(
    name='gargoyle',
    version='0.11.0',
    author='DISQUS',
    author_email='opensource@disqus.com',
    url='https://github.com/disqus/gargoyle',
    description='Gargoyle is a platform built on top of Django which allows you to switch functionality of your application on and off based on conditions.',
    packages=find_packages(exclude=["example_project", "tests"]),
    zip_safe=False,
    install_requires=install_requires,
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
