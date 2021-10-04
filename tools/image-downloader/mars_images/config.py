from pathlib import Path
from os import environ


class Config:
    data_dir = Path(environ.get("MARS_DATA_DIR"))
    scratch_dir = Path(environ.get("SCRATCH_DIR", data_dir / ".scratch"))
