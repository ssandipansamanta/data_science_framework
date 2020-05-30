import spark.implicits._
import spark.sqlContext.implicits._
import org.apache.spark.sql.functions.{col, count, lit, rank, _}
import org.apache.spark.sql.types.{StructType, StructField, StringType, IntegerType}
import org.apache.spark.sql.Row
import org.apache.spark.sql.hive.HiveContext

val schemaName = "SCHEMA_NAME"
val names = Seq("TABLE_NAME_1","TABLE_NAME_2")

val schemaallTableInformation = StructType(
    StructField("schema_name", StringType, false) ::
    StructField("table_name", StringType, false) ::
    StructField("col_name", StringType, false) ::
    StructField("data_type", StringType, false) ::
    StructField("no_non_null_values", StringType, false) ::
    StructField("no_distinct_values", StringType, false) :: Nil
)

var allTableFieldSummaryInfo = spark.createDataFrame(sc.emptyRDD[Row], schemaallTableInformation)

val schemafieldSummaryInformation = StructType(
    StructField("field_name", StringType, false) ::
    StructField("no_non_null_values", StringType, false) ::
    StructField("no_distinct_values", StringType, false) :: Nil
)

var fieldSummaryInformation = spark.createDataFrame(sc.emptyRDD[Row], schemafieldSummaryInformation)


for (tableNames <- names) {
  
  var tableName = schemaName.concat(".".concat(tableNames))
  var schemaInformation = spark.sql("DESCRIBE " + tableName)
  var schemaInformationRDD = spark.sql("DESCRIBE " + tableName).rdd
  var noFields = schemaInformationRDD.count().toInt
  for(rowsIter <- 0 to (noFields-1)){
  // var rowsIter = 0
    var varTypeInformation = schemaInformationRDD.zipWithIndex.filter(_._2==rowsIter).map(_._1).first().toSeq
    var fieldName = varTypeInformation(0).toString()
    var fieldType = varTypeInformation(1).toString().toUpperCase()
    var noNonMissingRowsRDD = spark.read.table(tableName).agg(count(fieldName).alias("noNonMissingRows")).rdd
    var distinctValuesRDD = spark.read.table(tableName).agg(countDistinct(fieldName).alias("noDistinctValues")).rdd
    var noNonMissingRows = noNonMissingRowsRDD.zipWithIndex.filter(_._2==0).map(_._1).first().toSeq
    var distinctValues = distinctValuesRDD.zipWithIndex.filter(_._2==0).map(_._1).first().toSeq
    var summaryInfo = Seq((fieldName, noNonMissingRows(0).toString(), distinctValues(0).toString()))
    var summaryInfoRDD = spark.sparkContext.parallelize(summaryInfo)
    var summaryData = summaryInfoRDD.toDF()
    fieldSummaryInformation = fieldSummaryInformation.union(summaryData)
  }
    
  val tableFieldSummaryInformation = schemaInformation.as("schemaInfo")
                                                    .join(fieldSummaryInformation.as("fieldSummary"),$"schemaInfo.col_name" === $"fieldSummary.field_name", "left")
                                                    .drop($"fieldSummary.field_name")
                                                    .withColumn("table_name", lit(tableNames))
                                                    .withColumn("schema_name", lit(schemaName))
                                                    .select("schema_name", "table_name","col_name","data_type","no_non_null_values","no_distinct_values")
  
  allTableFieldSummaryInfo = allTableFieldSummaryInfo.union(tableFieldSummaryInformation)
}

allTableFieldSummaryInfo.write.mode("overwrite").saveAsTable("/mention/your/location");
