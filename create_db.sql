CREATE TABLE articles (
    id INT NOT NULL PRIMARY KEY,
    article_name VARCHAR(255) NOT NULL,
    biography BOOL,
    geography BOOL,
    mean_word_length DOUBLE,
    mean_sentence_length DOUBLE,
    stddev_word_length DOUBLE,
    stddev_sentence_length DOUBLE,
    article_contents TEXT
)
