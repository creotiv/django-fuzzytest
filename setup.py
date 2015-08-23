from setuptools import setup, find_packages
from io import open

setup(
    name='django-fuzzytest',
    version='0.1.0',
    description='This is the automatic Fuzzy Test tool for testing Django applications.',
    long_description=open('README.rst', encoding='utf-8').read(),
    author='Andrey Nikishaev',
    author_email='creotiv@gmail.com',
    url='https://github.com/creotiv/django-fuzzytest',
    download_url = 'https://github.com/creotiv/django-fuzzytest/tarball/0.1.0',
    keywords = ['testing', 'django', 'fuzzy'], 
    license='BSD',
    packages=find_packages(exclude=('tests.*', 'tests')),
    install_requires=[
        'django>=1.6',
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
