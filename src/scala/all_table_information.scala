%scala 
import spark.implicits._
import org.apache.spark.sql.functions.{col, count, lit, rank, _}
import org.apache.spark.sql.types.{StructType, StructField, StringType, IntegerType}
import org.apache.spark.sql.Row

val schema = StructType(
    StructField("value", StringType, true) ::
    StructField("table_name", StringType, false) ::
    StructField("schema_name", StringType, false) :: Nil)

var allTable = spark.createDataFrame(sc.emptyRDD[Row], schema) //spark.createDataFrame(spark.sparkContext.emptyRDD[Row], schema)

val schemaName = "SCHEMA_NAME"
val names = Seq("TABLE_NAME_1",	"TABLE_NAME_2")

for (tableNames <- names) {
  val selectTables = spark.read.table(schemaName.concat(".".concat(tableNames))).limit(1)  
  val selectColumns = selectTables.columns.toList
  val columns_df = selectColumns.toDF
  val columnsWithTableName = columns_df.select(col("value"),lit(tableNames).as("table_name"), lit(schemaName).as("schema_name"))
  allTable = allTable.union(columnsWithTableName)
}
