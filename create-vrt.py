from os import path
import click
from click import Group, echo, secho,style
from subprocess import run as _run
from shlex import split
from rich import print
from pathlib import Path
import contextlib
import typer

def run(*command, **kwargs):
    """
    Runs a command safely in the terminal,
    only initializing a subshell if specified.
    """
    shell = kwargs.pop("shell",False)
    command = " ".join(command)
    echo(u"➔ "+style(command,"green"))
    if shell:
        _run(command,shell=True)
    else:
        _run(split(command))

def create_vrt():
    image_dir = "/mars-data/hirise-images/"

    for name in ("red","color"):
        # Create aggregate VRT files for each type
        files = Path(image_dir).glob(f"*_{name.upper()}.tif")

        urls = ["/mars-data/hirise-images/"+f.name for f in files]

        outfile = path.join(image_dir,f"hirise-{name}.vrt")

        run(
            "gdalbuildvrt",
            "-overwrite",
            "-resolution highest",
            "-allow_projection_difference",
            "-srcnodata 0",
            outfile,
            *urls)
        run("gdalinfo -approx_stats", outfile)

        with open(outfile) as f:
            new_text=f.read().replace('<SourceFilename relativeToVRT="1">', "<SourceFilename>http://argyre.geoscience.wisc.edu/hirise-images/")

        with open(outfile, "w") as f:
            f.write(new_text)


if __name__ == "__main__":
    typer.run(create_vrt)