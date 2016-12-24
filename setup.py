import os

from setuptools import setup, find_packages


# Utility function to read the README.md file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README.md file and 2) it's easier to type in the README.md file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

install_requires = [
    'numpy>=1.7.0',
    'matplotlib>=1.3.0',
    'pandas>=0.17.0',
    'scikit-learn>=0.18.1',
    'install_freedesktop'

]

test_requires = [
    'pylint>=1.0.0',
    'nosexcover>=1.0.0',
    'nose>=1.3.0',
]

extras_require = {
}

setup(
    name='dineral',
    version='0.9.1',
    author='Tobias Schoch',
    author_email='tobias.schoch@vtxmail.ch',
    description='This is a module which helps to quickly plot nice figures',
    license='public',
    keywords='finance budget gui report',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    package_data={'dineral': ['res/*.png','bash/*.sh','internaldata/classifier.pickle',
                              'internaldata/categorized.csv','internaldata/properties.json']},
    long_description=read('README.md'),
    install_requires=install_requires,
    tests_require=test_requires,
    extras_require=extras_require,
    test_suite='nose.collector',
    data_files=[
        ('share/icons/hicolor/scalable/apps', ['dineral/res/dineral.png']),
    ],
    entry_points = {
            'console_scripts': ['dineral=dineral.main:main']
        },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
