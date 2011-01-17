#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    from setuptools.command.test import test


class mytest(test):
    def run(self, *args, **kwargs):
        from runtests import runtests
        runtests()
        # Upgrade().run(dist=True)
        # test.run(self, *args, **kwargs)

setup(
    name='gargoyle',
    version='0.1.1',
    author='DISQUS',
    author_email='opensource@disqus.com',
    url='http://github.com/disqus/gargoyle',
    description = 'Switches',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'django-modeldict>=1.0.1',
        'nexus>=0.1.0',
        'django-jsonfield',
    ],
    test_suite = 'gargoyle.tests',
    include_package_data=True,
    cmdclass={"test": mytest},
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)