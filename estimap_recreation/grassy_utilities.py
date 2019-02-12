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
from .constants import CITATION_RECREATION_POTENTIAL

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


def string_to_file(string, filename=None):
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


def update_meta(raster, title, timestamp=None):
    """
    Update metadata of given raster map

    Parameters
    ----------
    raster :
        ...

    title :
        ...

    Returns
    -------
        Does not return any value

    Examples
    --------
    ...
    """
    history = "\n" + CITATION_RECREATION_POTENTIAL
    description_string = "Recreation {raster} map"
    description = description_string.format(raster=raster)

    title = "{title}".format(title=title)
    units = "Meters"

    source1 = "Source 1"
    source2 = "Source 2"

    r.support(
        map=raster,
        title=title,
        description=description,
        units=units,
        source1=source1,
        source2=source2,
        history=history,
    )

    if timestamp:
        r.timestamp(map=raster, date=timestamp)


def export_map(input_name, title, categories, colors, output_name, timestamp):
    """
    Export a raster map by renaming the (temporary) raster map name
    'input_name' to the requested output raster map name 'output_name'.
    This function is (mainly) used to export either of the intermediate
    recreation 'potential' or 'opportunity' maps.

    Parameters
    ----------
    raster :
        Input raster map name

    title :
        Title for the output raster map

    categories :
        Categories and labels for the output raster map

    colors :
        Colors for the output raster map

    output_name :
        Output raster map name

    Returns
    -------
    output_name :
        This function will return the requested 'output_name'

    Examples
    --------
    ..
    """
    finding = grass.find_file(name=input_name, element="cell")
    if not finding["file"]:
        grass.fatal("Raster map {name} not found".format(name=input_name))

    # inform
    msg = "\nOutputting '{raster}' map\n"
    msg = msg.format(raster=input_name)
    grass.verbose(_(msg))

    # get categories and labels
    temporary_raster_categories_map = tmp_map_name("categories_of_" + input_name)
    raster_category_labels = string_to_file(string=categories,
            filename=temporary_raster_categories_map)

    # add ascii file to removal list
    remove_files_at_exit(raster_category_labels)

    # apply categories and description
    r.category(map=input_name, rules=raster_category_labels, separator=":")

    # update meta and colors
    update_meta(input_name, title, timestamp)
    r.colors(map=input_name, rules="-", stdin=colors, quiet=True)
    # rename to requested output name
    g.rename(raster=(input_name, output_name), quiet=True)

    return output_name


def get_raster_statistics(map_one, map_two, separator, flags):
    """
    Parameters
    ----------
    map_one :
        First map as input to `r.stats`

    map_two :
        Second map as input to `r.stats`

    separator :
        Character to use as separator in `r.stats`

    flags :
        Flags for `r.stats`

    Returns
    -------
    dictionary :
        A nested dictionary that holds categorical statistics for both maps
        'map_one' and 'map_two'.

        - The 'outer_key' is the raster category _and_ label of 'map_one'.
        - The 'inner_key' is the raster map category of 'map_two'.
        - The 'inner_value' is the list of statistics for map two, as returned
          for `r.stats`.

        Example of a nested dictionary:

        {(u'3',
            u'Region 3'):
            {u'1': [
                u'355.747658',
                u'6000000.000000',
                u'6',
                u'6.38%'],
            u'3': [
                u'216304.146140',
                u'46000000.000000',
                u'46',
                u'48.94%'],
            u'2': [
                u'26627.415787',
                u'46000000.000000',
                u'46',
                u'48.94%']}}
    """

    statistics = grass.read_command(
        "r.stats",
        input=(map_one, map_two),
        output="-",
        flags=flags,
        separator=separator,
        quiet=True,
    )
    statistics = statistics.split("\n")[:-1]

    dictionary = dict()

    # build a nested dictionary where:
    for row in statistics:
        row = row.split("|")
        outer_key = (row[0], row[1])
        inner_key = row[2]
        inner_value = row[3:]
        inner_dictionary = {inner_key: inner_value}
        try:
            dictionary[outer_key][inner_key] = inner_value
        except KeyError:
            dictionary[outer_key] = {inner_key: inner_value}

    return dictionary


def smooth_map(raster, method, size):
    """
    Parameters
    ----------
    raster :

    method :

    size :

    Returns
    -------

    Examples
    --------
    """
    r.neighbors(
        input=raster,
        output=raster,
        method=method,
        size=size,
        overwrite=True,
        quiet=True,
    )


def update_vector(vector, raster, methods, column_prefix):
    """

    Parameters
    ----------
    vector :
        Vector map whose attribute table to update with results of the
        v.rast.stats call

    raster :
        Source raster map for statistics

    methods :
        Descriptive statistics for the `v.rast.stats` call

    column_prefix :
        Prefix for the names of the columns created by the `v.rast.stats` call

    Returns
    -------
        This helper function executes `v.rast.stats`. It does not return any
        value.

    Examples
    --------
    ..
    """
    run(
        "v.rast.stats",
        map=vector,
        flags="c",
        raster=raster,
        method=methods,
        column_prefix=column_prefix,
        overwrite=True,
    )
    # grass.verbose(_("Updating vector map '{v}'".format(v=vector)))
