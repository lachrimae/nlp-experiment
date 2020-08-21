package com.lachrimae.analyzeWiki

/**
 * Souped up version of wordcounting.
 */

import org.apache.spark.{SparkContext,SparkConf}
import org.apache.spark.rdd._
import scala.math._
import scala.collection._

object GetSentenceAndWordStats {
  /**
   * A slightly more complex than normal wordcount example with optional
   * separators and stopWords. Splits on the provided separators, removes
   * the stopwords, and converts everything to lower case.
   */
  def mean(seq : Array[Int]): Double = {
    if (seq.isEmpty)
      -1.0
    else
      seq.map(_.toDouble).sum / seq.map(_.toDouble).length
  }

  def stddev(seq : Array[Int]): Double = {
    if (seq.isEmpty)
      -1.0
    else {
      val floatSeq = seq.map(_.toDouble)
      val avg = floatSeq.sum / floatSeq.length
      val squares = seq.map(x => pow(x - avg, 2))
      sqrt(squares.sum / floatSeq.length).toDouble
    }
  }

  def getStats(rdd : RDD[Article],
    wordSeparators : Array[Char] = " ".toCharArray,
    sentenceSeparators : Array[Char] = ".!?".toCharArray): RDD[Stats] = {
    // We want to find [(article index, [([length of each word], length of each sentence)])]
    val nestedLengths: RDD[(Int, Array[(Array[Int], Int)])] = rdd.map(article =>
      (
        article.id,
        article.content.split(
          sentenceSeparators
        ).map(sentence =>
          (sentence.split(wordSeparators), sentence.length())
        ).map(sentencePair =>
          (sentencePair._1.map(_.length), sentencePair._2)
        )
      )
    )
    val sentenceLengths: RDD[(Int, Array[Int])] = nestedLengths.map(sentencePair =>
      (sentencePair._1, sentencePair._2.map(_._2))
    )
    val sentenceMeanAndStddev: RDD[(Int, SentenceMeanAndStddev)] = sentenceLengths.map(
      sentencePair =>
        (sentencePair._1, 
         SentenceMeanAndStddev(mean(sentencePair._2), stddev(sentencePair._2)))
    )
    val wordLengths: RDD[(Int, Array[Int])] = nestedLengths.map(sentencePair =>
      (sentencePair._1, sentencePair._2.flatMap(_._1))
    )
    val wordMeanAndStddev: RDD[(Int, WordMeanAndStddev)] = wordLengths.map(
      wordPair => 
        (wordPair._1, 
         WordMeanAndStddev(mean(wordPair._2), stddev(wordPair._2)))
    )
    //                             sentence           word
    val joinedStats: RDD[Stats] = sentenceMeanAndStddev
      .map(pair => (pair._1, (pair._2.mean, pair._2.stddev)))
      .join(wordMeanAndStddev
        .map(pair => (pair._1, (pair._2.mean, pair._2.stddev))))
      .map(pentuplet =>
        Stats(pentuplet._2._2._1, pentuplet._2._1._1, pentuplet._2._2._2, pentuplet._2._1._2, pentuplet._1)
      )
    joinedStats
  }
}
