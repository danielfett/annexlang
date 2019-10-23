from setuptools import setup
import sys
if sys.version_info < (3, 5):
    raise RuntimeError("This package requres Python 3.5+")

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='annexlang',
    version='0.4',
    description='A description language for drawing communication protocols in TeX documents.',
    url='http://github.com/webhamster/annexlang',
    author='Daniel Fett',
    author_email='github@danielfett.de',
    license='MIT',
    packages=['annexlang'],
    zip_safe=False,
    scripts=['bin/annex-convert'],
    install_requires=[
        'pyyaml',
        'pyScss',
    ],
      
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    long_description=readme(),
    include_package_data=True,
)
python_requires='>=3.5'
