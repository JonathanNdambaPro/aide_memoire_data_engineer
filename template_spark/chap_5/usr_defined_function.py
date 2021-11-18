from pathlib import Path

p = Path(".").resolve()
path_parent_folder = p.parents[0]
path_folder_data = path_parent_folder / "chap_4" / "data"

if __name__ == "__main__":
    if path_folder_data.exists():
        from pyspark.sql import SparkSession
        from pyspark.sql.types import LongType

        spark = SparkSession.builder.appName("SparkSQLExampleApp").getOrCreate()

        csv_file = path_folder_data / "departuredelays.csv"

        df = (
            spark.read.format("csv")
            .option("inferSchema", "true")
            .option("header", "true")
            .load(f"{csv_file}")
        )
        df.createOrReplaceTempView("us_delay_flights_tbl")

        # Create cubed function
        def cubed(s):
            return s * s * s

        # Register UDF
        spark.udf.register("cubed", cubed, LongType())

        query_0 = """SELECT distance, origin, destination 
                     FROM us_delay_flights_tbl WHERE distance > 1000 
                     ORDER BY distance DESC"""

        query_1 = """SELECT cubed(distance), origin, destination 
                     FROM us_delay_flights_tbl WHERE distance > 1000 
                     ORDER BY distance DESC"""

        query_2 = """SELECT cubed(distance), origin, destination 
                     FROM us_delay_flights_tbl WHERE distance > 1000 
                     ORDER BY distance DESC"""

        all_query = [query_0, query_1]

        for query in all_query:
            spark.sql(query).show(10)

    else:
        raise Exception("Le chemin n'existe pas.")
