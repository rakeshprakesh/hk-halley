from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit

spark = SparkSession.builder.appName("DataFrame Example").getOrCreate()
schema = ["id", "name", "age"]
sample_data = [(1, "Alice", 30), (2, "Bob", 25), (3, "Charlie", 35)]
df = spark.createDataFrame(sample_data, schema)
df = df.groupBy("age").agg(lit(1).alias("count")).withColumnRenamed("count", "age_count")
df = df.withColumn("age_count", col("age_count") + 1)
df = df.withColumn("age_count", col("age_count") * 2)
df = df.withColumn("age_count", col("age_count") - 1)
df.show()
df.write.mode("overwrite").parquet("output.parquet")