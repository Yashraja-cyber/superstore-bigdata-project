# Superstore Sales Analysis — Big Data Project

A complete end-to-end Big Data analytics pipeline using Apache Spark and Hadoop HDFS to analyze retail sales data, identify profit patterns and predict profitability using machine learning.

---

## Project Overview

This project processes **9,994 retail orders** across 4 geographic regions and 3 product categories to identify:
- Revenue distribution patterns
- Profitability drivers and loss sources
- Impact of discounting on margins
- Predictive modeling of profit using Linear Regression

---

## System Architecture

CSV Dataset (Windows)
↓
VMware Shared Folder
↓
Ubuntu 24.04.2 LTS
↓
Hadoop HDFS (Distributed Storage)
↓
Apache Spark (In-Memory Processing)
↓
Spark SQL (5 Queries) + MLlib (Linear Regression)
↓
Results saved back to HDFS
↓
HTML Report + Charts (PNG)

---

## Project Structure

bigdata-project/
├── SampleSuperstore.csv          # Raw dataset (9,994 rows, 13 columns)
├── superstore_complete.py        # Main Spark script
├── hadoop_website.py             # Website generator
├── architecture.html             # System architecture diagram
├── README.md                     # This file
└── docs/
├── hadoop_website.html       # Final analytics report
└── charts/
├── 1_sales_by_region.png
├── 2_profit_by_category.png
├── 3_top10_subcategory.png
├── 4_discount_vs_profit.png
└── 5_sales_by_shipmode.png

---

## Prerequisites

- Ubuntu 24.04.2 LTS
- Java JDK 11
- Apache Spark 3.5.8
- Hadoop HDFS 3.3.6
- Python 3.12 with pandas, matplotlib, numpy

---

## Installation

### Install Java
```bash
sudo apt install openjdk-11-jdk -y
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
```

### Install Spark
```bash
wget https://archive.apache.org/dist/spark/spark-3.5.8/spark-3.5.8-bin-hadoop3.tgz
tar -xvzf spark-3.5.8-bin-hadoop3.tgz
sudo mv spark-3.5.8-bin-hadoop3 /opt/spark
```

### Install Hadoop
```bash
wget https://downloads.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
tar -xvzf hadoop-3.3.6.tar.gz
sudo mv hadoop-3.3.6 /opt/hadoop
```

### Install Python Libraries
```bash
sudo apt install python3-pandas python3-matplotlib python3-numpy -y
```

---

## Running the Project

### Start Services
```bash
sudo systemctl start ssh
start-dfs.sh
jps
```

### Upload Dataset to HDFS
```bash
hdfs dfs -mkdir -p /user/yashraja/bigdata
hdfs dfs -put SampleSuperstore.csv /user/yashraja/bigdata/
```

### Run Spark Script
```bash
spark-submit superstore_complete.py
```

### Generate Website
```bash
python3 hadoop_website.py
```

---

## Analysis Results

### Key Metrics

| Metric | Value |
|---|---|
| Total Revenue | $2,297,200.86 |
| Net Profit | $286,397.02 |
| Profit Margin | 12.5% |
| Total Orders | 9,994 |
| Profitable Orders | 67.3% |

### SQL Query Results

| Query | Result |
|---|---|
| Top Region | West — $725,457 |
| Top Sub-Category | Copiers — $55,617 profit |
| Biggest Loss | Tables — $17,725 loss |
| Top Ship Mode | Standard Class — 5,968 orders |
| Top Category | Technology — $145,454 profit |

### ML Model Performance

| Metric | Value |
|---|---|
| Algorithm | Linear Regression |
| RMSE | 211.27 |
| R2 Score | 0.2121 |
| Training Records | 8,074 |
| Testing Records | 1,920 |

---

## Key Findings

1. **Discount Impact** — Orders with 40%+ discount average a loss of $96.84 per order
2. **Loss Driver** — Tables recorded $17,725 in cumulative losses
3. **Best Product** — Copiers generated $55,617 profit
4. **Top Region** — West leads with $725,457 revenue
5. **Best Category** — Technology most profitable at $145,454
6. **Shipping** — Standard Class accounts for 59.7% of all orders

---

## Visualizations

| Chart | Description |
|---|---|
| Sales by Region | Revenue distribution across regions |
| Profit by Category | Net profit comparison by category |
| Top 10 Sub-Categories | Best performing product lines |
| Discount vs Profit | Scatter plot showing discount impact |
| Sales by Ship Mode | Shipping method distribution |

---

## Technologies Used

| Technology | Version | Purpose |
|---|---|---|
| Apache Spark | 3.5.8 | Distributed processing |
| Hadoop HDFS | 3.3.6 | Distributed storage |
| Python | 3.12 | Scripting |
| Spark MLlib | 3.5.8 | Machine learning |
| Matplotlib | Latest | Visualization |
| Pandas | Latest | Data manipulation |
| Java JDK | 11 | JVM runtime |
| Ubuntu | 24.04.2 | Operating system |

---

## Author

**Yashraja**

---

## License

This project is for educational purposes.
