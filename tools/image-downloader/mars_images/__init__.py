import click

cli = click.Group(name="mars-images")


@cli.command(name="create-cog")
@click.argument("files", type=click.Path(dir_okay=False, exists=True), nargs=-1)
def create_cog(files):
    for file in files:
        print(file)


if __name__ == "__main__":
    cli()
