Question: is it easy to distinguish the Wikipedia pages of musicians and scientists? What about people who are both?

Method:
1. Use Python webscraping tools to amass bios of musicians and scientists, or at least the URLs. 
2. Use Apache Hadoop and MapReduce to preprocess these Wikipedia entries. 
3. Store the results in a PostgreSQL database.
4. Use Python Keras to train a neural net on the resulting vectors.
5. Assess the accuracy of the resulting neural net. 
