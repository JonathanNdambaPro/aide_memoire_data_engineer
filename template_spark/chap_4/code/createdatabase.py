from pathlib import Path

p = Path(".").resolve()
path_parent_folder = p.parent
path_folder_data = path_parent_folder / "data"

if __name__ == "__main__":
    if path_folder_data.exists():
        # Create managed database
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.appName("SparkSQLExampleApp").getOrCreate()

        spark.sql("CREATE DATABASE learn_spark_db")
        spark.sql("USE learn_spark_db")
        spark.sql(
            """CREATE TABLE managed_us_delay_flights_tbl 
        (date STRING, delay INT, distance INT, origin STRING, destination STRING)"""
        )

        csv_file = path_folder_data / "departuredelays.csv"

        schema = (
            "date STRING, delay INT, distance INT, origin STRING, destination STRING"
        )

        flights_df = spark.read.csv(csv_file, schema=schema)
        flights_df.write.saveAsTable("managed_us_delay_flights_tbl")

        # Create unmanaged database
        spark.sql(
            f"""CREATE TABLE us_delay_flights_tbl(date STRING, delay INT, 
        distance INT, origin STRING, destination STRING) 
        USING csv OPTIONS (PATH {csv_file})"""
        )

        # Create view
        spark.sql(
            f"""CREATE OR REPLACE GLOBAL TEMP VIEW us_origin_airport_SFO_global_tmp_view AS
        SELECT date, delay, origin, destination from us_delay_flights_tbl WHERE 
        origin = 'SFO';"""
        )

        spark.sql(
            f"""SELECT * FROM global_temp.us_origin_airport_SFO_global_tmp_view"""
        )

        spark.sql(f"""DROP VIEW IF EXISTS us_origin_airport_SFO_global_tmp_view;""")

        # OR
        spark.sql(
            f"""CREATE OR REPLACE TEMP VIEW us_origin_airport_JFK_tmp_view AS
        SELECT date, delay, origin, destination from us_delay_flights_tbl WHERE 
        origin = 'JFK'"""
        )

        spark.sql(f"""SELECT * FROM us_origin_airport_JFK_tmp_view""")

        spark.sql(f"""DROP VIEW IF EXISTS us_origin_airport_JFK_tmp_view""")

        # Une vue globale peut etre accessible par plusieurs sessions spark contrairement a une vue simple

        # Acces metadonnees
        spark.catalog.listDatabases()
        spark.catalog.listTables()
        spark.catalog.listColumns("us_delay_flights_tbl")

        # Mise en cache de table (Lazy : mise en cache apres la premiere utilisation)
        try:
            spark.sql(f"""CACHE [LAZY] TABLE <table-name> UNCACHE TABLE <table-name>""")
        except:
            print("Syntaxe uniquement")
    else:
        raise Exception("Le chemin indiue n'existe pas.")
