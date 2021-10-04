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
        _run(split(command)