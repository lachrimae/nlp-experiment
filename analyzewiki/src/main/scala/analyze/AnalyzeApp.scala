package com.lachrimae.analyzeWiki

import org.apache.spark.{SparkConf, SparkContext}
import doobie._
import doobie.implicits._
import doobie.util.ExecutionContexts
import cats._, cats.data._, cats.effect._, cats.implicits._
import scala.language.higherKinds

object QueryRecipe {
  val articleNames = sql"SELECT id, article_contents FROM articles".query[Article]
  def writeStats[F[_]: Foldable](statsList: F[Stats]): ConnectionIO[Int] = {
    var sql = "UPDATE articles SET mean_word_length = ?, mean_sentence_length = ?, stddev_word_length = ?, stddev_sentence_length ? WHERE id = ?"
    Update[Stats](sql).updateMany(statsList)
  }
}


/**
  * Use this when submitting the app to a cluster with spark-submit
  * */
object AnalyzeApp extends App{
  implicit val cs = IO.contextShift(ExecutionContexts.synchronous)
  val conn = Transactor.fromDriverManager[IO](
    "org.postgresql.Driver", 
    s"jdbc:postgresql://db/nlp_experiment", 
    args(0), // username
    args(1)  // password
  )
  val articles = QueryRecipe
    .articleNames
    .to[Seq]
    .transact(conn)
    .unsafeRunSync

//  val jdbcDF = -
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
