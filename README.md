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
tesseract
```
these can be installed via apt-get in unix systems
```bash
apt-get install tesseract-ocr tesseract-ocr-en tesseract-ocr-de poppler-utils pkg-config
```
or for mac
```bash
brew install poppler
brew install tesseract
brew install tesseract-en
brew install tesseract-de
```
for details see https://github.com/tesseract-ocr/tesseract/wiki
and http://brewformulas.org/Poppler

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

in order to update the classifier look into the jupyter notebook
classifier.py


