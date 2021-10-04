import click

cli = click.Group(name="mars-images")


@cli.command(name="create-cog")
@click.argument("file", type=click.Path(dir_okay=False, exists=True))
def create_cog(file):
    print(file)


if __name__ == "__main__":
    cli()
