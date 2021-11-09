from typing import List
from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from cogeo_mosaic.mosaic import MosaicJSON
from cogeo_mosaic.cache import cache_config
from cogeo_mosaic.backends import BaseBackend
from morecantile import tms, Tile
from geoalchemy2.functions import ST_MakeEnvelope, ST_SetSRID
from sqlalchemy import and_, desc
from sparrow.utils import get_logger
from titiler.core.utils import Timer

import attr
from .defs import mars_tms
from .util import MarsCOGReader, data_to_rgb
from .database import get_database


mercator_tms = tms.get("WebMercatorQuad")

log = get_logger(__name__)


def elevation_path():
    return "/mars-data/global-dems/Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.cog.tif"


def get_datasets(tile: Tile, mosaic: str):
    bounds = mars_tms.bounds(tile)

    db = get_database()

    Dataset = db.model.imagery_dataset

    datasets = (
        db.session.query(Dataset)
        .filter(Dataset.mosaic == mosaic)
        .filter(
            Dataset.footprint.ST_Intersects(
                ST_SetSRID(ST_MakeEnvelope(*bounds), 949900)
            )
        )
        .filter(Dataset.minzoom <= tile.z)
        .order_by(desc(Dataset.maxzoom))
    )
    _datasets = datasets.all()
    log.info(bounds)
    log.info([d.path for d in _datasets])

    return _datasets


@attr.s
class MarsMosaicBackend(BaseBackend):
    mosaicid: str = "hirise_red"

    def __attrs_post_init__(self):
        self.reader = MarsCOGReader

    def _get_assets(self, tile: Tile) -> List[str]:
        return [d.path for d in get_datasets(tile, self.mosaicid)]

    @cached(
        TTLCache(maxsize=cache_config.maxsize, ttl=cache_config.ttl),
        key=lambda self, x, y, z: hashkey(self.mosaicid, x, y, z),
    )
    def get_assets(self, x: int, y: int, z: int) -> List[str]:
        with Timer() as t:
            assets = self._get_assets(Tile(x, y, z))
        log.info(f"Got assets for tile {z}/{x}/{y}: took {t.elapsed:.2f}s")
        return assets

    def _read(self):
        return MosaicJSON(
            mosaicjson="", minzoom=0, maxzoom=18, tiles=[], quadkey_zoom=10
        )

    def write(self, overwrite=False):
        pass


@attr.s
class ElevationMosaicBackend(MarsMosaicBackend):
    mosaicid: str = "elevation_model"

    def _get_assets(self, tile: Tile) -> List[str]:
        if tile.z < 10:
            return [elevation_path()]
        return [d.path for d in get_datasets(tile, self.mosaicid)]

    def tile(self, *args, **kwargs):
        im, assets = super().tile(*args, **kwargs)
        im.data = data_to_rgb(im.data[0], -10000, 0.1)
        return (im, assets)
