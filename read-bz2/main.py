import access_bz2
import psycopg2
import sys
from wikitextparser import parse
from process_articles import get_wikitext, is_biography, is_geography


def main():
    # get a (biased) random sample from Wikipedia...
    random_sample = access_bz2.get_indices_semirandom(20000)
    access_bz2.populate_xml(random_sample)
    # initialize database connection
    with psycopg2.connect(host=sys.argv[1],
                          dbname='nlp-experiment', 
                          user=sys.argv[2]) as conn:
        with conn.cursor() as cur:
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
                cur.execute("""
                    INSERT INTO articles (id, article_name, biography, geography, article_contents)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
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
