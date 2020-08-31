import numpy as np
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


# This is an easy way to turn our question, which is
# about a pair of bools: (geography, biography)
# into a single variable with four possible values.
# This transformation is required in order to use multinomial
# logistic regression.
def assign_letter(bool_tuple):
    if not bool_tuple[0] and not bool_tuple[1]:
        return 'a'
    if bool_tuple[0] and not bool_tuple[1]:
        return 'b'
    if not bool_tuple[0] and bool_tuple[1]:
        return 'c'
    if bool_tuple[0] and bool_tuple[1]:
        return 'd'
    # if this code is written incorrectly it should be noisy
    raise Exception

# In this function, I build two logistic regression models which try to predict whether
# an article is about geography, or biography, respectively. 
def find_accuracy(df):
    stats     = df[['mean_word_length', 'mean_sentence_length', 'stddev_word_length', 'stddev_sentence_length']]
    categories = df[['biography', 'geography']]

    categories = list(map(assign_letter, zip(categories.biography, categories.geography)))
    stats_train, stats_test, categories_train, categories_test = train_test_split(
        stats, categories, random_state=4
    )

    regression = LogisticRegression(multi_class='multinomial')
    regression.fit(stats_train, categories_train)
    categories_pred = regression.predict(stats_test:
    accuracy = metrics.accuracy_score(categories_test, categories_pred)

    return (accuracy, regression.coef_)
