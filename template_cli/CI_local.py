import click
import os


@click.group()
def cli():
    pass


@click.command(help="package la solution")
@click.option("--packaging", default=True, help="Similaire au librarie")
def packaging_solution(packaging: bool):
    if packaging:
        step = "python3 setup.py bdist_wheel"
        os.system(f"{step}")
    else:
        pass


@click.command(help="push la solution sur git ou gitlab")
@click.option("--push", default=True, help="d'abord set le git")
def push_to_git(push: bool):
    if push:
        message_commit = str(input("Git message :"))
        step_1 = "git add ."
        step_2 = f'git commit -m "{message_commit}"'
        setp_3 = "git push"

        all_step_packaging = [step_1, step_2, setp_3]

        for step in all_step_packaging:
            os.system(f"{step}")
    else:
        pass


@click.command(help="Execute toutes les action en un fois")
@click.option(
    "--global_",
    default=True,
    help="convention_code -> packaging_solution -> push_to_git",
)
def global_CI(global_: bool):
    if global_:
        step = "python3 setup.py bdist_wheel"
        os.system(f"{step}")

        message_commit = str(input("Git message :"))
        step_1 = "git add ."
        step_2 = f'git commit -m "{message_commit}"'
        setp_3 = "git push"

        all_step_packaging = [step_1, step_2, setp_3]

        for step in all_step_packaging:
            os.system(f"{step}")
    else:
        pass


cli.add_command(packaging_solution)
cli.add_command(push_to_git)
cli.add_command(global_CI)


if __name__ == "__main__":
    cli()
