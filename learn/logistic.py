import numpy as np
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

def find_accuracy(df):
    stats = None
    categories = None
    # initialize the training and testing sets, and fit the model.
    stats_train, stats_test, categories_train, categories_test = train_test_split(
        stats, categories, random_state=4
    )
    logistic_regression = LogisticRegression()
    logistic_regression.fit(stats_train, categories_train)

    # check the prediction for accuracy
    categories_pred = logistic_regression.predict(stats_test)
    accuracy = metrics.accuracy_score(categories_test, categories_pred)
    return accuracy
