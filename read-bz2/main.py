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
    conn = psycopg2.connect(
        host=sys.argv[1],
        dbname='nlp-experiment', 
        user=sys.argv[2]
    )
    cur = conn.cursor()
    # insert all of our data
    for page in random_sample:
        wt = parse(get_wikitext(page.xml))
        is_biography = test_for_biography(wt)
        is_geography = test_for_geography(wt)
        plaintext = wt.plaintext()
        cur.execute("""
            INSERT INTO articles (id, article_name, biography, geography, article_contents)
            VALUES (%s %s %s %s %s);
            """,
            (
                page.pageid,
                page.name,
                is_biography(wt),
                is_geography(wt),
                wt.plaintext()
            )
        )
    # cleanup
    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
