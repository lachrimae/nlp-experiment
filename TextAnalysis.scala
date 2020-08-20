package com.lachrimae.analyzeWiki

/**
 * Souped up version of wordcounting.
 */

import org.apache.spark.rdd._
import scala.math._

object GetSentenceAndWordStats {
  /**
   * A slightly more complex than normal wordcount example with optional
   * separators and stopWords. Splits on the provided separators, removes
   * the stopwords, and converts everything to lower case.
   */
  def mean(seq: [Int]): Option[Float] = {
    if (seq.isEmpty)
      None
    else
      Some(seq.map(_.toFloat).sum / seq.map(_.toFloat).length)
  }

  def stddev(seq: [Int]): Option[Float] = {
    if (seq.isEmpty)
      None
    else
      val floatSeq = seq.map(_.toFloat)
      val avg = floatSeq.sum / floatSeq.length
      val squares = seq.map(pow((_ - avg), 2))
      sqrt(squares.sum / floatSeq.length)

  def withStopWordsFiltered(rdd : RDD[(Int, String)],
    wordSeparators : Array[Char] = " ".toCharArray,
    sentenceSeparators : Array[Char] = ".!?".toCharArray): RDD[(String, Option[Float], Option[Float], Option[Float], Option[Float])] = {
    // We want to find [(article index, [([length of each word], length of each sentence)])]
    val nestedLengths: RDD[(Int, [([Int], Int)])] = rdd.map(
      (
        _._1,
        _._2.split(
          sentenceSeparators
        ).map(
          (_.split(wordSeparators), _.length())
        ).map(
          (_._1.map(_.length), _._2)
        )
      )
    )
    val sentenceLengths: RDD[(Int, [Int])] = nestedLengths.map(
      (_._1, _._2.map(_._2))
    )
    val sentenceMeanAndStddev: RDD[(Int, Option[Float], Option[Float])] = sentenceLengths.map(
      (_._1, mean(_._2), stddev(_._2))
    )
    val wordLengths: RDD[(Int, [Int])] = nestedLengths.map(
      (_._1, _._2.map(_._1.flatten))
    )
    val wordMeanAndStddev: RDD[(Int, Option[Float], Option[Float])] = wordLengths.map(
      (_._1, mean(_._2), stddev(_._2))
    )
    val joinedStats: = sentenceMeanAndStddev.join(
      wordMeanAndStddev
    )
    val statsFlattened = joinedStats.map(
      (_._1, _._2._1, _._2._2, _._3._1, _._3._2)
    )

    statsFlattened
  }
}
