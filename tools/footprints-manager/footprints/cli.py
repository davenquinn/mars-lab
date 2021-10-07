#!/usr/bin/env python
"""
Downloads and imports coverage data for CTX and HiRISE
"""

import click
from rich import print
from pathlib import Path
from click import secho
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import ProgrammingError
from requests import get
from zipfile import ZipFile
from io import BytesIO
from shlex import quote

# External modules
from .settings import CACHE_DIR
from .util import run
from .database import database_connection, database_session, engine, create_fixtures

coverages = dict(ctx=["edr"], hirise=["rdr", "rdrv11"], crism=["trdr"])
mro_index = "https://ode.rsl.wustl.edu/mars/coverageshapefiles/mars/mro"

datadir = CACHE_DIR


def footprint_urls():
    """Generates URLs for PDS coverage files"""
    for inst, types in coverages.items():
        for dsid in types:
            # We don't need the 180º-centered coverage files
            basename = f"mars_mro_{inst}_{dsid}_c0a"
            yield mro_index + f"/{inst}/{dsid}/{basename}.tar.gz"


footprints_cache = Path(CACHE_DIR) / "footprints"
names_cache = Path(CACHE_DIR) / "nomenclature"


def download_footprints():
    secho("Downloading data", fg="green")
    footprints_cache.mkdir(parents=True, exist_ok=True)

    for url in footprint_urls():
        fname = url.split("/")[-1].replace(".tar.gz", ".shp")
        shapefile = footprints_cache / fname
        if shapefile.exists():
            print(f"File [cyan]{shapefile.stem}[/cyan] exists")
        else:
            run(f'curl "{url}" | tar -xz -C "{footprints_cache}"', shell=True)


def download_names():
    names_cache.mkdir(parents=True, exist_ok=True)
    url = "http://planetarynames.wr.usgs.gov/shapefiles/MARS_nomenclature.zip"
    tfile = names_cache / "names.zip"
    shp = names_cache / "MARS_nomenclature.shp"
    if shp.exists():
        print(f"File [cyan]{shp.stem}[/cyan] exists")
    else:
        z = ZipFile(BytesIO(get(url).content))
        z.extractall(names_cache)


def connection_args(url: URL):
    host = url.host
    if host is None:
        host = "localhost"
    args = dict(
        host=url.host or "localhost",
        port=url.port or 5432,
        dbname=url.database,
        user=url.username,
        password=url.password,
    )

    vals = " ".join([f"{k}='{v}'" for k, v in args.items()])

    return f'PG:"{vals}"'


def import_footprints(sources, truncate=False):

    conn = database_connection()
    session = database_session()
    create_fixtures(session)

    pg_conn = connection_args(conn.engine.url)

    if truncate:
        try:
            conn.execute("TRUNCATE TABLE footprints")
        except ProgrammingError:
            pass

    for source in sources:
        run(
            "ogr2ogr",
            "-lco GEOMETRY_NAME=geometry",
            "-nln footprints",
            "-nlt MULTIPOLYGON",
            "-append",
            "-progress",
            "-skipfailures",
            "-f PostgreSQL",
            pg_conn,
            str(source),
        )


def import_names(sources):
    """Import Mars nomenclature"""
    conn = database_connection()
    session = database_session()
    create_fixtures(session)

    pg_conn = connection_args(conn.engine.url)

    try:
        conn.execute("TRUNCATE TABLE nomenclature")
    except ProgrammingError:
        pass

    for source in sources:
        run(
            "ogr2ogr",
            "-lco GEOMETRY_NAME=geometry",
            "-nln nomenclature",
            "-nlt POINT",
            "-progress",
            "-append",
            "-f PostgreSQL",
            pg_conn,
            str(source),
        )


@click.group()
def cli():
    pass


@cli.command(name="import-footprints")
def _import_footprints():
    """Downloads and generates data files"""
    download_footprints()
    all_footprints = footprints_cache.glob("mars_mro_*.shp")
    import_footprints(all_footprints)


@cli.command(name="import-names")
def _import_names():
    download_names()
    import_names(names_cache.glob("*.shp"))


if __name__ == "__main__":
    cli()
