from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, rand
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, FloatType, DateType

schema = StructType([
    StructField("order_id", IntegerType(), True),
    StructField("customer_id", IntegerType(), True),
    StructField("product_id", IntegerType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("price", FloatType(), True),
    StructField("order_date", DateType(), True)
])

spark = SparkSession.builder.appName("SalesDatasetGenerator").getOrCreate()
df = spark.read.csv("dbfs:/FileStore/tables/sales_data.csv", header=True, inferSchema=False, schema=schema)
df = df.withColumn("price", col("price").cast(FloatType())).withColumn("order_date", col("order_date").cast(DateType()))

