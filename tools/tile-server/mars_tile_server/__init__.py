import json
import os

# import click
# import cligj
# import mercantile
# from click_plugins import with_plugins
# from pkg_resources import iter_entry_points

# from cogeo_mosaic import __version__ as cogeo_mosaic_version
# from cogeo_mosaic.backends import MosaicBackend
# from cogeo_mosaic.mosaic import MosaicJSON
from rio_tiler.io import COGReader
from rasterio.vrt import WarpedVRT
from rasterio.crs import CRS
import rasterio
import typer
from typing import List, Dict
from pathlib import Path
from rich import print

cli = typer.Typer()


def get_cog_info(src_path: str, cog: COGReader):
    bounds = cog.bounds
    return {
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [bounds[0], bounds[3]],
                    [bounds[0], bounds[1]],
                    [bounds[2], bounds[1]],
                    [bounds[2], bounds[3]],
                    [bounds[0], bounds[3]],
                ]
            ],
        },
        "properties": {
            "path": src_path,
            "bounds": cog.bounds,
            "minzoom": cog.minzoom,
            "maxzoom": cog.maxzoom,
            "datatype": cog.dataset.meta["dtype"],
        },
        "type": "Feature",
    }


EARTH_RADIUS = 6378137


def fake_earth_crs(crs: CRS) -> CRS:
    data = crs.to_dict()
    radius = data.get("R", None)
    if radius is None:
        raise AttributeError("CRS does not have 'R' parameter...")
    if radius == EARTH_RADIUS:
        return crs
    data["R"] = EARTH_RADIUS
    return CRS.from_dict(data)


def get_dataset_info(src_path: str) -> Dict:
    """Get rasterio dataset meta."""
    with rasterio.open(src_path) as src_dst:
        with WarpedVRT(
            src_dst,
            # Fake an Earth radius.
            src_crs=fake_earth_crs(src_dst.crs),
        ) as vrt_dst:
            with COGReader(None, dataset=vrt_dst) as cog:
                return get_cog_info(str(src_path), cog)


@cli.command()
def create_mosaic(files: List[Path]):
    for file in files:
        print(file)
        info = get_dataset_info(file)
        print(info)


# def create_mosaic(input_files):
#     input_files = [file.strip() for file in input_files if file.strip()]
#     mosaicjson = MosaicJSON.from_urls(
#         input_files,
#         minzoom=minzoom,
#         maxzoom=maxzoom,
#         quadkey_zoom=quadkey_zoom,
#         minimum_tile_cover=min_tile_cover,
#         tile_cover_sort=tile_cover_sort,
#         max_threads=threads,
#         quiet=quiet,
#     )

#     if name:
#         mosaicjson.name = name
#     if description:
#         mosaicjson.description = description
#     if attribution:
#         mosaicjson.attribution = attribution

#     if output:
#         with MosaicBackend(output, mosaic_def=mosaicjson) as mosaic:
#             mosaic.write(overwrite=True)
#     else:
#         click.echo(mosaicjson.json(exclude_none=True))
