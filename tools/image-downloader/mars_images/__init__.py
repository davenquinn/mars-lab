import click
from pathlib import Path
from os import environ
from rich.console import Console
from rio_cogeo import cog_translate, cog_profiles, cog_validate
from .config import Config

from .download_hirise import download_hirise

cli = click.Group(name="mars-images")
console = Console()


def _translate(file_path: Path, profile="lzw", profile_options={}, **options):
    """Convert image to COG in place"""

    cfg = Config()
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

    cfg.scratch_dir.mkdir(exist_ok=True)

    out_path = file_path.with_suffix(".tif")
    dst_path = cfg.scratch_dir / out_path.name

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
    cfg = Config()
    file = Path(fn)
    pth = file.relative_to(cfg.data_dir)

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


cli.add_command(download_hirise, "download-hirise")

if __name__ == "__main__":
    cli()
