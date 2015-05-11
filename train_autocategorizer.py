# ----------------------------------
# project: 
# file:    train_autocategorizer.py
# author:  tobi
# created: 02.08.14
# ----------------------------------
from collections import Counter
import logging
import pickle
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.grid_search import GridSearchCV
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn import cross_validation, metrics
from sklearn.pipeline import Pipeline

from datasave import load_data

__author__ = 'tobi'
__copyright__ = 'Copyright tobi, 2014'

""" """

log = logging.getLogger()

def main():

    database = 'data/categorized.csv'
    data = load_data(database)
    data.Kategorie[data.Deleted]='Delete'
    log.info("database loaded")

    categories = np.unique(data.Kategorie).tolist()
    log.info("found categories: %s",categories)
    target = np.array([categories.index(cat) for cat in data.Kategorie.tolist()])
    log.info("assinged target index")

    data_train, data_test, target_train, target_test = cross_validation.train_test_split(data.Text, target, test_size=0.1)
    log.info("split data into training- and testset")

    text_clf = Pipeline([('vect',CountVectorizer()),
                         ('tfidf',TfidfTransformer()),
                         ('clf', SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, n_iter=5))])

    parameters = {'vect__ngram_range': [(2,4),(2,5),(2,6)],
                  'vect__analyzer':['char_wb'],
                  'vect__lowercase': [True],
                  'tfidf__use_idf': [True],
                  'clf__alpha': np.linspace(1e-2,1e-4,5)}

    gs_clf = GridSearchCV(text_clf,parameters,cv=10,verbose=3)
    gs_clf.fit(data_train,target_train)
    log.info("classifier trained")

    preds = gs_clf.predict(data_test)

    print metrics.classification_report(target_test, preds,target_names=categories)

    text_clf = gs_clf.best_estimator_
    text_clf.classes_names = categories

    with open("data/classifier.pickle","wb") as fp:
        pickle.dump(text_clf,fp)
    log.info("classifier saved!")

    print gs_clf.best_params_





if __name__=='__main__':
    logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main()

