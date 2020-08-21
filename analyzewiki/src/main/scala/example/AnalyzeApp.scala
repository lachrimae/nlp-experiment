package com.lachrimae.analyzeWiki

import org.apache.spark.{SparkConf, SparkContext}
import doobie._
import doobie.implicits._
import doobie.util.ExecutionContexts
import cats._, cats.data._, cats.effect._, cats.implicits._
import scala.language.higherKinds

/**
  * Use this to test the app locally, from sbt:
  * sbt "run inputFile.txt outputFile.txt"
  *  (+ select AnalyzeLocalApp when prompted)
  *
object AnalyzeLocalApp extends App{
  val (inputFile, outputFile) = (args(0), args(1))
  val conf = new SparkConf()
    .setMaster("local")
    .setAppName("nlp-experiment")

  Runner.run(conf, inputFile, outputFile)
}
  */


object QueryRecipe {
  val tableName = "bio_articles"
  val articleNames = sql"SELECT id, article_contents FROM ${tableName}".query[Article]
  def writeStats[F[_]: Foldable](statsList: F[Stats]): ConnectionIO[Int] = {
    var sql = "UPDATE ${tableName} SET mean_word_length = ?, mean_sentence_length = ?, stddev_word_length = ?, stddev_sentence_length ? WHERE id = ?"
    Update[Stats](sql).updateMany(statsList)
  }
}

/**
  * Use this when submitting the app to a cluster with spark-submit
  * */
object AnalyzeApp extends App{
  implicit val cs = IO.contextShift(ExecutionContexts.synchronous)
  val conn = Transactor.fromDriverManager[IO](
  "org.postgresql.Driver", "jdbc:postgresql:world", "postgres", ""
  )

  val articles = QueryRecipe
    .articleNames
    .to[Seq]
    .transact(conn)
    .unsafeRunSync

  // spark-submit command should supply all necessary config elements
  Runner.run(new SparkConf(), articles, conn)
}

object Runner {
  def run(conf: SparkConf, inputData: Seq[Article], dbConn: Transactor[IO]): Unit = {
    val sc = new SparkContext(conf)
    val rdd = sc.makeRDD(inputData)
    val stats = GetSentenceAndWordStats
      .getStats(rdd)
      .toLocalIterator
      .toStream
    val outputStream = QueryRecipe
      .writeStats(stats)
      .transact(dbConn)
      .unsafeRunSync
  }
}
