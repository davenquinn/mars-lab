from subprocess import run as _run
from click import secho
from sqlparse import split, format
from sqlalchemy.exc import ProgrammingError, IntegrityError


def run(*args, **kwargs):
    command = " ".join(args)
    if kwargs.pop("echo", True):
        secho(command, fg="cyan")
    kwargs["shell"] = True
    return _run(command, **kwargs)


# The below functions are stolen from sparrow; we should place them in a utility module


def pretty_print(sql, **kwargs):
    for line in sql.split("\n"):
        for i in ["SELECT", "INSERT", "UPDATE", "CREATE", "DROP", "DELETE", "ALTER"]:
            if not line.startswith(i):
                continue
            start = line.split("(")[0].strip().rstrip(";").replace(" AS", "")
            secho(start, **kwargs)
            return


def run_sql(sql, params=None, session=None):
    if session is None:
        from .database import database_session

        session = database_session()
    queries = split(sql)
    for q in queries:
        sql = format(q, strip_comments=True).strip()
        if sql == "":
            continue
        try:
            session.execute(sql, params=params)
            session.commit()
            pretty_print(sql, dim=True)
        except (ProgrammingError, IntegrityError) as err:
            err = str(err.orig).strip()
            dim = "already exists" in err
            session.rollback()
            pretty_print(sql, fg=None if dim else "red", dim=True)
            if dim:
                err = "  " + err
            secho(err, fg="red", dim=dim)


def run_sql_file(sql_file, **kwargs):
    sql = open(sql_file).read()
    return run_sql(sql, **kwargs)


def run_query_file(sql_file, params=None, session=None):
    if session is None:
        from .database import database_session

        session = database_session()
    sql = open(sql_file).read()
    return session.execute(sql, params=params)
