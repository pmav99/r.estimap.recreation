#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 MODULE:       r.estimap.recreation

 AUTHOR(S):    Nikos Alexandris <nik@nikosalexandris.net>

               First implementation as a collection of Python scripts by
               Grazia Zulian <Grazia.Zulian@ec.europa.eu>

 PURPOSE:      An implementation of the Ecosystem Services Mapping Tool
               (ESTIMAP). ESTIMAP is a collection of spatially explicit models
               to support mapping and modelling of ecosystem services
               at European scale.

 SOURCES:      https://www.bts.gov/archive/publications/journal_of_transportation_and_statistics/volume_04_number_23/paper_03/index

 COPYRIGHT:    Copyright 2018 European Union

               Licensed under the EUPL, Version 1.2 or – as soon they will be
               approved by the European Commission – subsequent versions of the
               EUPL (the "Licence");

               You may not use this work except in compliance with the Licence.
               You may obtain a copy of the Licence at:

               https://joinup.ec.europa.eu/collection/eupl/eupl-text-11-12

               Unless required by applicable law or agreed to in writing,
               software distributed under the Licence is distributed on an
               "AS IS" basis, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
               either express or implied. See the Licence for the specific
               language governing permissions and limitations under the Licence.

               Consult the LICENCE file for details.
"""

from __future__ import print_function

'''Flags'''

#%Module
#%  description: Implementation of ESTIMAP to support mapping and modelling of ecosystem services (Zulian, 2014)
#%  keywords: estimap
#%  keywords: ecosystem services
#%  keywords: recreation potential
#%End

#%flag
#%  key: e
#%  description: Match computational region to extent of land use map
#%end

#%flag
#%  key: f
#%  description: Filter maps in land and natural components before computing recreation maps
#%end

#%flag
#%  key: s
#%  description: Save temporary maps for debugging
#%end

#%flag
#%  key: i
#%  description: Print out citation and other information
#%end

#%flag
#%  key: p
#%  description: Print out results (i.e. supply table), don't export to file
#%end

'''
exclusive: at most one of the options may be given
required: at least one of the options must be given
requires: if the first option is given, at least one of the subsequent options must also be given
requires_all: if the first option is given, all of the subsequent options must also be given
excludes: if the first option is given, none of the subsequent options may be given
collective: all or nothing; if any option is given, all must be given
'''

'''Components section'''

#%option G_OPT_R_INPUT
#% key: land
#% type: string
#% key_desc: name
#% label: Input map scoring access to and suitability of land resources for recreation
#% description: Arbitrary number of maps scoring access to and land resources suitability of land use classes to support recreation activities
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: natural
#% key_desc: name
#% label: Input maps scoring access to and quality of inland natural resources
#% description: Arbitrary number of maps scoring access to and quality of inland natural resources
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: water
#% key_desc: name
#% label: Input maps scoring access to and quality of water resources
#% description: Arbitrary number of maps scoring access to and quality of water resources such as lakes, sea, bathing waters and riparian zones
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: urban
#% key_desc: name
#% description: Input maps scoring recreational value of urban surfaces
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: infrastructure
#% type: string
#% key_desc: name
#% label: Input maps scoring infrastructure to reach locations of recreation activities
#% description: Infrastructure to reach locations of recreation activities [required to derive recreation spectrum map]
#% required: no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: recreation
#% type: string
#% key_desc: name
#% label: Input maps scoring recreational facilities, amenities and services
#% description: Recreational opportunities facilities, amenities and services [required to derive recreation spectrum map]
#% required: no
#% guisection: Components
#%end

'''Land'''

#%option G_OPT_R_INPUT
#% key: landuse
#% type: string
#% key_desc: name
#% label: Input land features map from which to derive suitability for recreation
#% description: Input to derive suitability of land use classes to support recreation activities. Requires scores, overrides suitability.
#% required : no
#% guisection: Land
#%end

#%rules
#%  exclusive: land
#%end

#%option G_OPT_F_INPUT
#% key: suitability_scores
#% type: string
#% key_desc: filename
#% label: Input recreational suitability scores for the categories of the 'landuse' map
#% description: Scores for suitability of land to support recreation activities. Expected are rules for `r.recode` that correspond to categories of the input 'landuse' map. If the 'landuse' map is given and 'suitability_scores not provided, the module will use internal rules for the CORINE land classes.
#% required: no
#% guisection: Land
#%end

#%rules
#%  excludes: land, suitability_scores
#%end

#%option G_OPT_R_INPUT
#% key: landcover
#% type: string
#% key_desc: name
#% label: Input land cover map from which to derive cover percentages within zones of high recreational value
#% description: Input to derive percentage of land classes within zones of high recreational value.
#% required : no
#% guisection: Land
#%end

#%option G_OPT_F_INPUT
#% key: land_classes
#% type: string
#% key_desc: filename
#% label: Input reclassification rules for the classes of the 'landcover' map
#% description: Expected are rules for `r.reclass` that correspond to classes of the input 'landcover' map. If 'landcover' map is given and 'land_classess' not provided, the module will use internal rules for the Urban Atlas land classes
#% required: no
#% guisection: Land
#%end

'''Water'''

#%option G_OPT_R_INPUT
#% key: lakes
#% key_desc: name
#% label: Input map of inland waters resources for which to score accessibility
#% description: Map of inland water resources to compute proximity for, score accessibility based on a distance function
#% required : no
#% guisection: Water
#%end

#%option
#% key: lakes_coefficients
#% type: string
#% key_desc: Coefficients
#% label: Input distance function coefficients for the 'lakes' map
#% description: Distance function coefficients to compute proximity: distance metric, constant, kappa, alpha and score. Refer to the manual for details.
#% multiple: yes
#% required: no
#% guisection: Water
#% answer: euclidean,1,30,0.008,1
#%end

##%rules
##%  requires: lakes, lakes_coefficients
##%end

#%option G_OPT_R_INPUT
#% key: coastline
#% key_desc: name
#% label: Input sea coast map for which to compute proximity
#% description: Input map to compute coast proximity, scored based on a distance function
#% required : no
#% guisection: Water
#%end

#%option
#% key: coastline_coefficients
#% key_desc: Coefficients
#% label: Input distance function coefficients for the 'coastline' map
#% description: Distance function coefficients to compute proximity: distance metric, constant, kappa, alpha and score. Refer to the manual for details.
#% multiple: yes
#% required: no
#% guisection: Water
#% answer: euclidean,1,30,0.008,1
#%end

#%rules
#%  requires: coastline, coastline_coefficients
#%end

#%option G_OPT_R_INPUT
#% key: coast_geomorphology
#% key_desc: name
#% label: Input map scoring recreation potential in coast
#% description: Coastal geomorphology, scored as suitable to support recreation activities
#% required : no
#% guisection: Water
#%end

#%rules
#%  requires: coast_geomorphology, coastline
#%end

##%option
##% key: geomorphology_coefficients
##% key_desc: Coefficients
##% label: Input distance function coefficients
##% description: Distance function coefficients to compute proximity: distance metric, constant, kappa, alpha and score. Refer to the manual for details.
##% multiple: yes
##% required: no
##% guisection: Water
##% answer: euclidean,1,30,0.008,1
##%end

##%rules
##%  requires: coast_geomorphology, geomorphology_coefficients
##%end

#%option G_OPT_R_INPUT
#% key: bathing_water
#% key_desc: name
#% label: Input bathing water quality map
#% description: Bathing water quality index. The higher, the greater is the recreational value.
#% required : no
#% guisection: Water
#%end

#%option
#% key: bathing_coefficients
#% type: string
#% key_desc: Coefficients
#% label: Input distance function coefficients for the 'bathing_water' map
#% description: Distance function coefficients to compute proximity to bathing waters: distance metric, constant, kappa and alpha. Refer to the manual for details.
#% multiple: yes
#% required: no
#% guisection: Water
#% answer: euclidean,1,5,0.01101
#%end

#%rules
#%  requires: bathing_water, bathing_coefficients
#%end

##%rules
##%  exclusive: lakes
##%  exclusive: coastline
##%  excludes: water, coast_geomorphology, coast_proximity, marine, lakes, lakes_proximity, bathing_water
##%end

'''Natural'''

#%option G_OPT_R_INPUT
#% key: protected
#% key_desc: filename
#% label: Input protected areas map
#% description: Input map depicting natural protected areas
#% required : no
#% guisection: Natural
#%end

#%option G_OPT_R_INPUT
#% key: protected_scores
#% type: string
#% key_desc: rules
#% label: Input recreational value scores for the classes of the 'protected' map
#% description: Scores for recreational value of designated areas. Expected are rules for `r.recode` that correspond to classes of the input land use map. If the 'protected' map is given and 'protected_scores' are not provided, the module will use internal rules for the IUCN categories.
#% required : no
#% guisection: Anthropic
#% answer: 11:11:0,12:12:0.6,2:2:0.8,3:3:0.6,4:4:0.6,5:5:1,6:6:0.8,7:7:0,8:8:0,9:9:0
#%end

##%rules
##% exclusive: natural, protected
##% exclusive: protected, natural
###% requires: protected, protected_scores
##%end

'''Artificial areas'''

#%option G_OPT_R_INPUT
#% key: artificial
#% key_desc: name
#% label: Input map of artificial surfaces
#% description: Partial input map to compute proximity to artificial areas, scored via a distance function
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: artificial_distances
#% type: string
#% key_desc: rules
#% label: Input distance classification rules
#% description: Categories for distance to artificial surfaces. Expected are rules for `r.recode` that correspond to distance values in the 'artificial' map
#% required : no
#% guisection: Anthropic
#% answer: 0:500:1,500.000001:1000:2,1000.000001:5000:3,5000.000001:10000:4,10000.00001:*:5
#%end

#%rules
#%  requires: artificial, artificial_distances
#%end

'''Roads'''

#%option G_OPT_R_INPUT
#% key: roads
#% key_desc: name
#% label: Input map of primary road network
#% description: Input map to compute roads proximity, scored based on a distance function
#% required : no
#% guisection: Infrastructure
#%end

#%option G_OPT_R_INPUT
#% key: roads_distances
##% key: roads_scores
#% type: string
#% key_desc: rules
#% label: Input distance classification rules
#% description: Categories for distance to roads. Expected are rules for `r.recode` that correspond to distance values in the roads map
#% required : no
#% guisection: Anthropic
#% answer: 0:500:1,500.000001:1000:2,1000.000001:5000:3,5000.000001:10000:4,10000.00001:*:5
#%end

#%rules
#%  requires: roads, roads_distances
#%  collective: artificial, roads
#%end

'''Recreation'''

#######################################################################
# Offer input for potential?

# #%option G_OPT_R_OUTPUT
# #% key: recreation_potential
# #% key_desc: name
# #% description: Recreation potential map
# #% required: no
# #% answer: recreation_potential
# #% guisection: Components
# #%end

#
#######################################################################

## Review the following item's "parsing rules"!

##%rules
##%  excludes: infrastructure, roads
##%end

'''Devaluation'''

#%option G_OPT_R_INPUTS
#% key: devaluation
#% key_desc: name
#% label: Input map of devaluing elements
#% description: Maps hindering accessibility to and degrading quality of various resources or infrastructure relating to recreation
#% required : no
#% guisection: Devaluation
#%end

'''MASK'''

#%option G_OPT_R_INPUT
#% key: mask
#% key_desc: name
#% description: A raster map to apply as a MASK
#% required : no
#%end

'''Output'''

#%option G_OPT_R_OUTPUT
#% key: potential
#% key_desc: name
#% label: Output map of recreation potential
#% description: Recreation potential map classified in 3 categories
#% required: no
#% guisection: Output
#%end

#%rules
#%  requires: potential, land, natural, water, landuse, protected, lakes, coastline
#%end

#%option G_OPT_R_OUTPUT
#% key: opportunity
#% key_desc: name
#% label: Output intermediate map of recreation opportunity
#% description: Intermediate step in deriving the 'spectrum' map, classified in 3 categories, meant for expert use
#% required: no
#% guisection: Output
#%end

#%rules
#%  requires: opportunity, infrastructure, roads
#%end

#%option G_OPT_R_OUTPUT
#% key: spectrum
#% key_desc: name
#% label: Output map of recreation spectrum
#% description: Recreation spectrum map classified by default in 9 categories
#% required: no
#% guisection: Output
#%end

#%rules
#%  requires: spectrum, infrastructure, roads
##%  requires: spectrum, landcover
#%  required: land, landcover, landuse
#%end

#%option G_OPT_R_INPUT
#% key: spectrum_distances
#% type: string
#% key_desc: rules
#% label: Input distance classification rules for the 'spectrum' map
#% description: Classes for distance to areas of high recreational spectrum. Expected are rules for `r.recode` that correspond to classes of the input spectrum of recreation use map.
#% required : no
#% guisection: Output
#% answer: 0:1000:1,1000:2000:2,2000:3000:3,3000:4000:4,4000:*:5
#%end

'''Required for Cumulative Opportunity Model'''

#%option G_OPT_R_INPUT
#% key: base
#% key_desc: name
#% description: Input base map for zonal statistics
#% required : no
#%end

#%option G_OPT_V_INPUT
#% key: base_vector
#% key_desc: name
#% description: Input base vector map for zonal statistics
#% required : no
#%end

#%option G_OPT_R_INPUT
#% key: aggregation
#% key_desc: name
#% description: Input map of regions over which to aggregate the actual flow
#% required : no
#%end

#%option G_OPT_R_INPUT
#% key: population
#% key_desc: name
#% description: Input map of population density
#% required : no
#%end

#%option G_OPT_R_OUTPUT
#% key: demand
#% type: string
#% key_desc: name
#% label: Output map of demand distribution
#% description: Demand distribution output map: population density per Local Administrative Unit and areas of high recreational value
#% required : no
#% guisection: Output
#%end

#%option G_OPT_R_OUTPUT
#% key: unmet
#% type: string
#% key_desc: name
#% label: Output map of unmet demand distribution
#% description: Unmet demand distribution output map: population density per Local Administrative Unit and areas of high recreational value
#% required : no
#% guisection: Output
#%end

#%rules
#%  requires_all: demand, population, base
#%  requires: demand, infrastructure, artificial, roads
#%  requires: unmet, demand
#%end

#%option G_OPT_R_OUTPUT
#% key: flow
#% type: string
#% key_desc: name
#% label: Output map of flow
#% description: Flow output map: population (per Local Administrative Unit) near areas of high recreational value
#% required : no
#% guisection: Output
#%end

#%rules
#%  requires_all: flow, population, base
#%  requires: flow, infrastructure, artificial, roads
#%end

#%option G_OPT_F_OUTPUT
#% key: supply
#% key_desc: prefix
#% type: string
#% label: Output prefix for the file name of the supply table CSV
#% description: Supply table CSV output file names will get this prefix
#% multiple: no
#% required: no
#% guisection: Output
#%end

#%option G_OPT_F_OUTPUT
#% key: use
#% key_desc: prefix
#% type: string
#% label: Output prefix for the file name of the supply table CSV
#% description: Supply table CSV output file names will get this prefix
#% multiple: no
#% required: no
#% guisection: Output
#%end

#%rules
#%  requires: opportunity, spectrum, demand, flow, supply
#%  required: potential, spectrum, demand, flow, supply, use
#%end

#%rules
#%  requires: supply, land, natural, water, landuse, protected, lakes, coastline
#%  requires_all: supply, population
#%  requires_all: supply, landcover, land_classes
#%  requires: supply, base, base_vector, aggregation
#%  requires: supply, landcover, landuse
#%  requires_all: use, population
#%  requires: use, base, base_vector, aggregation
#%  requires: use, landcover, landuse
#%end

'''Various'''

#%option
#% key: metric
#% key_desc: Metric
#% label: Distance metric to areas of highest recreation opportunity spectrum
#% description: Distance metric to areas of highest recreation opportunity spectrum
#% multiple: yes
#% options: euclidean,squared,maximum,manhattan,geodesic
#% required: no
#% guisection: Output
#% answer: euclidean
#%end

#%option
#% key: units
#% key_desc: Units
#% label: Units to report
#% description: Units to report the demand distribution
#% multiple: yes
#% options: mi,me,k,a,h,c,p
#% required: no
#% guisection: Output
#% answer: k
#%end

#%option
#% key: timestamp
#% type: string
#% label: Timestamp
#% description: Timestamp for the recreation potential raster map
#% required: no
#%end

# required librairies

import datetime
import math
import os
import subprocess
import sys
import time

from pprint import pprint as pp

if "GISBASE" not in os.environ:
    g.message(_("You must be in GRASS GIS to run this program."))
    sys.exit(1)

from estimap_recreation.grassy_utilities import *
from estimap_recreation.colors import *
from estimap_recreation.constants import *
from estimap_recreation.labels import *

from estimap_recreation.utilities import *
from estimap_recreation.distance_functions import *
from estimap_recreation.normalisation_functions import *
from estimap_recreation.accessibility_functions import *
from estimap_recreation.spectrum_functions import *
from estimap_recreation.components import *
from estimap_recreation.mobility_functions import *
from estimap_recreation.supply_and_use_functions import *

# helper functions

def neighborhood_function(raster, method, size, distance_map):
    """
    Parameters
    ----------
    raster :
        Name of input raster map for which to apply r.neighbors

    method :
        Method for r.neighbors

    size :
        Size for r.neighbors

    distance :
        A distance map

    Returns
    -------
    filtered_output :
        A neighborhood filtered raster map

    Examples
    --------
    ...
    """
    r.null(map=raster, null=0)  # Set NULLs to 0

    neighborhood_output = distance_map + "_" + method
    msg = "Neighborhood operator '{method}' and size '{size}' for map '{name}'"
    msg = msg.format(method=method, size=size, name=neighborhood_output)
    grass.verbose(_(msg))

    r.neighbors(
        input=raster,
        output=neighborhood_output,
        method=method,
        size=size,
        overwrite=True,
    )

    scoring_function = "{neighborhood} * {distance}"
    scoring_function = scoring_function.format(
        neighborhood=neighborhood_output, distance=distance_map
    )

    filtered_output = distance_map
    filtered_output += "_" + method + "_" + str(size)

    neighborhood_function = EQUATION.format(
        result=filtered_output, expression=scoring_function
    )
    # ---------------------------------------------------------------
    grass.debug(_("Expression: {e}".format(e=neighborhood_function)))
    # ---------------------------------------------------------------
    grass.mapcalc(neighborhood_function, overwrite=True)

    # tmp_distance_map = filtered_output

    # r.compress(distance_map, flags='g')


    return filtered_output


def compute_artificial_proximity(raster, distance_categories, output_name=None):
    """
    Compute proximity to artificial surfaces

    1. Distance to features
    2. Classify distances

    Parameters
    ----------
    raster :
        Name of input raster map

    distance_categories :
        Category rules to recode the input distance map

    output_name :
        Name to pass to tmp_map_name() to create a temporary map name

    Returns
    -------
    tmp_output :
        Name of the temporary output map for internal, in-script, re-use

    Examples
    --------
    ...
    """
    artificial_distances = tmp_map_name(name=raster)

    grass.run_command(
        "r.grow.distance",
        input=raster,
        distance=artificial_distances,
        metric=EUCLIDEAN,
        quiet=True,
        overwrite=True,
    )

    # temporary maps will be removed
    if output_name:
        tmp_output = tmp_map_name(name=output_name)
        grass.debug(_("Pre-defined output map name {name}".format(name=tmp_output)))

    else:
        tmp_output = tmp_map_name(name="artificial_proximity")
        grass.debug(_("Hardcoded temporary map name {name}".format(name=tmp_output)))

    msg = "Computing proximity to '{mapname}'"
    msg = msg.format(mapname=raster)
    grass.verbose(_(msg))
    grass.run_command(
        "r.recode",
        input=artificial_distances,
        output=tmp_output,
        rules=distance_categories,
        overwrite=True,
    )

    output = grass.find_file(name=tmp_output, element="cell")
    if not output["file"]:
        grass.fatal("Proximity map {name} not created!".format(name=raster))
    #     else:
    #         g.message(_("Output map {name}:".format(name=tmp_output)))

    return tmp_output


def main():
    """
    Main program
    """

    """Flags and Options"""
    options, flags = grass.parser()

    # Flags that are not being used
    info = flags["i"]
    save_temporary_maps = flags["s"]

    # Flags that are being used
    average_filter = flags["f"]
    landuse_extent = flags["e"]
    print_only = flags["p"]

    timestamp = options["timestamp"]

    metric = options["metric"]
    units = options["units"]
    if len(units) > 1:
        units = units.split(",")

    """names for input, output, output suffix, options"""

    mask = options["mask"]

    """
    following some hard-coded names -- review and remove!
    """

    land = options["land"]
    land_component_map_name = tmp_map_name(name="land_component")

    water = options["water"]
    water_component_map_name = tmp_map_name(name="water_component")

    natural = options["natural"]
    natural_component_map_name = tmp_map_name(name="natural_component")

    urban = options["urban"]
    urban_component_map = "urban_component"

    infrastructure = options["infrastructure"]
    infrastructure_component_map_name = tmp_map_name(name="infrastructure_component")

    recreation = options["recreation"]
    recreation_component_map_name = tmp_map_name(name="recreation_component")

    """Land components"""

    landuse = options["landuse"]
    if landuse:
        # Check datatype: a land use map should be categorical, i.e. of type CELL
        landuse_datatype = grass.raster.raster_info(landuse)["datatype"]
        if landuse_datatype != "CELL":
            msg = (
                "The '{landuse}' input map "
                "should be a categorical one "
                "and of type 'CELL'. "
                "Perhaps you meant to use the 'land' input option instead?"
            )
            grass.fatal(_(msg.format(landuse=landuse)))

    suitability_map_name = tmp_map_name(name="suitability")
    suitability_scores = options["suitability_scores"]

    if landuse and suitability_scores and ":" not in suitability_scores:
        msg = "Suitability scores from file: {scores}."
        msg = msg.format(scores=suitability_scores)
        grass.verbose(_(msg))

    if landuse and not suitability_scores:
        msg = "Using internal rules to score land use classes in '{map}'"
        msg = msg.format(map=landuse)
        grass.warning(_(msg))

        suitability_scores = string_to_file(
            SUITABILITY_SCORES, name=suitability_map_name
        )
        remove_files_at_exit(suitability_scores)

    if landuse and suitability_scores and ":" in suitability_scores:
        msg = "Using provided string of rules to score land use classes in {map}"
        msg = msg.format(map=landuse)
        grass.verbose(_(msg))
        suitability_scores = string_to_file(
            suitability_scores, name=suitability_map_name
        )
        remove_files_at_exit(suitability_scores)

    # FIXME -----------------------------------------------------------------

    # Use one landcover input if supply is requested
    # Use one set of land cover reclassification rules

    landcover = options["landcover"]

    if not landcover:
        landcover = landuse
        msg = "Land cover map 'landcover' not given. "
        msg += "Attempt to use the '{landuse}' map to derive areal statistics"
        msg = msg.format(landuse=landuse)
        grass.verbose(_(msg))

    maes_ecosystem_types = "maes_ecosystem_types"
    maes_ecosystem_types_scores = "maes_ecosystem_types_scores"
    landcover_reclassification_rules = options["land_classes"]

    # if 'land_classes' is a file
    if (
        landcover
        and landcover_reclassification_rules
        and ":" not in landcover_reclassification_rules
    ):
        msg = "Land cover reclassification rules from file: {rules}."
        msg = msg.format(rules=landcover_reclassification_rules)
        grass.verbose(_(msg))

    # if 'land_classes' not given
    if landcover and not landcover_reclassification_rules:

        # if 'landcover' is not the MAES land cover,
        # then use internal reclassification rules
        # how to test:
        # 1. landcover is not a "MAES" land cover
        # 2. landcover is an Urban Atlas one?

        msg = "Using internal rules to reclassify the '{map}' map"
        msg = msg.format(map=landcover)
        grass.verbose(_(msg))

        landcover_reclassification_rules = string_to_file(
            URBAN_ATLAS_TO_MAES_NOMENCLATURE, name=maes_ecosystem_types
        )
        remove_files_at_exit(landcover_reclassification_rules)

        # if landcover is a "MAES" land cover, no need to reclassify!

    if (
        landuse
        and landcover_reclassification_rules
        and ":" in landcover_reclassification_rules
    ):
        msg = "Using provided string of rules to reclassify the '{map}' map"
        msg = msg.format(map=landcover)
        grass.verbose(_(msg))
        landcover_reclassification_rules = string_to_file(
            landcover_reclassification_rules, name=maes_land_classes
        )
        remove_files_at_exit(landcover_reclassification_rules)

    # FIXME -----------------------------------------------------------------

    """Water components"""

    lakes = options["lakes"]
    lakes_coefficients = options["lakes_coefficients"]
    lakes_proximity_map_name = "lakes_proximity"
    coastline = options["coastline"]
    coast_proximity_map_name = "coast_proximity"
    coast_geomorphology = options["coast_geomorphology"]
    # coast_geomorphology_coefficients = options['geomorphology_coefficients']
    coast_geomorphology_map_name = "coast_geomorphology"
    bathing_water = options["bathing_water"]
    bathing_water_coefficients = options["bathing_coefficients"]
    bathing_water_proximity_map_name = "bathing_water_proximity"

    """Natural components"""

    protected = options["protected"]
    protected_scores = options["protected_scores"]
    protected_areas_map_name = "protected_areas"

    """Artificial areas"""

    artificial = options["artificial"]
    artificial_proximity_map_name = "artificial_proximity"
    artificial_distance_categories = options["artificial_distances"]

    roads = options["roads"]
    roads_proximity_map_name = "roads_proximity"
    roads_distance_categories = options["roads_distances"]

    artificial_accessibility_map_name = "artificial_accessibility"

    """Devaluation"""

    devaluation = options["devaluation"]

    """Aggregational boundaries"""

    base = options["base"]
    base_vector = options["base_vector"]
    aggregation = options["aggregation"]

    """Population"""

    population = options["population"]
    if population:
        population_ns_resolution = grass.raster_info(population)["nsres"]
        population_ew_resolution = grass.raster_info(population)["ewres"]

    """Outputs"""

    potential_title = "Recreation potential"
    recreation_potential = options["potential"]  # intermediate / output
    recreation_potential_map_name = tmp_map_name(name="recreation_potential")

    opportunity_title = "Recreation opportunity"
    recreation_opportunity = options["opportunity"]
    recreation_opportunity_map_name = "recreation_opportunity"

    spectrum_title = "Recreation spectrum"
    # if options['spectrum']:
    recreation_spectrum = options["spectrum"]  # output
    # else:
    #     recreation_spectrum = 'recreation_spectrum'
    # recreation_spectrum_component_map_name =
    #       tmp_map_name(name='recreation_spectrum_component_map')

    spectrum_distance_categories = options["spectrum_distances"]
    if ":" in spectrum_distance_categories:
        spectrum_distance_categories = string_to_file(
            spectrum_distance_categories, name=recreation_spectrum
        )
        remove_files_at_exit(spectrum_distance_categories)

    highest_spectrum = "highest_recreation_spectrum"
    crossmap = "crossmap"  # REMOVEME

    demand = options["demand"]
    unmet_demand = options["unmet"]

    flow = options["flow"]
    flow_map_name = "flow"

    supply = options["supply"]  # use as CSV filename prefix
    use = options["use"]  # use as CSV filename prefix

    """ First, care about the computational region"""

    if mask:
        msg = "Masking NULL cells based on '{mask}'".format(mask=mask)
        grass.verbose(_(msg))
        r.mask(raster=mask, overwrite=True, quiet=True)

    if landuse_extent:
        grass.use_temp_region()  # to safely modify the region
        g.region(flags="p", raster=landuse)  # Set region to 'mask'
        msg = "|! Computational resolution matched to {raster}"
        msg = msg.format(raster=landuse)
        g.message(_(msg))

    """Land Component
            or Suitability of Land to Support Recreation Activities (SLSRA)"""

    land_component = []  # a list, use .extend() wherever required

    if land:

        land_component = land.split(",")

    if landuse and suitability_scores:

        msg = "Deriving land suitability from '{landuse}' "
        msg += "based on rules described in file '{rules}'"
        grass.verbose(msg.format(landuse=landuse, rules=suitability_scores))

        # suitability is the 'suitability_map_name'
        recode_map(
            raster=landuse,
            rules=suitability_scores,
            colors=SCORE_COLORS,
            output=suitability_map_name,
        )

        append_map_to_component(
            raster=suitability_map_name,
            component_name="land",
            component_list=land_component,
        )

    """Water Component"""

    water_component = []
    water_components = []

    if water:

        water_component = water.split(",")
        msg = "Water component includes currently: {component}"
        msg = msg.format(component=water_component)
        grass.debug(_(msg))
        # grass.verbose(_(msg))

    if lakes:

        if lakes_coefficients:
            metric, constant, kappa, alpha, score = get_coefficients(lakes_coefficients)

        lakes_proximity = compute_attractiveness(
            raster=lakes,
            metric=EUCLIDEAN,
            constant=constant,
            kappa=kappa,
            alpha=alpha,
            score=score,
            mask=lakes,
        )

        append_map_to_component(
            raster=lakes_proximity,
            component_name="water",
            component_list=water_components,
        )

    if coastline:

        coast_proximity = compute_attractiveness(
            raster=coastline,
            metric=EUCLIDEAN,
            constant=WATER_PROXIMITY_CONSTANT,
            alpha=WATER_PROXIMITY_ALPHA,
            kappa=WATER_PROXIMITY_KAPPA,
            score=WATER_PROXIMITY_SCORE,
        )

        append_map_to_component(
            raster=coast_proximity,
            component_name="water",
            component_list=water_components,
        )

    if coast_geomorphology:

        try:

            if not coastline:
                msg = "The coastline map is required in order to "
                msg += "compute attractiveness based on the "
                msg += "coast geomorphology raster map"
                msg = msg.format(c=water_component)
                grass.fatal(_(msg))

        except NameError:
            grass.fatal(_("No coast proximity"))

        coast_attractiveness = neighborhood_function(
            raster=coast_geomorphology,
            method=NEIGHBORHOOD_METHOD,
            size=NEIGHBORHOOD_SIZE,
            distance_map=coast_proximity,
        )

        append_map_to_component(
            raster=coast_attractiveness,
            component_name="water",
            component_list=water_components,
        )

    if bathing_water:

        if bathing_water_coefficients:
            metric, constant, kappa, alpha = get_coefficients(
                bathing_water_coefficients
            )

        bathing_water_proximity = compute_attractiveness(
            raster=bathing_water,
            metric=EUCLIDEAN,
            constant=constant,
            kappa=kappa,
            alpha=alpha,
        )

        append_map_to_component(
            raster=bathing_water_proximity,
            component_name="water",
            component_list=water_components,
        )

    # merge water component related maps in one list
    water_component += water_components

    """Natural Component"""

    natural_component = []
    natural_components = []

    if natural:

        natural_component = natural.split(",")

    if protected:
        msg = "Scoring protected areas '{protected}' based on '{rules}'"
        grass.verbose(_(msg.format(protected=protected, rules=protected_scores)))

        protected_areas = protected_areas_map_name

        recode_map(
            raster=protected,
            rules=protected_scores,
            colors=SCORE_COLORS,
            output=protected_areas,
        )

        append_map_to_component(
            raster=protected_areas,
            component_name="natural",
            component_list=natural_components,
        )

    # merge natural resources component related maps in one list
    natural_component += natural_components

    """ Normalize land, water, natural inputs
    and add them to the recreation potential component"""

    recreation_potential_component = []

    if land_component:

        for dummy_index in land_component:

            # remove 'land_map' from 'land_component'
            # process and add it back afterwards
            land_map = land_component.pop(0)

            """
            This section sets NULL cells to 0.
            Because `r.null` operates on the complete input raster map,
            manually subsetting the input map is required.
            """
            suitability_map = tmp_map_name(name=land_map)
            subset_land = EQUATION.format(result=suitability_map, expression=land_map)
            r.mapcalc(subset_land)

            grass.debug(_("Setting NULL cells to 0"))  # REMOVEME ?
            r.null(map=suitability_map, null=0)  # Set NULLs to 0

            msg = "\nAdding land suitability map '{suitability}' "
            msg += "to 'Recreation Potential' component\n"
            msg = msg.format(suitability=suitability_map)
            grass.verbose(_(msg))

            # add 'suitability_map' to 'land_component'
            land_component.append(suitability_map)

    if len(land_component) > 1:
        grass.verbose(_("\nNormalize 'Land' component\n"))
        zerofy_and_normalise_component(
            land_component, THRESHHOLD_ZERO, land_component_map_name
        )
        recreation_potential_component.extend(land_component)
    else:
        recreation_potential_component.extend(land_component)

    if land_component and average_filter:
        smooth_component(land_component, method="average", size=7)

    remove_map_at_exit(land_component)

    if len(water_component) > 1:
        grass.verbose(_("\nNormalize 'Water' component\n"))
        zerofy_and_normalise_component(
            water_component, THRESHHOLD_ZERO, water_component_map_name
        )
        recreation_potential_component.append(water_component_map_name)
    else:
        recreation_potential_component.extend(water_component)

    remove_map_at_exit(water_component_map_name)

    if len(natural_component) > 1:
        grass.verbose(_("\nNormalize 'Natural' component\n"))
        zerofy_and_normalise_component(
            components=natural_component,
            threshhold=THRESHHOLD_ZERO,
            output_name=natural_component_map_name,
        )
        recreation_potential_component.append(natural_component_map_name)
    else:
        recreation_potential_component.extend(natural_component)

    if natural_component and average_filter:
        smooth_component(natural_component, method="average", size=7)

    remove_map_at_exit(natural_component_map_name)

    """ Recreation Potential [Output] """

    tmp_recreation_potential = tmp_map_name(name=recreation_potential_map_name)

    msg = "Computing intermediate 'Recreation Potential' map: '{potential}'"
    grass.verbose(_(msg.format(potential=tmp_recreation_potential)))
    grass.debug(_("Maps: {maps}".format(maps=recreation_potential_component)))

    zerofy_and_normalise_component(
        components=recreation_potential_component,
        threshhold=THRESHHOLD_ZERO,
        output_name=tmp_recreation_potential,
    )

    # recode recreation_potential
    tmp_recreation_potential_categories = tmp_map_name(name=recreation_potential)

    msg = "\nClassifying '{potential}' map"
    msg = msg.format(potential=tmp_recreation_potential)
    grass.verbose(_(msg))

    classify_recreation_component(
        component=tmp_recreation_potential,
        rules=RECREATION_POTENTIAL_CATEGORIES,
        output_name=tmp_recreation_potential_categories,
    )

    if recreation_potential:

        # export 'recreation_potential' map and
        # use 'output_name' for the temporary 'potential' map for spectrum
        tmp_recreation_potential_categories = export_map(
            input_name=tmp_recreation_potential_categories,
            title=potential_title,
            categories=POTENTIAL_CATEGORY_LABELS,
            colors=POTENTIAL_COLORS,
            output_name=recreation_potential,
            timestamp=timestamp,
        )

    # Infrastructure to access recreational facilities, amenities, services
    # Required for recreation opportunity and successively recreation spectrum

    if infrastructure and not any(
        [recreation_opportunity, recreation_spectrum, demand, flow, supply]
    ):
        msg = (
            "Infrastructure is not required "
            "to derive the 'potential' recreation map."
        )
        grass.warning(_(msg))

    if any([recreation_opportunity, recreation_spectrum, demand, flow, supply]):

        infrastructure_component = []
        infrastructure_components = []

        if infrastructure:
            infrastructure_component.append(infrastructure)

        """Artificial surfaces (includung Roads)"""

        if artificial and roads:

            msg = "Roads distance categories: {c}"
            msg = msg.format(c=roads_distance_categories)
            grass.debug(_(msg))
            roads_proximity = compute_artificial_proximity(
                raster=roads,
                distance_categories=roads_distance_categories,
                output_name=roads_proximity_map_name,
            )

            msg = "Artificial distance categories: {c}"
            msg = msg.format(c=artificial_distance_categories)
            grass.debug(_(msg))
            artificial_proximity = compute_artificial_proximity(
                raster=artificial,
                distance_categories=artificial_distance_categories,
                output_name=artificial_proximity_map_name,
            )

            artificial_accessibility = compute_artificial_accessibility(
                artificial_proximity,
                roads_proximity,
                output_name=artificial_accessibility_map_name,
            )

            infrastructure_components.append(artificial_accessibility)

        # merge infrastructure component related maps in one list
        infrastructure_component += infrastructure_components

    # # Recreational facilities, amenities, services

    # recreation_component = []
    # recreation_components = []

    # if recreation:
    #     recreation_component.append(recreation)

    # # merge recreation component related maps in one list
    # recreation_component += recreation_components

    """ Recreation Spectrum """

    if any([recreation_spectrum, demand, flow, supply]):

        recreation_opportunity_component = []

        # input
        zerofy_and_normalise_component(
            components=infrastructure_component,
            threshhold=THRESHHOLD_ZERO,
            output_name=infrastructure_component_map_name,
        )

        recreation_opportunity_component.append(infrastructure_component_map_name)

        # # input
        # zerofy_and_normalise_component(recreation_component,
        #         THRESHHOLD_0001, recreation_component_map_name)
        # recreation_opportunity_component.append(recreation_component_map_name)
        # remove_map_at_exit(recreation_component_map_name)

        # intermediate

        # REVIEW --------------------------------------------------------------
        tmp_recreation_opportunity = tmp_map_name(name=recreation_opportunity_map_name)
        msg = "Computing intermediate opportunity map '{opportunity}'"
        grass.debug(_(msg.format(opportunity=tmp_recreation_opportunity)))

        grass.verbose(_("\nNormalize 'Recreation Opportunity' component\n"))
        grass.debug(_("Maps: {maps}".format(maps=recreation_opportunity_component)))

        zerofy_and_normalise_component(
            components=recreation_opportunity_component,
            threshhold=THRESHHOLD_0001,
            output_name=tmp_recreation_opportunity,
        )

        # Why threshhold 0.0003? How and why it differs from 0.0001?
        # -------------------------------------------------------------- REVIEW

        msg = "Classifying '{opportunity}' map"
        grass.verbose(msg.format(opportunity=tmp_recreation_opportunity))

        # recode opportunity_component
        tmp_recreation_opportunity_categories = tmp_map_name(
            name=recreation_opportunity
        )

        classify_recreation_component(
            component=tmp_recreation_opportunity,
            rules=RECREATION_OPPORTUNITY_CATEGORIES,
            output_name=tmp_recreation_opportunity_categories,
        )

        """ Recreation Opportunity [Output]"""

        if recreation_opportunity:

            # export 'recreation_opportunity' map and
            # use 'output_name' for the temporary 'potential' map for spectrum
            tmp_recreation_opportunity_categories = export_map(
                input_name=tmp_recreation_opportunity_categories,
                title=opportunity_title,
                categories=OPPORTUNITY_CATEGORY_LABELS,
                colors=OPPORTUNITY_COLORS,
                output_name=recreation_opportunity,
                timestamp=timestamp,
            )

        # Recreation Spectrum: Potential + Opportunity [Output]

        if not recreation_spectrum and any([demand, flow, supply]):
            recreation_spectrum = tmp_map_name(name="recreation_spectrum")
            remove_map_at_exit(recreation_spectrum)

        recreation_spectrum = compute_recreation_spectrum(
            potential=tmp_recreation_potential_categories,
            opportunity=tmp_recreation_opportunity_categories,
            spectrum=recreation_spectrum,
        )

        msg = "Writing '{spectrum}' map"
        msg = msg.format(spectrum=recreation_spectrum)
        grass.verbose(_(msg))
        get_univariate_statistics(recreation_spectrum)

        # get category labels
        spectrum_categories = "categories_of_"
        spectrum_categories += recreation_spectrum
        spectrum_category_labels = string_to_file(
            SPECTRUM_CATEGORY_LABELS, name=spectrum_categories
        )

        # add to list for removal
        remove_files_at_exit(spectrum_category_labels)

        # update category labels, meta and colors
        spectrum_categories = "categories_of_"

        r.category(
            map=recreation_spectrum, rules=spectrum_category_labels, separator=":"
        )

        update_meta(recreation_spectrum, spectrum_title)

        r.colors(map=recreation_spectrum, rules="-", stdin=SPECTRUM_COLORS, quiet=True)

        if base_vector:
            update_vector(
                vector=base_vector,
                raster=recreation_spectrum,
                methods=METHODS,
                column_prefix="spectrum",
            )

    """Valuation Tables"""

    if any([demand, flow, supply, aggregation]):

        """Highest Recreation Spectrum == 9"""

        expression = (
            "if({spectrum} == {highest_recreation_category}, {spectrum}, null())"
        )
        highest_spectrum_expression = expression.format(
            spectrum=recreation_spectrum,
            highest_recreation_category=HIGHEST_RECREATION_CATEGORY,
        )
        highest_spectrum_equation = EQUATION.format(
            result=highest_spectrum, expression=highest_spectrum_expression
        )
        r.mapcalc(highest_spectrum_equation, overwrite=True)

        """Distance map"""

        distance_to_highest_spectrum = tmp_map_name(name=highest_spectrum)
        r.grow_distance(
            input=highest_spectrum,
            distance=distance_to_highest_spectrum,
            metric=metric,
            quiet=True,
            overwrite=True,
        )

        """Distance categories"""

        distance_categories_to_highest_spectrum = "categories_of_"
        distance_categories_to_highest_spectrum += distance_to_highest_spectrum
        remove_map_at_exit(distance_categories_to_highest_spectrum)  # FIXME

        recode_map(
            raster=distance_to_highest_spectrum,
            rules=spectrum_distance_categories,
            colors=SCORE_COLORS,
            output=distance_categories_to_highest_spectrum,
        )

        spectrum_distance_category_labels = string_to_file(
            SPECTRUM_DISTANCE_CATEGORY_LABELS,
            name=distance_categories_to_highest_spectrum,
        )
        remove_files_at_exit(spectrum_distance_category_labels)

        r.category(
            map=distance_categories_to_highest_spectrum,
            rules=spectrum_distance_category_labels,
            separator=":",
        )

        """Combine Base map and Distance Categories"""

        tmp_crossmap = tmp_map_name(name=crossmap)
        r.cross(
            input=(distance_categories_to_highest_spectrum, base),
            flags="z",
            output=tmp_crossmap,
            quiet=True,
        )

        grass.use_temp_region()  # to safely modify the region
        g.region(
            nsres=population_ns_resolution, ewres=population_ew_resolution, flags="a"
        )  # Resolution should match 'population' FIXME
        msg = "|! Computational extent & resolution matched to {raster}"
        msg = msg.format(raster=landuse)
        grass.verbose(_(msg))

        population_statistics = get_univariate_statistics(population)
        population_total = population_statistics['sum']
        msg = "|i Population statistics: {s}".format(s=population_total)
        grass.verbose(_(msg))

        """Demand Distribution"""

        if any([flow, supply, aggregation]) and not demand:
            demand = tmp_map_name(name="demand")

        r.stats_zonal(
            base=tmp_crossmap,
            flags="r",
            cover=population,
            method="sum",
            output=demand,
            overwrite=True,
            quiet=True,
        )

        # copy 'reclassed' as 'normal' map (r.mapcalc)
        # so as to enable removal of it and its 'base' map
        demand_copy = demand + "_copy"
        copy_expression = "{input_raster}"
        copy_expression = copy_expression.format(input_raster=demand)
        copy_equation = EQUATION.format(result=demand_copy, expression=copy_expression)
        r.mapcalc(copy_equation, overwrite=True)

        # remove the reclassed map 'demand'
        g.remove(flags="f", type="raster", name=demand, quiet=True)

        # rename back to 'demand'
        g.rename(raster=(demand_copy, demand), quiet=True)

        if demand and base_vector:
            update_vector(
                vector=base_vector,
                raster=demand,
                methods=METHODS,
                column_prefix="demand",
            )

        """Unmet Demand"""

        if unmet_demand:

            # compute unmet demand

            unmet_demand_expression = compute_unmet_demand(
                distance=distance_categories_to_highest_spectrum,
                constant=MOBILITY_CONSTANT,
                coefficients=MOBILITY_COEFFICIENTS[4],
                population=demand,
                score=MOBILITY_SCORE,
            )
            # suitability=suitability)  # Not used.
            # Maybe it can, though, after successfully testing its
            # integration to build_distance_function().

            grass.debug(
                _("Unmet demand function: {f}".format(f=unmet_demand_expression))
            )

            unmet_demand_equation = EQUATION.format(
                result=unmet_demand, expression=unmet_demand_expression
            )
            r.mapcalc(unmet_demand_equation, overwrite=True)

            if base_vector:
                update_vector(
                    vector=base_vector,
                    raster=unmet_demand,
                    methods=METHODS,
                    column_prefix="unmet",
                )

        """Mobility function"""

        if not flow and any([supply, aggregation]):

            flow = flow_map_name
            remove_map_at_exit(flow)

        if flow or any([supply, aggregation]):

            mobility_expression = mobility_function(
                distance=distance_categories_to_highest_spectrum,
                constant=MOBILITY_CONSTANT,
                coefficients=MOBILITY_COEFFICIENTS,
                population=demand,
                score=MOBILITY_SCORE,
            )
            # suitability=suitability)  # Not used.
            # Maybe it can, though, after successfully testing its
            # integration to build_distance_function().

            msg = "Mobility function: {f}"
            grass.debug(_(msg.format(f=mobility_expression)))

            """Flow map"""

            mobility_equation = EQUATION.format(
                result=flow, expression=mobility_expression
            )
            r.mapcalc(mobility_equation, overwrite=True)

            if base_vector:
                update_vector(
                    vector=base_vector,
                    raster=flow_map_name,
                    methods=METHODS,
                    column_prefix="flow",
                )

    """Supply Table"""

    if aggregation:

        supply_parameters = {}

        if supply:
            supply_parameters.update({"supply_filename": supply})

        if use:
            supply_parameters.update({"use_filename": use})

        if base_vector:
            supply_parameters.update({"vector": base_vector})

        compute_supply(
            base=landcover,
            recreation_spectrum=recreation_spectrum,
            highest_spectrum=highest_spectrum,
            base_reclassification_rules=landcover_reclassification_rules,
            reclassified_base=maes_ecosystem_types,
            reclassified_base_title="MAES ecosystem types",
            flow=flow,
            flow_map_name=flow_map_name,
            aggregation=aggregation,
            ns_resolution=population_ns_resolution,
            ew_resolution=population_ew_resolution,
            print_only=print_only,
            **supply_parameters
        )

    # restore region
    if landuse_extent:
        grass.del_temp_region()  # restoring previous region settings
        grass.verbose("Original Region restored")

    # print citation
    citation = "Citation: " + CITATION_RECREATION_POTENTIAL
    grass.verbose(citation)


if __name__ == "__main__":
    atexit.register(remove_temporary_maps)
    sys.exit(main())
