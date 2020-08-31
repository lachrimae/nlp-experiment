import numpy as np
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def assign_letter(bool_tuple):
    if not bool_tuple[0] and not bool_tuple[1]:
        return 'a'
    elif bool_tuple[0] and not bool_tuple[1]:
        return 'b'
    elif not bool_tuple[0]:
        return 'c'
    else:
        return 'd'

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
    categories_pred = regression.predict(stats_test)
    accuracy = metrics.accuracy_score(categories_test, categories_pred)

    accuracy2 = metrics.accuracy_score(categories_test, ['a'] * len(categories_test))

    return (accuracy2, regression.coef_)
