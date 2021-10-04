import click

mars_images = click.Group(name="mars-images")


@mars_images.command(name="create-cog")
@click.argument("file", type=click.File(exists=True))
def create_cog(file):
    print(file)


if __name__ == "__main__":
    mars_images()
