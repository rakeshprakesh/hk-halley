from pyspark import pipelines as dp
from pyspark.sql.functions import col, lit

dp.create_streaming_table("hk-prod.sales.bronze")

@dp.append_flow(
    name="Sales Data Processing Flow",
    description="A flow to process sales data",
    version="1.0"
)
def process_sales_data(df):
    df = df.withColumn("total_amount", col("quantity") * col("price"))
    df = df.withColumn("discounted_amount", col("total_amount") * lit(0.9))
    return df

@dp.materialized_view(
    name="Sales Data Materialized View",
    description="A materialized view for processed sales data",
    version="1.0"
)
def sales_data_materialized_view(df):
    df = process_sales_data(df)
    return df.select("order_id", "product_id", "quantity", "price", "total_amount", "discounted_amount")