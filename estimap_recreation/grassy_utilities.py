#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author Nikos Alexandris |
"""

import atexit
import os
import grass.script as grass
from grass.exceptions import CalledModuleError
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import raster as r
from grass.pygrass.modules.shortcuts import vector as v

from .colors import SCORE_COLORS

def run(cmd, **kwargs):
    """Pass required arguments to grass commands (?)"""
    grass.run_command(cmd, quiet=True, **kwargs)


def remove_map(map_name):
    """ Remove the provided map """
    grass.verbose("Removing %s" % map_name)
    g.remove(
        flags="f",
        type=("raster", "vector"),
        name=map_name,
        quiet=True,
    )


def remove_map_at_exit(map_name):
    """ Remove the provided map when the program exits """
    atexit.register(lambda: remove_map(map_name))


def remove_files_at_exit(filename):
    """ Remove the specified file when the program exits """
    atexit.register(lambda: os.unlink(filename))


def tmp_map_name(name=None):
    """Return a temporary map name, for example:

    Parameters
    ----------
    name :
        Name of input raster map

    Returns
    -------
    temporary_filename :
        A temporary file name for the input raster map

    Examples
    --------
    >>> tmp_map_name(potential)
    tmp.SomeTemporaryString.potential
    """
    temporary_absolute_filename = grass.tempfile()
    temporary_filename = "tmp." + grass.basename(temporary_absolute_filename)
    if name:
        temporary_filename = temporary_filename + "." + str(name)
    return temporary_filename


def remove_temporary_maps():
    """Clean up temporary maps"""

    # get list of temporary maps
    # temporary_raster_maps = grass.list_strings(
        # type="raster", pattern="tmp.{pid}*".format(pid=os.getpid())
    # )

    # # remove temporary maps
    # if temporary_raster_maps:
    g.message("Removing temporary maps")
    g.remove(
        flags="f",
        type="raster",
        pattern="tmp.{pid}*".format(pid=os.getpid()),
        quiet=True,
    )

    # # remove MASK ? FIXME
    # if grass.find_file(name='MASK', element='cell')['file']:
    #     r.mask(flags='r', verbose=True)


def string_to_file(string, name=None):
    """Split series of strings separated by comma in lines and write as an
    ASCII file

    Parameters
    ----------
    string :
        A string where commas will be replaced by a newline

    name :
        A string for tmp_map_name() to create a temporary file name 'filename'

    Returns
    -------
    filename :
        Name of the ASCII file into where the transformed string is written

    Examples
    --------

    """
    string = string.split(",")
    string = "\n".join(string)
    # string = string.splitlines()
    msg = "String split in lines: {s}".format(s=string)
    grass.debug(_(msg))

    filename = tmp_map_name(name=name)

    # # Use a file-like object instead?
    # import tempfile
    # ascii_file = tempfile.TemporaryFile()

    try:
        ascii_file = open(filename, "w")
        ascii_file.writelines(string)
        # ascii_file.seek(0)  # in case of a file-like object

    # if DEBUG, then do:
    # for line in ascii_file:
    #     grass.debug(_(line.rstrip()))

    except IOError as error:
        print("IOError :", error)
        return

    finally:
        ascii_file.close()
        return filename  # how would that work with a file-like object?
        # Will be removed right after `.close()` -- How to possibly re-use it
        # outside the function?
        # Wrap complete main() in a `try` statement?


def get_univariate_statistics(raster):
    """
    Return and print basic univariate statistics of the input raster map

    Parameters
    ----------
    raster :
        Name of input raster map

    Returns
    -------
    univariate :
        Univariate statistics min, mean, max and variance of the input raster
        map

    Example
    -------
    ...
    """
    univariate = grass.parse_command("r.univar", flags="g", map=raster)
    minimum = univariate["min"]
    mean = univariate["mean"]
    maximum = univariate["max"]
    variance = univariate["variance"]
    msg = "min {mn} | mean {avg} | max {mx} | variance {v}"
    msg = msg.format(mn=minimum, avg=mean, mx=maximum, v=variance)
    grass.verbose(_(msg))
    return univariate


def recode_map(raster, rules, colors, output):
    """Scores a raster map based on a set of category recoding rules.

    This is a wrapper around r.recode

    Parameters
    ----------
    raster :
        Name of input raster map

    rules :
        Rules for r.recode

    colors :
        Color rules for r.colors

    output :
        Name of output raster map

    Returns
    -------
        Does not return any value

    Examples
    --------
    ...
    """
    msg = "Setting NULL cells in {name} map to 0"
    msg = msg.format(name=raster)
    grass.debug(_(msg))

    # ------------------------------------------
    r.null(map=raster, null=0)  # Set NULLs to 0
    msg = "To Do: confirm if setting the '{raster}' map's NULL cells to 0 is right"
    msg = msg.format(raster=raster)
    grass.debug(_(msg))
    # Is this right?
    # ------------------------------------------

    r.recode(input=raster, rules=rules, output=output)

    r.colors(map=output, rules="-", stdin=SCORE_COLORS, quiet=True)

    grass.verbose(_("Scored map {name}:".format(name=raster)))


def float_to_integer(double):
    """Converts an FCELL or DCELL raster map into a CELL raster map

    Parameters
    ----------
    double :
            An 'FCELL' or 'DCELL' type raster map

    Returns
    -------
    This function does not return any value

    Examples
    --------
    ..
    """
    expression = "int({double})"
    expression = expression.format(double=double)
    equation = EQUATION.format(result=double, expression=expression)
    r.mapcalc(equation)
