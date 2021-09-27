from os import path
import click
from click import Group, echo, secho,style
from subprocess import run as _run
from shlex import split
from rich import print
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
        _run(split(command))

def create_cog(infile, outfile):
    scratchdir = "/mars-data/hirise-images/.scratch"
    scratchfile = scratchdir+"/scratch.tif"
    run("mkdir -p", scratchdir)
    run("rm -f", scratchdir)
    run("gdal_translate --config GDAL_CACHEMAX 2048 -of COG -co COMPRESS=LZW -co NUM_THREADS=8 -co BIGTIFF=YES -if JP2OpenJPEG", infile, scratchfile)
    run("mv", scratchfile, outfile)

def import_images(file_list: str, rebuild: bool = False):
    with open(file_list) as f:
        images = [l for l in f.read().splitlines() if not l.startswith("#")]

    greyscale = True
    color = True

    image_files = []

    image_dir = "/mars-data/hirise-images/base-images"
    final_dir = "/mars-data/hirise-images/"

    print("Importing HiRISE images")
    for id in images:
        print(id)

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
            out = path.join(image_dir,f)
            final_file = path.join(final_dir, f.replace(".JP2", ".tif"))
            if path.isfile(final_file):
                fn = style(final_file,fg="cyan")
                echo(f"File {fn} already processed")
                continue

            if path.isfile(out):
                _ = "File {} already downloaded".format(
                    style(out,fg="cyan"))
                echo(_)
            else:
                run("wget","-O",out,url+f)

            base, ext = path.splitext(out)
            vrt = base+".vrt"

            # Ignore label files for geodata processing
            if ext.lower() != '.jp2': continue

            #print("Fixing JPEG2000 georeference")
            #run("fix_jp2", out)

            image_files.append(out)
            print(out)

            # Full-resolution geotiffs
            create_cog(out, final_file)

            print("")

    # for name in ("red","color"):
    #     # Create aggregate VRT files for each type
    #     suffix = "_{}.JP2".format(name.upper())
    #     files = [i for i in image_files if i.endswith(suffix)]

    #     run(
    #         "gdalbuildvrt",
    #         "-overwrite",
    #         '-srcnodata "0"',
    #         '-vrtnodata "0"',
    #         path.join(image_dir,"hirise-{}.vrt".format(name)),
    #         *files)


if __name__ == "__main__":
    typer.run(import_images)