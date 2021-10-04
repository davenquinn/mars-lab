import click
from pathlib import Path
from os import environ
from rich.console import Console
from rio_cogeo import cog_translate, cog_profiles, cog_validate
from shell_utils import run
from requests import get

cli = click.Group(name="mars-images")
console = Console()

mars_data_dir = Path(environ.get("MARS_DATA_DIR"))
scratch_dir = Path(environ.get("SCRATCH_DIR", mars_data_dir / ".scratch"))


def _translate(file_path: Path, profile="lzw", profile_options={}, **options):
    """Convert image to COG in place"""
    # Format creation option (see gdalwarp `-co` option)
    output_profile = cog_profiles.get(profile)
    output_profile.update(dict(BIGTIFF="IF_SAFER"))
    output_profile.update(profile_options)

    # Dataset Open option (see gdalwarp `-oo` option)
    config = dict(
        GDAL_NUM_THREADS="ALL_CPUS",
        GDAL_TIFF_INTERNAL_MASK=True,
        GDAL_TIFF_OVR_BLOCKSIZE="128",
    )

    scratch_dir.mkdir(exist_ok=True)

    out_path = file_path.with_suffix(".tif")
    dst_path = scratch_dir / out_path.name

    cog_translate(
        file_path,
        dst_path,
        output_profile,
        config=config,
        in_memory=False,
        quiet=False,
        **options,
    )

    is_valid = cog_validate(dst_path, strict=True)[0]
    if not is_valid:
        console.print("Did not create a valid COG")
        dst_path.unlink()
        return

    if file_path.suffix == ".tif":
        if not options.pop("overwrite", True):
            file_path.rename(file_path.with_suffix(".source.tif"))
        else:
            file_path.unlink()
    dst_path.rename(out_path)


def create_cog(fn):
    file = Path(fn)
    pth = file.relative_to(mars_data_dir)

    console.print(str(pth.parent) + "/", style="dim", end="")
    console.print(pth.name, style="bold cyan")
    if pth.suffix == ".tif":
        res = cog_validate(file, strict=True)[0]
        if res:
            console.print("File is a COG already.", style="green")
            return
        else:
            console.print("File is not a COG.", style="red")
    _translate(file)

    console.print("")


@cli.command(name="process-to-cog")
@click.argument("files", type=click.Path(dir_okay=False, exists=True), nargs=-1)
def create_cogs(files):
    console.print("Processing files to COG", style="bold green")
    for file in files:
        create_cog(file)


if __name__ == "__main__":
    cli()
