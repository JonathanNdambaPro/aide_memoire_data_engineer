from pathlib import Path
import click
import os 

@click.group()
def cli():
    pass


@click.command(help="installation de apache airflow")
@click.option("--install_airflow", default=True, help="installation de airflow local")
def install(install_airflow: bool):
    if install_airflow:
        step = "pip installer apache-airflow"
        os.system(f"{step}")
    else:
        pass


@click.command(help="initialisation de apache airflow")
@click.option("--setup_airflow", default=True, help="installation de airflow local")
def setup(setup_airflow: bool):
    if setup_airflow:
        step_0 = "airflow db init"

        username = str(input("entrer le nom du user pour acceder a l'airflow UI"))
        password = str(input("entrer le mot de passe du user pour acceder a l'airflow UI"))
        first_name = str(input("entrer le prenom du user pour acceder a l'airflow UI"))
        last_name = str(input("entrer le nom d famille du user pour acceder a l'airflow UI"))
        role = 'Admin'
        email = str(input("entrer le email du user pour acceder a l'airflow UI"))

        step_1 = f"""airflow users create 
                    --username {username} \
                    --password {password} \
                    --firstname {first_name} \
                    --lastname {last_name} \
                    --role {role} \
                    --email {email}
                """
        all_step = [step_0, step_1]
        for step in all_step:
            os.system(f"{step}")
    else:
        pass


@click.command(help="deplace script dans le dag")
@click.option("--script_python", default=None, help="""bouge le script python dans le dag pour qu'il soit accessible sur la web UI \n
                                                       si chemin du DAG non definie transfer tous les scripts python du repertoire courant""")
def move_script(script_python: str):
    if isinstance(script_python, str):
        os.system(f"cp {script_python} ~/airflow/dags/")
   
    elif script_python is None:
        current_folder = Path(".").resolve()
        all_file_python = list(current_folder.glob("*.py"))

        for file_python in all_file_python:
            os.system(f"cp {file_python} ~/airflow/dags/")
    else:
        pass


@click.command(help="lance la web UI")
@click.option("--launch", default=True, help="lance la web UI")
def launch_airflow(launch: str):
    if launch:
        os.system(f"airflow webserver & airflow scheduler")
    else:
        pass

cli.add_command(install)
cli.add_command(setup)
cli.add_command(move_script)
cli.add_command(launch_airflow)


if __name__ == "__main__":
    cli()
