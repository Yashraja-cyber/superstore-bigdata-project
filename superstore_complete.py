from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, desc, count, avg
from pyspark.sql.functions import round as spark_round
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml import Pipeline
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import subprocess
import os

HDFS = "hdfs://localhost:9000/user/yashraja/bigdata"
LOCAL_OUT = "/home/yashraja/bigdata-project/output"
CHARTS = f"{LOCAL_OUT}/charts"

os.makedirs(CHARTS, exist_ok=True)

spark = SparkSession.builder \
    .appName("SuperstoreCompleteProject") \
    .master("local[*]") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("\n" + "="*55)
print("   SUPERSTORE BIG DATA PROJECT")
print("="*55)
print(f"📂 Reading from HDFS: {HDFS}/SampleSuperstore.csv")

df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(f"{HDFS}/SampleSuperstore.csv")

print(f"\n✅ Data Loaded from HDFS!")
print(f"   Total Records : {df.count()}")
print(f"   Total Columns : {len(df.columns)}")

df.printSchema()
df.show(5)

df = df.na.drop()
print(f"\n✅ Data Cleaned! Records: {df.count()}")

df.createOrReplaceTempView("superstore")

print("\n--- Sales and Profit by Region ---")
spark.sql("""
    SELECT Region,
           ROUND(SUM(Sales), 2)  AS TotalSales,
           ROUND(SUM(Profit), 2) AS TotalProfit
    FROM superstore
    GROUP BY Region
    ORDER BY TotalSales DESC
""").show()

print("\n--- Top 5 Sub-Categories by Profit ---")
spark.sql("""
    SELECT `Sub-Category`,
           ROUND(SUM(Profit), 2) AS TotalProfit
    FROM superstore
    GROUP BY `Sub-Category`
    ORDER BY TotalProfit DESC
    LIMIT 5
""").show()

print("\n--- Loss-Making Sub-Categories ---")
spark.sql("""
    SELECT `Sub-Category`,
           ROUND(SUM(Profit), 2) AS TotalProfit
    FROM superstore
    GROUP BY `Sub-Category`
    ORDER BY TotalProfit ASC
    LIMIT 5
""").show()

print("\n--- Sales by Ship Mode ---")
spark.sql("""
    SELECT `Ship Mode`,
           COUNT(*)             AS TotalOrders,
           ROUND(SUM(Sales), 2) AS TotalSales
    FROM superstore
    GROUP BY `Ship Mode`
    ORDER BY TotalSales DESC
""").show()

print("\n--- Profit by Category ---")
spark.sql("""
    SELECT Category,
           ROUND(SUM(Sales), 2)    AS TotalSales,
           ROUND(SUM(Profit), 2)   AS TotalProfit,
           ROUND(AVG(Discount), 3) AS AvgDiscount
    FROM superstore
    GROUP BY Category
    ORDER BY TotalProfit DESC
""").show()

df.groupBy("Region", "Category") \
  .agg(
      spark_round(sum("Sales"),  2).alias("TotalSales"),
      spark_round(sum("Profit"), 2).alias("TotalProfit")
  ) \
  .orderBy(desc("TotalProfit")) \
  .write \
  .option("header", "true") \
  .mode("overwrite") \
  .csv(f"{HDFS}/output/sql_results")

print(f"✅ SQL Results saved to HDFS!")
print(f"   Path: {HDFS}/output/sql_results")

segmentIndexer  = StringIndexer(inputCol="Segment",   outputCol="SegmentIdx")
categoryIndexer = StringIndexer(inputCol="Category",  outputCol="CategoryIdx")
regionIndexer   = StringIndexer(inputCol="Region",    outputCol="RegionIdx")
shipmodeIndexer = StringIndexer(inputCol="Ship Mode", outputCol="ShipModeIdx")

assembler = VectorAssembler(
    inputCols=["Sales", "Quantity", "Discount",
               "SegmentIdx", "CategoryIdx",
               "RegionIdx", "ShipModeIdx"],
    outputCol="features"
)

lr = LinearRegression(
    labelCol="Profit",
    featuresCol="features",
    maxIter=10,
    regParam=0.3
)

pipeline = Pipeline(stages=[
    segmentIndexer,
    categoryIndexer,
    regionIndexer,
    shipmodeIndexer,
    assembler,
    lr
])

train, test = df.randomSplit([0.8, 0.2], seed=42)
print(f"\n   Training Records : {train.count()}")
print(f"   Testing Records  : {test.count()}")

print("\n⏳ Training ML Model...")
model = pipeline.fit(train)
print("✅ Model Trained!")

predictions = model.transform(test)

print("\n--- Sample Predictions ---")
predictions.select(
    "Sales", "Quantity", "Discount", "Profit", "prediction"
).show(10)

rmse = RegressionEvaluator(
    labelCol="Profit",
    predictionCol="prediction",
    metricName="rmse").evaluate(predictions)

r2 = RegressionEvaluator(
    labelCol="Profit",
    predictionCol="prediction",
    metricName="r2").evaluate(predictions)

print(f"\n--- Model Performance ---")
print(f"   RMSE  : {float(rmse):.2f}")
print(f"   R2    : {float(r2):.4f}")

