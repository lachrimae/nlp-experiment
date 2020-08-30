import Dependencies._

ThisBuild / scalaVersion     := "2.11.7"
ThisBuild / version          := "0.1.0-SNAPSHOT"
ThisBuild / organization     := "com.example"
ThisBuild / organizationName := "example"

lazy val doobieVersion = "0.8.0-RC1"

lazy val root = (project in file("."))
  .settings(
    name := "analyzeWiki",
    libraryDependencies ++= Seq(
        scalaTest % Test,
        "org.apache.spark" %% "spark-core"      % "2.4.6",
        "org.tpolecat"     %% "doobie-core"     % doobieVersion,
        "org.tpolecat"     %% "doobie-postgres" % doobieVersion,
        "org.tpolecat"     %% "doobie-specs2"   % doobieVersion,
    )
  )

mainClass in Compile := Some("org.lachrimae.analyzeWiki.AnalyzeApp")

assemblyMergeStrategy in assembly := {   
  case PathList("META-INF", xs @ _*) => MergeStrategy.discard   
  case x => MergeStrategy.first 
}

// See https://www.scala-sbt.org/1.x/docs/Using-Sonatype.html for instructions on how to publish to Sonatype.
