# Dineral
Reads bank and credit card extracts provided by plugins and automatically categorizes entries for comparison with your budget. With Qt Gui

## Installation
### Download
Clone repo from git
```bash
git clone git@github.com:toschoch/dineral.git
```

####External Dependencies
Most of the dataplugins (PostFinance, etc.) depend on the unix commandline tools
```text
pdftotext
```
these can be installed via apt-get in unix systems
```bash
apt-get install poppler-utils pkg-config
```
or for mac
```bash
brew install poppler
```
http://brewformulas.org/Poppler

####Python Dependencies
```text
numpy
scipy
scikit-learn
```
Unfortunately pip/setuptools dependencies on numpy and scipy do not work out of the box.Therefore one has to install these dependencies in the following order:
```bash
pip install numpy
``` 
```bash
pip install scipy
```
```bash
pip install scikit-learn
```
```bash
python setup.py install
```


##Usage

### Start the programm
start programm over bash script
```bash
dineral
```

or in python
```python
import dineral.main as main
    
if __name__ == '__main__':
    main()
    
```

### Account information
Dineral offers to choose at program start between multiple accounts. Each account has to be configured in the 
'properties.json' configuration file.

This file is can be found under \<your python installation>\Lib\site-packages\dineral\internaldata\properties.json

There is a template in the same directory that can be used (must be renamed)

#### Minimum configuration
##### Database
path to *.csv file where data is stored

##### Budget
In order to specify account categories and to enable comparison with budget a file

in order to update the classifier look into the jupyter notebook
classifier.py


