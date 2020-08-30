import access_bz2
import psycopg2
import sys
from wikitextparser import parse
from process_articles import get_wikitext, is_biography, is_geography, sentence_stats, word_stats


CREATE_TABLE_STATEMENT = """
CREATE TABLE articles (
    id INT NOT NULL PRIMARY KEY,
    article_name VARCHAR(255) NOT NULL,
    biography BOOL,
    geography BOOL,
    mean_word_length FLOAT,
    mean_sentence_length FLOAT,
    stddev_word_length FLOAT,
    stddev_sentence_length FLOAT,
    article_contents TEXT
);
"""


INSERT_COLUMNS_FOR_LATER_ANALYSIS = """
INSERT INTO articles (id, article_name, biography, geography, article_contents)
VALUES (%s, %s, %s, %s, %s);
"""


INSERT_COLUMNS_ANALYZED = """
INSERT INTO articles (id, article_name, biography, geography, mean_word_length, mean_sentence_length, stddev_word_length, stddev_sentence_length)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""


def main():
    """format: main.py db_hostname db_username db_password"""
    # get a (biased) random sample from Wikipedia...
    analyze_now = False
    try:
        if sys.argv[4] == '--analyzenow':
            analyze_now = True
    except IndexError:
        pass
    try:
        host = sys.argv[1]
        user = sys.argv[2]
        pwd  = sys.argv[3]
    except IndexError:
        print('Use format: main.py db_hostname db_username db_password')
        sys.exit(1)
    random_sample = access_bz2.get_indices_semirandom(20000)
    access_bz2.populate_xml(random_sample)
    # initialize database connection
    with psycopg2.connect(host=host
                          dbname='nlp_experiment', 
                          user=user
                          password=pwd) as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_STATEMENT)
            # insert all of our data
            counter1 = 0
            counter2 = 0
            for page in random_sample:
                try:
                    wt = parse(get_wikitext(page.xml))
                except AttributeError:
                    continue
                try:
                    plaintext = wt.plain_text()
                except TypeError:
                    plaintext = ""
                except AttributeError:
                    plaintext = ""
                if analyze_now:
                    try:
                        word_mean,     word_stddev     = word_stats(plaintext)
                        sentence_mean, sentence_stddev = sentence_stats(plaintext)
                    except ZeroDivisionError:
                        word_mean,     word_stddev     = None, None
                        sentence_mean, sentence_stddev = None, None
                    cur.execute(
                        INSERT_COLUMNS_ANALYZED,
                        (
                            page.pageid,
                            page.name,
                            is_biography(wt),
                            is_geography(wt),
                            word_mean,
                            sentence_mean,
                            word_stddev,
                            sentence_stddev
                        )
                    )
                else:
                    cur.execute(
                        INSERT_COLUMNS_FOR_LATER_ANALYSIS,
                        (
                            page.pageid,
                            page.name,
                            is_biography(wt),
                            is_geography(wt),
                            plaintext
                        )
                    )
                counter1 += 1
                if counter1 % 100 == 0:
                    counter2 += 1
                    print(counter2 * 100, ' articles inserted')
            conn.commit()


if __name__ == '__main__':
    main()
