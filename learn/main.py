import logistic
import neural
from sqlalchemy import create_engine
from sys import argv, exit


READ_NON_NULL_ENTRIES = """
SELECT * FROM articles
WHERE mean_word_length IS NOT NULL
AND mean_sentence_length IS NOT NULL
AND stddev_word_length IS NOT NULL
AND stddev_sentence IS NOT NULL;
"""


def main():
    """format: main.py db_hostname db_username db_password"""
    try:
        connect_string = f'postgresql+psycopg2://{argv[2]}:{argv[3]}@{argv[1]}/nlp_experiment'
    except IndexError as e:
        print('Use the format: main.py db_hostname db_username db_password')
        raise e

    engine = create_engine(connect_string)
    with engine.connect() as connection:
        articles = pandas.read_sql_query(
            READ_NON_NULL_ENTRIES,
            connection
        )
        logistic_accuracy = logistic.find_accuracy(articles)
        neural_accuracy = neural.find_accuracy(articles)
        print("Logistic accuracy was ", logistic_accuracy, "\nNeural accuracy was ", neural_accuracy)


if __name__ == '__main__':
    main()
