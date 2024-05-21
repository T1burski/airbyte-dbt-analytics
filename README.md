# airbyte-dbt-analytics
This is a data engineering project that showcases the use of Airbyte, dbt Cloud and Postgres in the creation of a cloud database to store liquor sales data in the state of Iowa, USA.

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/1ebd3a1b-71cc-46a2-b9c7-aa6faea9ee7b)

## 1) The Challenge

We were approached with the challenge to create an ETL process to build a Data Warehouse (DW) that provides data regarding the sales of liquor in the state of Iowa, USA. There are two analysis the stakeholders desire to see:
### - An analysis of the Revenue (USD) per Volume Sold (L) in each region of the state in the last 5 months along with the comparison of the values obtained with the goals associated with each region;
### - An analysis of the Top 10 product category sold according to the Revenue (USD), containing information such as total volume, units, and revenue per product category.

## 2) The Sources of Data

All the history of sales is located in Google BigQuery, and the goals, per region of the state of Iowa, of Revenue (USD) per Volume Sold (L) is located in a Google Sheets file in which the managers of each Region associate their USD/L goals.

Below, we show how the region goals data in available in Google Sheets:

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/169b432d-19a4-46ef-8679-5ca9c5cc72a3)


## 3) The Tools: ETL and Storage Processes

The final database in which the data was stored to be accessed by the business personnel was PostgreSQL, that was hosted in the cloud using Render, as shown below:

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/eff66dc9-b922-4085-b06f-9ed79ef784eb)

In order to proceed with the data integration process (from BQ and Google Sheets into the PostgreSQL), the Airbyte tool was used. First, we set the Sources (BigQuery and Google Sheets):

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/d6ee10c6-e31c-45c0-bae3-bb1524947b95)

Then, the Destination (PostgreSQL):

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/a7146374-cebd-479d-a067-6f35f6c0f987)

In the end, having the Sources and Destination set, we create the Connections (two are necessary). However, before proceeding with the Sync of the data, we need to create a bronze schema in our PostgreSQL to insert the data in, which was done using DBeaver. After doing so, the Sync processes took place:

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/c43325ae-ad37-4d2c-99f0-c67858c952bd)

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/b7aa236c-e271-4aa1-9748-792cebc59ae1)

Finally, our bronze layer was built:

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/4a585075-9831-45cc-aecb-bcbf8e709a47)

Now, we need to transform/process the data located in the bronze layer (schema) in order to generate consumption ready data in the gold layer so that the business team can apply their analysis, for example, using BI tools such as Power BI.
For this, the tool dbt was used. First, we create our project setup, connecting to our PostgreSQL database and setting the output schema as the gold schema. After, we create three files within the dbt development system along with a native version control system:

An .yml file containing information of the sources we are accessing within our bronze schema:

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/70dd5959-e954-4cfe-8f42-69d19b126a7c)


A .sql query that creates a CTE named 'regions' which will be used afterwards:

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/8e52116e-fdef-452d-a457-5c1bd44f5998)

And finally another .sql query that consumes the previous CTE and data from the bronze layer to create a table that provides the information to satisfy one of the stakeholder's necessities: An analysis of the Revenue (USD) per Volume Sold (L) in each region of the state in the last 5 months along with the comparison of the values obtained with the goals associated with each region:

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/37043016-8596-47dd-af49-645114e5ba5d)

Below, the data lineage within dbt, showing the logic behind the ETL process within it:

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/7b191042-da2b-4b74-a26c-0df3d1fa6772)

Now, regarding the second stakeholder's requirements, we need to create a table that provides an analysis of the Top 10 product category sold according to the Revenue (USD), containing information such as total volume, units, and revenue per product category. We could have easily done this with dbt. However, in order to showcase different ways to complete this task, it was done through SQL commands such as CREATE TABLE and INSERT INTO.

Creating the table:

```sql
CREATE TABLE gold.top_product_categories (
	category_name VARCHAR(255) NOT NULL,
	total_n_sales INT NOT NULL,
	perc_n_sales DECIMAL(10, 2) NOT NULL,
	total_volume_sold_liters DECIMAL(10, 2) NOT NULL,
	perc_volume DECIMAL(10, 2) NOT NULL,
	total_revenue_usd DECIMAL(10, 2) NOT NULL,
	perc_revenue DECIMAL(10, 2) NOT NULL
)
```

Inserting the data into the table:

```sql
WITH total_sales AS (
	SELECT 
		*
	FROM bronze.bigquery_product_analysis
)
INSERT INTO gold.top_product_categories
SELECT
	"category_name",
	SUM("n_sales") AS "total_n_sales",
	ROUND((SUM("n_sales") / (SELECT SUM("n_sales") FROM total_sales))*100, 2) AS "perc_n_sales",
	SUM("sales_volume_l") AS "total_volume_sold_liters",
	ROUND((SUM("sales_volume_l") / (SELECT SUM("sales_volume_l") FROM total_sales))*100, 2) AS "perc_volume",
	SUM("sales_revenue_usd") AS "total_revenue_usd",
	ROUND((SUM("sales_revenue_usd") / (SELECT SUM("sales_revenue_usd") FROM total_sales))*100, 2) AS "perc_revenue"
FROM bronze.bigquery_product_analysis
GROUP BY "category_name"
ORDER BY SUM("sales_revenue_usd") DESC
LIMIT 10
```
We are done with the databse construction!!

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/5175cf8a-d3d1-4480-9a20-c5e10896705f)

Nice!

## 4) Final Pipeline: Orquestration

In order to create the whole pipeline that does the ETL process, from BigQuery + Google Sheets -> Airbyte -> PostgreSQL (bronze) -> dbt -> PostgreSQL (gold), we use Apache Airflow within a Docker Container. The DAGs developed are in this repository and below we can see the graph that describes them. The two Airbyte processes are done in parallel!

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/6c11fb6f-59ac-4be9-b014-480a5fd8ff6b)

## 5) Final Data and Applications:

Now, let's see how the final tables look like:

### Regions' Goals Analysis:

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/478165c5-a344-4237-8a0f-71c0748a56e4)

### Top 10 Product Categories:

![image](https://github.com/T1burski/airbyte-dbt-analytics/assets/100734219/5d80d31f-5fa0-4b1e-88a7-589df2f87561)
