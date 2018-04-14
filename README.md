# Dineral
Reads bank and credit card extracts provided by plugins and automatically categorizes entries for comparison with your budget. With Qt Gui

## Installation
### Download
Clone repo from git
```bash
git clone git@github.com:toschoch/dineral.git
```
install with setuptools
```bash
python setup.py install
```


####External Dependencies
As the PostFinance extracts are now text aware, tesseract ocr is not needed anymore. There are no more external dependencies.


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


