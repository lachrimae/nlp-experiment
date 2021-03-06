# Question
Can we train machine learning models to detect whether a Wikipedia article is about geography, or if it is about biography, if the only input data we feed to the models is the mean and standard deviation of characters per word, and the mean and standard deviation of words per sentence?

## Method
1. Make a small (~20 000 articles) sample from Wikipedia's bz2-compressed XML dump from 1 Aug 2020. Categorize the articles as geography or biography (or both) based on the presence of keywords in their section headers.
2. Use Scala with Apache Hadoop and Spark to find the statistical properties of the articles' word and sentence length. (Or, in the absence of access to a cluster, process the articles directly after decompressing them in Python.)
3. Store the results in a PostgreSQL database.
4. Use scikit-learn to build a multinomial logistic model; use Keras to train a neural net model. 
5. Assess the accuracy of the models.

## Results
I ran this code, and got a 72.8% accuracy out of the multinomial logistic model. That's actually worse than the constant model that constantly guesses that an article is neither a biography or a geography, which has 73.7% accuracy.
I want to try removing non-geography and non-biography articles from the sample set. I wonder whether the multinomial logistic model will work better to distinguish geography and biography articles in the absence of other articles.

Writing the neural network is still a work-in-progress.

## Directory structure
Inside `read-bz2/` is a lot of Python code I use to read from the `.bz2` compressed XML dump. Inside `analyzewiki/` is a Scala project containing Hadoop code which will do basic statistical analyses of the Wikipedia articles. Inside `learn/` is the regression and neural network code. The `docker-hadoop/` directory includes some dockerfiles for images I was using to test the Scala code. However, due to limitations on the use of Docker with the JVM, the Scala app crashes due to garbage-collection and heap size issues.
