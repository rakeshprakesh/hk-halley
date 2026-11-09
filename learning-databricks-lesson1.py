from pyspark import pipelines as ldp
from pyspark.sql import SparkSession

@ldp.append_flow(
    name="Sales Data Processing Flow",
    description="A flow to process sales data",
    version="1.0"
)
def process_sales_data(df):
    # Perform data cleaning
    df_cleaned = df.dropna(subset=["sales_amount", "product_id"])
    
    # Perform data transformation
    df_transformed = df_cleaned.withColumn("sales_amount_usd", df_cleaned["sales_amount"] * 1.1)
    
    # Perform data aggregation
    df_aggregated = df_transformed.groupBy("product_id").agg({"sales_amount_usd": "sum"})
    
    return df_aggregated