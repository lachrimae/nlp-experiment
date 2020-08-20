CREATE TABLE articles (
    id INT NOT NULL PRIMARY KEY,
    musician BOOLEAN,
    scientist BOOLEAN,
    article_name VARCHAR(255) NOT NULL,
    mean_word_length FLOAT,
    mean_sentence_length FLOAT,
    stddev_word_length FLOAT,
    stddev_sentence_length FLOAT,
    article_contents TEXT
)
