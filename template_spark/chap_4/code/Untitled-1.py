from pathlib import Path

p = Path(".").resolve()
path_parent_folder = p.parent
path_folder_data = path_parent_folder / "data"

if __name__ == "__main__":
    if path_folder_data.exists():
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.appName("SparkSQLExampleApp").getOrCreate()

        csv_file = path_folder_data / "departuredelays.csv"

        df = (
            spark.read.format("csv")
            .option("inferSchema", "true")
            .option("header", "true")
            .load(f"{csv_file}")
        )
        df.createOrReplaceTempView("us_delay_flights_tbl")

        query_1 = """SELECT distance, origin, destination 
                     FROM us_delay_flights_tbl WHERE distance > 1000 
                     ORDER BY distance DESC"""

        query_2 = """SELECT date, delay, origin, destination 
                      FROM us_delay_flights_tbl 
                      WHERE delay > 120 AND ORIGIN = 'SFO' AND DESTINATION = 'ORD' 
                      ORDER by delay DESC"""

        query_3 = """SELECT delay, origin, destination,
                CASE
                  WHEN delay > 360 THEN 'Very Long Delays'
                  WHEN delay > 120 AND delay < 360 THEN 'Long Delays'
                  WHEN delay > 60 AND delay < 120 THEN 'Short Delays'
                  WHEN delay > 0 and delay < 60  THEN  'Tolerable Delays'
                  WHEN delay = 0 THEN 'No Delays'
                  ELSE 'Early'
               END AS Flight_Delays
               FROM us_delay_flights_tbl
               ORDER BY origin, delay DESC"""

        all_query = [query_1, query_2, query_3]

        for query in all_query:
            spark.sql(query).show(10)
    else:
        raise Exception("Le chemin indiue n'existe pas.")
