# Dineral
Reads bank and credit card extracts provided by plugins and automatically categorizes entries for comparison with your budget. With Qt Gui

## Installation
### Download
Clone repo from git
```text
git clone git@github.com:toschoch/dineral.git
```
install with setuptools
```bash
python setup.py install
```


#### External Dependencies
As the PostFinance extracts are now text aware, tesseract ocr is not needed anymore. 
However Dineral still depends on the `pdftotext` command line tool (see [here](https://en.wikipedia.org/wiki/Pdftotext)) from the [poppler-utils](https://linuxappfinder.com/package/poppler-utils) apps.

Install them under linux with 
```bash
apt-get install poppler-utils
```  
If you have a mac, use brew
```bash
brew install poppler
```
and under windows you can try [http://blog.alivate.com.au/poppler-windows/] (good luck!)


## Usage

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
'.dineral.yaml' configuration file.

After the first start of the program (that might fail due to a missing configuration file)
a sample configuration file will be created in your userhome directory (e.g. ~/.dineral.yaml).

#### Minimum configuration
##### Database
path to *.csv file where data is stored

##### Budget
In order to specify account categories and to enable comparison with budget a file

in order to update the classifier look into the jupyter notebook
classifier.py


Change-Log
----------
##### 1.2.9
* added version in logs
* fixed bug in raiffeisen import
* update README.md for tag v1.2.9
* Raiffeisen extracts. Adapted to 2019 format

##### 1.2.8
* fixed regex for mastercard

##### 1.2.7
* added new mastercard extract format
* try jenkinsfile
* fixed robustness for no data

##### 1.2.6
* fixed bug in postfinance plugin
* other builder image
* first test with abstruse.yml

##### 1.2.5
* fixed width issue, removed additional extract parsing, and reload db after save

##### v1.2.4
* fixed update recently stored entries before report
* fixed missing entries (with numbers in transaction text) from mastercard extracts
* included change-log

##### v1.2.1
* Fixed bug loading the budget
* Fixed scaling bug

##### v1.2.0
* Raiffeissen account monthly/yearly

##### v1.1.5
* Database in feather format
* PyQt5 HiDpi Display

##### v1.1.3
* Mastercard plugin works now without OCR (more reliable)
* Temporary files are all in temp dir

##### v1.1.2
* supports multiple accounts
* YAML configuration format