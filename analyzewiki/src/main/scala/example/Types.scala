package com.lachrimae.analyzeWiki

import scalaz._
import Scalaz._
import scala.collection

case class Article(id: Int, content: String)
case class Stats(mean_word: Double, mean_sentence: Double, stddev_word: Double, stddev_sentence: Double, id: Int)
case class WordMeanAndStddev(mean: Double, stddev: Double)
case class SentenceMeanAndStddev(mean: Double, stddev: Double)
