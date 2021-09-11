from os import path
import click
from click import Group, echo, secho,style
from click import echo, style, secho
from subprocess import run as _run
from shlex import split
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


@typer.command()
def import_images(rebuild: bool = False):
    fn = path.join(_,"hirise-images.txt")
    with open(fn) as f:
        images = f.read().splitlines()

    greyscale = True
    color = True

    image_files = []

    message("Importing HiRISE images")
    for id in images:
        header(id)

        dn = path.join(image_dir,id)
        run("mkdir -p",q(dn))

        if rebuild:
            run("rm -f {}/*".format(q(dn)))

        ext = []
        if greyscale:
            ext += ["_RED.JP2", "_RED.LBL"]
        if color:
            ext += ["_COLOR.JP2", "_COLOR.LBL"]
        names = [id+i for i in ext]

        orbit = id[4:10]
        mission = id[0:3]
        orbitrange = "{0}00_{0}99".format(orbit[0:4])
        _ = "http://hirise-pds.lpl.arizona.edu/download/PDS/RDR/{0}/ORB_{1}/{2}/"
        url = _.format(mission, orbitrange, id)

        for f in names:
            out = path.join(dn,f)
            if path.isfile(out):
                _ = "File {} already downloaded".format(
                    style(out,fg="cyan"))
                message(_)
            else:
                run("wget","-O",out,url+f)

            base, ext = path.splitext(out)
            vrt = base+".vrt"

            # Ignore label files for geodata processing
            if ext.lower() != '.jp2': continue

            message("Fixing JPEG2000 georeference")
            run("fix_jp2", out)

            image_files.append(out)

    for name in ("red","color"):
        # Create aggregate VRT files for each type
        suffix = "_{}.JP2".format(name.upper())
        files = [i for i in image_files if i.endswith(suffix)]

        run(
            "gdalbuildvrt",
            "-overwrite",
            '-srcnodata "0"',
            '-vrtnodata "0"',
            path.join(image_dir,"hirise-{}.vrt".format(name)),
            *files)

