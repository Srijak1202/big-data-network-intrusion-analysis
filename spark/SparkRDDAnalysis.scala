import org.apache.spark.SparkConf
import org.apache.spark.SparkContext
import org.apache.spark.HashPartitioner
import org.apache.spark.Partitioner
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession

// ============================================================
// CUSTOM PARTITIONER
// ============================================================

class AttackCategoryPartitioner(
    override val numPartitions: Int
) extends Partitioner {

  require(numPartitions > 0, "Number of partitions must be positive")

  override def getPartition(key: Any): Int = {
    key.toString match {
      case "Normal" => 0 % numPartitions
      case "DoS"    => 1 % numPartitions
      case "Probe"  => 2 % numPartitions
      case "R2L"    => 3 % numPartitions
      case "U2R"    => 4 % numPartitions
      case other    => Math.floorMod(other.hashCode, numPartitions)
    }
  }

  override def equals(other: Any): Boolean = other match {
    case p: AttackCategoryPartitioner =>
      p.numPartitions == numPartitions
    case _ => false
  }

  override def hashCode(): Int = numPartitions
}

// ============================================================
// MAIN ANALYSIS PROGRAM
// ============================================================

object SparkRDDAnalysis {

  def main(args: Array[String]): Unit = {

    val spark = SparkSession.builder()
      .appName("NSL-KDD Spark RDD Analysis")
      .master("local[*]")
      .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    val sc = spark.sparkContext

    val inputPath =
      if (args.nonEmpty) args(0)
      else "../big-data-network-intrusion-analysis/data/raw/KDDTrain+.txt"

    val raw: RDD[String] = sc.textFile(inputPath)

    // NSL-KDD TXT files have no header.
    // Retain only records with the expected 43 columns.
    val records = raw
      .map(_.trim)
      .filter(_.nonEmpty)
      .map(_.split(",", -1).map(_.trim))
      .filter(_.length == 43)
      .cache()

    val totalRecords = records.count()

    println("\n========== DATASET VALIDATION ==========")
    println(s"Input: $inputPath")
    println(s"Valid records: $totalRecords")
    println(s"Partitions: ${records.getNumPartitions}")

    // NSL-KDD field indexes:
    // protocol=1, service=2, flag=3, attack label=41,
    // difficulty=42.

    val attacks = records.map(row => row(41).stripSuffix("."))

    // ========================================================
    // ATTACK CATEGORY MAPPING
    // ========================================================

    val dos = Set(
      "back", "land", "neptune", "pod", "smurf", "teardrop",
      "apache2", "mailbomb", "processtable", "udpstorm", "worm"
    )

    val probe = Set(
      "ipsweep", "nmap", "portsweep", "satan", "mscan", "saint"
    )

    val r2l = Set(
      "ftp_write", "guess_passwd", "imap", "multihop", "phf",
      "spy", "warezclient", "warezmaster", "named", "sendmail",
      "snmpgetattack", "snmpguess", "xlock", "xsnoop", "httptunnel"
    )

    val u2r = Set(
      "buffer_overflow", "loadmodule", "perl", "rootkit",
      "ps", "sqlattack", "xterm"
    )

    def category(label: String): String = {
      if (label == "normal") "Normal"
      else if (dos.contains(label)) "DoS"
      else if (probe.contains(label)) "Probe"
      else if (r2l.contains(label)) "R2L"
      else if (u2r.contains(label)) "U2R"
      else "Unknown"
    }

    val enriched = records.map { row =>
      val label = row(41).stripSuffix(".")
      (row, label, category(label))
    }.cache()

    // ========================================================
    // A1: ATTACK CATEGORY COUNTS
    // ========================================================

    val categoryCounts = enriched
      .map { case (_, _, cat) => (cat, 1L) }
      .reduceByKey(_ + _)
      .cache()

    println("\n========== A1: ATTACK CATEGORY COUNTS ==========")
    categoryCounts.sortByKey().collect().foreach(println)

    // ========================================================
    // A2: INDIVIDUAL ATTACK LABEL COUNTS
    // ========================================================

    println("\n========== A2: ATTACK LABEL COUNTS ==========")

    attacks.map(label => (label, 1L))
      .reduceByKey(_ + _)
      .sortBy(_._2, ascending = false)
      .take(20)
      .foreach(println)

    // ========================================================
    // A3: PROTOCOL COUNTS
    // ========================================================

    println("\n========== A3: PROTOCOL COUNTS ==========")

    records.map(row => (row(1), 1L))
      .reduceByKey(_ + _)
      .sortByKey()
      .collect()
      .foreach(println)

    // ========================================================
    // A4: PROTOCOL x CATEGORY
    // ========================================================

    println("\n========== A4: PROTOCOL x CATEGORY ==========")

    enriched.map { case (row, _, cat) =>
      ((row(1), cat), 1L)
    }.reduceByKey(_ + _)
      .sortByKey()
      .collect()
      .foreach(println)

    // ========================================================
    // A5: TOP SERVICES
    // ========================================================

    println("\n========== A5: TOP SERVICES ==========")

    records.map(row => (row(2), 1L))
      .reduceByKey(_ + _)
      .sortBy(_._2, ascending = false)
      .take(15)
      .foreach(println)

    // ========================================================
    // A6: FLAG COUNTS
    // ========================================================

    println("\n========== A6: FLAG COUNTS ==========")

    records.map(row => (row(3), 1L))
      .reduceByKey(_ + _)
      .sortBy(_._2, ascending = false)
      .collect()
      .foreach(println)

    // ========================================================
    // A7: SERVICE x CATEGORY
    // ========================================================

    println("\n========== A7: SERVICE x CATEGORY ==========")

    enriched.map { case (row, _, cat) =>
      ((row(2), cat), 1L)
    }.reduceByKey(_ + _)
      .sortBy(_._2, ascending = false)
      .take(30)
      .foreach(println)

    // ========================================================
    // A8: LOGIN STATUS x CATEGORY
    // ========================================================

    println("\n========== A8: LOGIN STATUS x CATEGORY ==========")

    enriched.map { case (row, _, cat) =>
      ((row(11), cat), 1L)
    }.reduceByKey(_ + _)
      .sortByKey()
      .collect()
      .foreach(println)

    // ========================================================
    // A9: FAILED LOGINS x CATEGORY
    // ========================================================

    println("\n========== A9: FAILED LOGINS x CATEGORY ==========")

    enriched.map { case (row, _, cat) =>
      ((row(10).toDouble, cat), 1L)
    }.reduceByKey(_ + _)
      .filter { case ((failedLogins, _), _) => failedLogins > 0 }
      .sortBy(_._2, ascending = false)
      .take(20)
      .foreach(println)

    // ========================================================
    // A10: ROOT SHELL x CATEGORY
    // ========================================================

    println("\n========== A10: ROOT SHELL x CATEGORY ==========")

    enriched.map { case (row, _, cat) =>
      ((row(13), cat), 1L)
    }.reduceByKey(_ + _)
      .sortByKey()
      .collect()
      .foreach(println)

    // ========================================================
    // A11: GUEST LOGIN x CATEGORY
    // ========================================================

    println("\n========== A11: GUEST LOGIN x CATEGORY ==========")

    enriched.map { case (row, _, cat) =>
      ((row(21), cat), 1L)
    }.reduceByKey(_ + _)
      .sortByKey()
      .collect()
      .foreach(println)

    // ========================================================
    // A12: AVERAGE SOURCE AND DESTINATION BYTES
    // ========================================================

    println("\n========== A12: AVERAGE BYTES x CATEGORY ==========")

    enriched.map { case (row, _, cat) =>
      (cat, (row(4).toDouble, row(5).toDouble, 1L))
    }.reduceByKey {
      case ((src1, dst1, n1), (src2, dst2, n2)) =>
        (src1 + src2, dst1 + dst2, n1 + n2)
    }.mapValues {
      case (src, dst, n) =>
        (src / n, dst / n, n)
    }.sortByKey()
      .collect()
      .foreach(println)

    // ========================================================
    // A13: LAND FLAG x CATEGORY
    // ========================================================

    println("\n========== A13: LAND FLAG x CATEGORY ==========")

    enriched.map { case (row, _, cat) =>
      ((row(6), cat), 1L)
    }.reduceByKey(_ + _)
      .sortByKey()
      .collect()
      .foreach(println)

    // ========================================================
    // A14: AVERAGE DURATION x CATEGORY
    // ========================================================

    println("\n========== A14: AVERAGE DURATION x CATEGORY ==========")

    enriched.map { case (row, _, cat) =>
      (cat, (row(0).toDouble, 1L))
    }.reduceByKey {
      case ((sum1, n1), (sum2, n2)) =>
        (sum1 + sum2, n1 + n2)
    }.mapValues {
      case (sum, n) => sum / n
    }.sortByKey()
      .collect()
      .foreach(println)

    // ========================================================
    // A15: AVERAGE ERROR RATES x CATEGORY
    // ========================================================

    println("\n========== A15: ERROR RATE x CATEGORY ==========")

    enriched.map { case (row, _, cat) =>
      (cat, (row(24).toDouble, row(26).toDouble, 1L))
    }.reduceByKey {
      case ((s1, r1, n1), (s2, r2, n2)) =>
        (s1 + s2, r1 + r2, n1 + n2)
    }.mapValues {
      case (serror, rerror, n) =>
        (serror / n, rerror / n)
    }.sortByKey()
      .collect()
      .foreach(println)

    // ========================================================
    // ADVANCED 1: combineByKey
    // ========================================================

    println("\n========== ADVANCED: COMBINE BY KEY ==========")

    val avgDuration = records
      .map(row => (row(1), row(0).toDouble))
      .combineByKey(
        (value: Double) => (value, 1L),
        (acc: (Double, Long), value: Double) =>
          (acc._1 + value, acc._2 + 1L),
        (left: (Double, Long), right: (Double, Long)) =>
          (left._1 + right._1, left._2 + right._2)
      )
      .mapValues { case (sum, count) => sum / count }

    avgDuration.collect().foreach(println)

    // ========================================================
    // ADVANCED 2: HASH PARTITIONING, PARTITIONS AND LINEAGE
    // ========================================================

    println("\n========== ADVANCED: HASH PARTITIONING ==========")

    val hashPartitioned = records
      .map(row => (row(1), 1L))
      .partitionBy(new HashPartitioner(4))

    println(s"Hash partition count: ${hashPartitioned.getNumPartitions}")
    println(s"Lineage:\n${hashPartitioned.toDebugString}")

    // ========================================================
    // ADVANCED 3: CACHE AND MATERIALIZATION
    // ========================================================

    println("\n========== ADVANCED: CACHE ==========")
    println(s"Cached records: ${enriched.count()}")
    println(s"Cached partitions: ${enriched.getNumPartitions}")

    // ========================================================
    // ADVANCED 4: CUSTOM ATTACK CATEGORY PARTITIONER
    // ========================================================

    println("\n========== ADVANCED: CUSTOM PARTITIONER ==========")

    val categoryPairs = enriched.map {
      case (_, _, cat) => (cat, 1L)
    }

    val customPartitioner = new AttackCategoryPartitioner(5)

    val partitionedCategories =
      categoryPairs.partitionBy(customPartitioner)

    val partitionDistribution = partitionedCategories
      .mapPartitionsWithIndex { (partitionId, iterator) =>
        val counts = scala.collection.mutable.Map.empty[String, Long]

        iterator.foreach { case (cat, _) =>
          counts.update(cat, counts.getOrElse(cat, 0L) + 1L)
        }

        val summary = counts.toSeq
          .sortBy(_._1)
          .map { case (cat, count) => s"$cat=$count" }
          .mkString(", ")

        Iterator(s"Partition $partitionId: $summary")
      }
      .collect()
      .sortBy(_.takeWhile(_ != ':'))

    partitionDistribution.foreach(println)
    println(s"Custom partition count: ${partitionedCategories.getNumPartitions}")

    // ========================================================
    // ADVANCED 5: BROADCAST LOOKUP
    // ========================================================

    println("\n========== ADVANCED: BROADCAST LOOKUP ==========")

    val categoryLookup = sc.broadcast(
      dos.map(_ -> "DoS").toMap ++
      probe.map(_ -> "Probe").toMap ++
      r2l.map(_ -> "R2L").toMap ++
      u2r.map(_ -> "U2R").toMap ++
      Map("normal" -> "Normal")
    )

    val broadcastCategories = attacks
      .map(label => categoryLookup.value.getOrElse(label, "Unknown"))
      .map(cat => (cat, 1L))
      .reduceByKey(_ + _)

    broadcastCategories.collect().foreach(println)

    // ========================================================
    // SAVE REUSABLE ANALYSIS RESULTS
    // ========================================================

    val outputBase = s"out/analysis/run_${System.currentTimeMillis()}"

    def saveResults(name: String, data: RDD[String]): Unit = {
      data.saveAsTextFile(s"$outputBase/$name")
      println(s"Saved $name to $outputBase/$name")
    }

    saveResults(
      "attack_category_counts",
      categoryCounts.map { case (cat, count) => s"$cat,$count" }
    )

    saveResults(
      "protocol_counts",
      records.map(row => (row(1), 1L))
        .reduceByKey(_ + _)
        .map { case (protocol, count) => s"$protocol,$count" }
    )

    saveResults(
      "service_counts",
      records.map(row => (row(2), 1L))
        .reduceByKey(_ + _)
        .map { case (service, count) => s"$service,$count" }
    )

    saveResults(
      "flag_counts",
      records.map(row => (row(3), 1L))
        .reduceByKey(_ + _)
        .map { case (flag, count) => s"$flag,$count" }
    )

    saveResults(
      "protocol_category_counts",
      enriched.map { case (row, _, cat) =>
        ((row(1), cat), 1L)
      }.reduceByKey(_ + _)
        .map { case ((protocol, cat), count) =>
          s"$protocol,$cat,$count"
        }
    )

    saveResults(
      "service_category_counts",
      enriched.map { case (row, _, cat) =>
        ((row(2), cat), 1L)
      }.reduceByKey(_ + _)
        .map { case ((service, cat), count) =>
          s"$service,$cat,$count"
        }
    )

    // Save per-category statistics for analysis and visualization.
    saveResults(
      "category_duration_bytes",
      enriched.map { case (row, _, cat) =>
        (cat, (row(0).toDouble, row(4).toDouble, row(5).toDouble, 1L))
      }.reduceByKey {
        case ((d1, s1, t1, n1), (d2, s2, t2, n2)) =>
          (d1 + d2, s1 + s2, t1 + t2, n1 + n2)
      }.map { case (cat, (duration, src, dst, n)) =>
        s"$cat,${duration / n},${src / n},${dst / n},$n"
      }
    )

    println("\n========== COMPLETED ==========")

    categoryCounts.unpersist()
    enriched.unpersist()
    records.unpersist()
    hashPartitioned.unpersist()
    categoryLookup.destroy()

    spark.stop()
  }
}