predictions.select(
    "Sales", "Quantity", "Discount", "Profit", "prediction"
) \
    .write.option("header", "true") \
    .mode("overwrite") \
    .csv(f"{HDFS}/output/ml_predictions")

print(f"✅ ML Predictions saved to HDFS!")
print(f"   Path: {HDFS}/output/ml_predictions")

spark.stop()
print("\n✅ Spark Session Stopped!")

print("\n📊 Generating Charts from HDFS data...")

subprocess.run([
    "hdfs", "dfs", "-getmerge",
    f"/user/yashraja/bigdata/SampleSuperstore.csv",
    f"{LOCAL_OUT}/data_local.csv"
])

df_pd = pd.read_csv(f"{LOCAL_OUT}/data_local.csv")
df_pd.columns = df_pd.columns.str.strip()
print(f"✅ Data pulled from HDFS for charts! Records: {len(df_pd)}")

region_sales = df_pd.groupby("Region")["Sales"].sum().sort_values(ascending=False)
plt.figure(figsize=(8, 5))
bars = plt.bar(region_sales.index, region_sales.values,
               color=["#2563eb","#7c3aed","#059669","#d97706"])
for bar, val in zip(bars, region_sales.values):
    plt.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + 5000,
             f'${val:,.0f}', ha='center', fontsize=9, fontweight='bold')
plt.title("Total Sales by Region")
plt.xlabel("Region")
plt.ylabel("Total Sales ($)")
plt.tight_layout()
plt.savefig(f"{CHARTS}/1_sales_by_region.png", dpi=150)
plt.close()
print("✅ Chart 1 saved!")

cat_profit = df_pd.groupby("Category")["Profit"].sum().sort_values(ascending=False)
plt.figure(figsize=(8, 5))
bars = plt.bar(cat_profit.index, cat_profit.values,
               color=["#2563eb","#059669","#d97706"])
for bar, val in zip(bars, cat_profit.values):
    plt.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + 500,
             f'${val:,.0f}', ha='center', fontsize=9, fontweight='bold')
plt.title("Total Profit by Category")
plt.xlabel("Category")
plt.ylabel("Total Profit ($)")
plt.tight_layout()
plt.savefig(f"{CHARTS}/2_profit_by_category.png", dpi=150)
plt.close()
print("✅ Chart 2 saved!")

sub_sales = df_pd.groupby("Sub-Category")["Sales"].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(10, 6))
colors = ["#2563eb" if i < 3 else "#64748b" for i in range(len(sub_sales))]
plt.barh(sub_sales.index, sub_sales.values, color=colors)
plt.title("Top 10 Sub-Categories by Sales")
plt.xlabel("Total Sales ($)")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f"{CHARTS}/3_top10_subcategory.png", dpi=150)
plt.close()
print("✅ Chart 3 saved!")

plt.figure(figsize=(9, 5))
colors = ['#ef4444' if p < 0 else '#2563eb' for p in df_pd["Profit"]]
plt.scatter(df_pd["Discount"], df_pd["Profit"],
            alpha=0.3, c=colors, s=10)
plt.title("Discount vs Profit")
plt.xlabel("Discount Rate")
plt.ylabel("Profit ($)")
plt.axhline(y=0, color="black", linestyle="--", linewidth=1.5, label="Zero Profit")
plt.axvline(x=0.4, color="orange", linestyle="--", linewidth=1.5, label="40% Discount")
plt.legend()
plt.tight_layout()
plt.savefig(f"{CHARTS}/4_discount_vs_profit.png", dpi=150)
plt.close()
print("✅ Chart 4 saved!")

ship_sales = df_pd.groupby("Ship Mode")["Sales"].sum()
plt.figure(figsize=(7, 7))
plt.pie(ship_sales.values,
        labels=ship_sales.index,
        autopct="%1.1f%%",
        colors=["#2563eb","#7c3aed","#059669","#d97706"],
        startangle=90,
        wedgeprops=dict(edgecolor='white', linewidth=2))
plt.title("Sales by Ship Mode")
plt.tight_layout()
plt.savefig(f"{CHARTS}/5_sales_by_shipmode.png", dpi=150)
plt.close()
print("✅ Chart 5 saved!")

print("\nUploading charts to HDFS...")
subprocess.run([
    "hdfs", "dfs", "-mkdir", "-p",
    "/user/yashraja/bigdata/output/charts"
])

for i in range(1, 6):
    files = {
        1: "1_sales_by_region.png",
        2: "2_profit_by_category.png",
        3: "3_top10_subcategory.png",
        4: "4_discount_vs_profit.png",
        5: "5_sales_by_shipmode.png"
    }
    subprocess.run([
        "hdfs", "dfs", "-put", "-f",
        f"{CHARTS}/{files[i]}",
        f"/user/yashraja/bigdata/output/charts/{files[i]}"
    ])
    print(f"✅ {files[i]} uploaded to HDFS!")

print("\n" + "="*55)
print("   PROJECT COMPLETE!")
print("="*55)
print(f"📂 Input   : {HDFS}/SampleSuperstore.csv")
print(f"📊 SQL     : {HDFS}/output/sql_results")
print(f"🤖 ML      : {HDFS}/output/ml_predictions")
print(f"📈 Charts  : {HDFS}/output/charts")
print("="*55)
