from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from .util import run_sql_file
from .settings import DATABASE

engine = create_engine(DATABASE)
Session = sessionmaker(bind=engine)

here = Path(__file__).parent
fixtures = here / "fixtures"
queries = here / "queries"


def query(fp):
    if not fp.endswith(".sql"):
        fp += ".sql"
    return (queries / fp).open().read()


def database_connection():
    return engine.connect()


def database_session(engine=None):
    if engine is None:
        return Session()
    return sessionmaker(bind=engine)()


def create_fixtures(session):
    for f in fixtures.glob("*.sql"):
        run_sql_file(f, session=session)
