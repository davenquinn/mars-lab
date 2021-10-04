from starlette.config import Config

config = Config(".env")

DATABASE = config("DATABASE")
CACHE_DIR = config("CACHE_DIR")
