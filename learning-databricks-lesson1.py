from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, rand
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, FloatType, DateType
from pyspark import pipelines as dp

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
df = spark.read.parquet("abfss://raw@storageaccountname.dfs.core.windows.net/sales_data.parquet")
df = df.withColumn("order_date", col("order_date").cast(DateType()))
df = df.withColumn("price", col("price").cast(FloatType()))
df = df.withColumn("quantity", col("quantity").cast(IntegerType()))

@dp.pipeline(
    name="Sales Data Processing Pipeline",
    description="A pipeline to process sales data",
    version="1.0"
    )   
def process_sales_data(df):
    df = df.withColumn("total_amount", col("quantity") * col("price"))
    df = df.withColumn("discounted_amount", col("total_amount") * lit(0.9))
    return df
df = df.withColumn("quantity", col("quantity").cast(IntegerType()))
df = df.withColumn("price", col("price").cast(FloatType()))
