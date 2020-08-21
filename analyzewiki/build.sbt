import Dependencies._

ThisBuild / scalaVersion     := "2.11.7"
ThisBuild / version          := "0.1.0-SNAPSHOT"
ThisBuild / organization     := "com.example"
ThisBuild / organizationName := "example"

lazy val root = (project in file("."))
  .settings(
    name := "analyzeWiki",
    libraryDependencies ++= Seq(
        scalaTest % Test,
        "org.apache.spark" %% "spark-core"                % "2.4.6",
        "org.scalaz"       %% "scalaz-core"               % "7.3.2",
        "org.tpolecat"     %% "doobie-core"               % "0.8.0-RC1",
        "org.tpolecat"     %% "doobie-contrib-postgresql" % "0.3.0",
        "org.tpolecat"     %% "doobie-contrib-specs2"     % "0.3.0",
    )
  )

// See https://www.scala-sbt.org/1.x/docs/Using-Sonatype.html for instructions on how to publish to Sonatype.
