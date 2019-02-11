#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author Nikos Alexandris |
"""

import grass.script as grass
from grass.exceptions import CalledModuleError
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import raster as r
from grass.pygrass.modules.shortcuts import vector as v

def build_distance_function(constant, kappa, alpha, variable, score=None, suitability=None):
    """
    Build a valid `r.mapcalc` expression based on the following "space-time"
    function:

        ( {constant} + {kappa} ) / ( {kappa} + exp({alpha} * {variable}) )

    Parameters
    ----------
    constant :
        1

    kappa :
        A constant named 'K'

    alpha :
        A constant named 'a'

    variable :
        The main input variable: for 'attractiveness' it is 'distance', for
        'flow' it is 'population'

    score :
        If 'score' is given, it is used as a multiplication factor to the base
        equation.

    suitability :
        [ NOTE: this argument is yet unused!  It is meant to be used only after
        successful integration of land suitability scores in
        build_distance_function(). ]
        If 'suitability' is given, it is used as a multiplication
        factor to the base equation.

    Returns
    -------
    function:
        A valid `r.mapcalc` expression

    Examples
    --------
    ..
    """
    numerator = "{constant} + {kappa}"
    numerator = numerator.format(constant=constant, kappa=kappa)

    denominator = "{kappa} + exp({alpha} * {variable})"
    denominator = denominator.format(
        kappa=kappa, alpha=alpha, variable=variable
    )  # variable "formatted" by a caller function

    function = " ( {numerator} ) / ( {denominator} )"
    function = function.format(numerator=numerator, denominator=denominator)
    grass.debug("Function without score: {f}".format(f=function))

    if score:
        function += " * {score}"  # need for float()?
        function = function.format(score=score)
    grass.debug(_("Function after adding 'score': {f}".format(f=function)))

    # -------------------------------------------------------------------------
    # if suitability:
    #     function += " * {suitability}"  # FIXME : Confirm Correctness
    #     function = function.format(suitability=suitability)
    # msg = "Function after adding 'suitability': {f}".format(f=function)
    # grass.debug(_(msg))
    # -------------------------------------------------------------------------

    return function


def compute_attractiveness(raster, metric, constant, kappa, alpha, mask=None, output_name=None):
    """
    Compute a raster map whose values follow an (euclidean) distance function
    ( {constant} + {kappa} ) / ( {kappa} + exp({alpha} * {distance}) ), where:

    Source: http://publications.jrc.ec.europa.eu/repository/bitstream/JRC87585/lb-na-26474-en-n.pd

    Parameters
    ----------
    constant : 1

    kappa :
        A constant named 'K'

    alpha :
        A constant named 'a'

    distance :
        A distance map based on the input raster

    score :
        A score term to multiply the distance function

    mask :
        Optional raster MASK which is inverted to selectively exclude non-NULL
        cells from distance related computations.

    output_name :
        Name to pass to tmp_map_name() to create a temporary map name

    Returns
    -------
    tmp_output :
        A temporary proximity to features raster map.

    Examples
    --------
    ...

    """
    distance_terms = [
        str(raster),
        str(metric),
        "distance",
        str(constant),
        str(kappa),
        str(alpha),
    ]

    if score:
        grass.debug(_("Score for attractiveness equation: {s}".format(s=score)))
        distance_terms += str(score)

    # tmp_distance = tmp_map_name('_'.join(distance_terms))
    tmp_distance = tmp_map_name(name="_".join([raster, metric]))
    r.grow_distance(
        input=raster, distance=tmp_distance, metric=metric, quiet=True, overwrite=True
    )

    if mask:
        msg = "Inverted masking to exclude non-NULL cells "
        msg += "from distance related computations based on '{mask}'"
        msg = msg.format(mask=mask)
        grass.verbose(_(msg))
        r.mask(raster=mask, flags="i", overwrite=True, quiet=True)

    # FIXME: use a parameters dictionary, avoid conditionals
    if score:
        distance_function = build_distance_function(
            constant=constant,
            kappa=kappa,
            alpha=alpha,
            variable=tmp_distance,
            score=score,
        )

    # FIXME: use a parameters dictionary, avoid conditionals
    if not score:
        distance_function = build_distance_function(
            constant=constant,
            kappa=kappa,
            alpha=alpha,
            variable=tmp_distance
        )

    # temporary maps will be removed
    if output_name:
        tmp_distance_map = tmp_map_name(name=output_name)
    else:
        basename = "_".join([raster, "attractiveness"])
        tmp_distance_map = tmp_map_name(name=basename)

    distance_function = EQUATION.format(
        result=tmp_distance_map, expression=distance_function
    )
    msg = "Distance function: {f}".format(f=distance_function)
    grass.verbose(_(msg))
    grass.mapcalc(distance_function, overwrite=True)

    r.null(map=tmp_distance_map, null=0)  # Set NULLs to 0

    compress_status = grass.read_command("r.compress", flags="g", map=tmp_distance_map)
    grass.verbose(_("Compress status: {s}".format(s=compress_status)))  # REMOVEME

    return tmp_distance_map



