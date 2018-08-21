#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 MODULE:       r.estimap.recreation

 AUTHOR(S):    Nikos Alexandris <nik@nikosalexandris.net>

               Grazia Zulian <Grazia.Zulian@ec.europa.eu>
               First scripted implementation in Python

 PURPOSE:      An implementation of the Ecosystem Services Mapping Tool
               (ESTIMAP). ESTIMAP is a collection of spatially explicit models
               to support mapping and modelling of ecosystem services
               at European scale.

 SOURCES:      https://www.bts.gov/archive/publications/journal_of_transportation_and_statistics/volume_04_number_23/paper_03/index

 COPYRIGHT:    (C) 2017 by the GRASS Development Team

               This programme is released under the European Union Public
               Licence v 1.1. Please consult the LICENCE file for details.
"""

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
#%  description: Filter input map before...
#%end

#%flag
#%  key: d
#%  description: Draw maps in terminology (developper's version)
#%end

#%flag
#%  key: s
#%  description: Save temporary maps for debugging
#%end

#%flag
#%  key: i
#%  description: Print out citation and other information
#%end

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
#% label: Input land featurs map from which to derive suitability for recreation
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

'''Anthropic areas'''

#%option G_OPT_R_INPUT
#% key: anthropic
#% key_desc: name
#% label: Input map of artificial surfaces
#% description: Partial input map to compute anthropic areas proximity, scored via a distance function
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: anthropic_distances
#% type: string
#% key_desc: rules
#% label: Input distance classification rules
#% description: Categories for distance to anthropic surfaces. Expected are rules for `r.recode` that correspond to distance values in the 'anthropic' map
#% required : no
#% guisection: Anthropic
#% answer: 0:500:1,500.000001:1000:2,1000.000001:5000:3,5000.000001:10000:4,10000.00001:*:5
#%end

#%rules
#%  requires: anthropic, anthropic_distances
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
#%  collective: anthropic, roads
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
#% description: A raster map to apply as an inverted MASK
#% required : no
#%end

'''Output'''

#%option G_OPT_R_OUTPUT
#% key: potential
#% key_desc: name
#% label: Output map of ecreation potential
#% description: Recreation potential map classified in 3 categories
#% required: no
#% guisection: Output
#%end

#%option G_OPT_R_OUTPUT
#% key: opportunity
#% key_desc: name
#% label: Output intermediate map of recreation opportunity
#% description: Intermediate step in deriving the 'spectrum' map, classified in 3 categories
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
#%  requires: landcover, spectrum
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
#% label: Output map unmet demand distribution
#% description: Unmet demand distribution output map: population density per Local Administrative Unit and areas of high recreational value
#% required : no
#% guisection: Output
#%end

#%rules
#%  requires_all: demand, population, base
#%  requires: demand, infrastructure, anthropic, roads
#%end

#%option G_OPT_R_OUTPUT
#% key: mobility
#% type: string
#% key_desc: name
#% label: Output map of mobility
#% description: Mobility output map: population (per Local Administrative Unit) near areas of high recreational value
#% required : no
#% guisection: Output
#%end

#%rules
#%  requires_all: mobility, population, base
#%  requires: mobility, infrastructure, anthropic, roads
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

#%rules
#%  requires: opportunity, spectrum, demand, mobility, supply
#%  required: potential, spectrum, demand, mobility, supply
#%end

#%rules
#%  requires_all: supply, population
#%  requires: supply, base, base_vector, aggregation
#%  requires: supply, landcover, landuse
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

import os, sys, subprocess
import datetime, time

'''Fake a file-like object from an in-script hardcoded string?'''
# import StringIO
# from cStringIO import StringIO

import atexit
import grass.script as grass
from grass.exceptions import CalledModuleError
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import raster as r

if "GISBASE" not in os.environ:
    g.message(_("You must be in GRASS GIS to run this program."))
    sys.exit(1)

# from scoring_schemes import corine

# globals

global grass_render_directory, grass_render_file
grass_render_directory = "/geo/grassdb/render"
# grass_render_file = grass_render_directory + 'grass_render_file.png'  # REMOVEME

global equation, citation, spacy_plus
citation_recreation_potential='Zulian (2014)'
spacy_plus = ' + '
equation = "{result} = {expression}"  # basic equation for mapcalc

global THRESHHOLD_ZERO, THRESHHOLD_0001, THRESHHOLD_0003
THRESHHOLD_ZERO = 0
THRESHHOLD_0001 = 0.0001
THRESHHOLD_0003 = 0.0003

global COMMA, EUCLIDEAN, NEIGHBORHOOD_SIZE, NEIGHBORHOOD_METHOD
COMMA='comma'
EUCLIDEAN='euclidean'
# units='k'
NEIGHBORHOOD_SIZE = 11  # this and below, required for neighborhood_function
NEIGHBORHOOD_METHOD = 'mode'

water_proximity_constant=1
water_proximity_kappa=30
water_proximity_alpha=0.008
water_proximity_score=1
bathing_water_proximity_constant=1
bathing_water_proximity_kappa=5
bathing_water_proximity_alpha=0.1101

SUITABILITY_SCORES='''1:1:0:0
2:2:0.1:0.1
3:9:0:0
10:10:1:1
11:11:0.1:0.1
12:13:0.3:0.3
14:14:0.4:0.4
15:17:0.5:0.5
18:18:0.6:0.6
19:20:0.3:0.3
21:22:0.6:0.6
23:23:1:1
24:24:0.8:0.8
25:25:1:1
26:29:0.8:0.8
30:30:1:1
31:31:0.8:0.8
32:32:0.7:0.7
33:33:0:0
34:34:0.8:0.8
35:35:1:1
36:36:0.8:0.8
37:37:1:1
38:38:0.8:0.8
39:39:1:1
40:42:1:1
43:43:0.8:0.8
44:44:1:1
45:45:0.3:0.3'''

URBAN_ATLAS_CATEGORIES = '''11100
11200
12100
12200
12300
12400
13100
13200
13300
14100
14200
21100
21200
21300
22100
22200
22300
23100
24100
24200
24300
24400
31100
31200
31300
32100
32200
32300
32400
33100
33200
33300
33400
33500
41100
41200
42100
42200
42300
'''

URBAN_ATLAS_TO_MAES_NOMENCLATURE='''
11100 = 1 Urban
11210 = 1 Urban
11220 = 1 Urban
11230 = 1 Urban
11240 = 1 Urban
11300 = 1 Urban
12100 = 1 Urban
12210 = 1 Urban
12220 = 1 Urban
12230 = 1 Urban
12300 = 1 Urban
12400 = 1 Urban
13100 = 1 Urban
13300 = 1 Urban
13400 = 1 Urban
14100 = 1 Urban
14200 = 1 Urban
21000 = 2 Cropland
22000 = 2 Cropland
23000 = 2 Cropland
25400 = 2 Cropland
31000 = 3 Woodland and forest
32000 = 3 Woodland and forest
33000 = 3 Woodland and forest
40000 = 4 Grassland
50000 = 5 Heathland and shrub
'''

recreation_potential_categories = '''0.0:0.2:1
0.2:0.4:2
0.4:*:3'''
#anthropic_distance_categories=
#'0:500:1,500.000001:1000:2,1000.000001:5000:3,5000.000001:10000:4,10000.00001:*:5'
recreation_opportunity_categories=recreation_potential_categories

#
## FIXME -- No hardcodings please.
#

POTENTIAL_CATEGORY_LABELS = '''1:Near
2:Midrange
3:Far
'''

OPPORTUNITY_CATEGORY_LABELS = POTENTIAL_CATEGORY_LABELS

SPECTRUM_CATEGORY_LABELS = '''1:Low provision (far)
2:Low provision (midrange)
3:Low provision (near)
4:Moderate provision (far)
5:Moderate provision (midrange)
6:Moderate provision (near)
7:High provision (far)
8:High provision (midrange)
9:High provision (near)
'''

SPECTRUM_DISTANCE_CATEGORY_LABELS = '''1:0 to 1 km
2:1 to 2 km
3:2 to 3 km
4:3 to 4 km
5:>4 km
'''

#
## FIXME -- No hardcodings please.
#

HIGHEST_RECREATION_CATEGORY = 9

SCORE_COLORS = """ # http://colorbrewer2.org/?type=diverging&scheme=RdYlGn&n=11
0.0% 165:0:38
10.0% 215:48:39
20.0% 244:109:67
30.0% 253:174:97
40.0% 254:224:139
50.0% 255:255:191
60.0% 217:239:139
70.0% 166:217:106
80.0% 102:189:99
90.0% 26:152:80
100.0% 0:104:55"""

POTENTIAL_COLORS = """ # Cubehelix color table generated using:
#   r.colors.cubehelix -dn ncolors=3 map=recreation_potential nrotations=0.33 gamma=1.5 hue=0.9 dark=0.3 output=recreation_potential.colors
0.000% 55:29:66
33.333% 55:29:66
33.333% 157:85:132
66.667% 157:85:132
66.667% 235:184:193
100.000% 235:184:193"""

OPPORTUNITY_COLORS = """# Cubehelix color table generated using:
#   r.colors.cubehelix -dn ncolors=3 map=recreation_potential nrotations=0.33 gamma=1.5 hue=0.9 dark=0.3 output=recreation_potential.colors
0.000% 55:29:66
33.333% 55:29:66
33.333% 157:85:132
66.667% 157:85:132
66.667% 235:184:193
100.000% 235:184:193"""

SPECTRUM_COLORS = """# Cubehelix color table generated using:
#   r.colors.cubehelix -dn ncolors=9 map=recreation_spectrum nrotations=0.33 gamma=1.5 hue=0.9 dark=0.3 output=recreation_spectrum.colors
0.000% 55:29:66
11.111% 55:29:66
11.111% 79:40:85
22.222% 79:40:85
22.222% 104:52:102
33.333% 104:52:102
33.333% 131:67:118
44.444% 131:67:118
44.444% 157:85:132
55.556% 157:85:132
55.556% 180:104:145
66.667% 180:104:145
66.667% 202:128:159
77.778% 202:128:159
77.778% 221:156:175
88.889% 221:156:175
88.889% 235:184:193
100.000% 235:184:193"""

MOBILITY_CONSTANT = 1
MOBILITY_COEFFICIENTS = { 0 : (0.02350, 0.00102),
                          1 : (0.02651, 0.00109),
                          2 : (0.05120, 0.00098),
                          3 : (0.10700, 0.00067),
                          4 : (0.06930, 0.00057)}
MOBILITY_SCORE = 52
MOBILITY_COLORS = 'wave'
LANDCOVER_FRACTIONS_COLOR='wave'

METHODS='sum'

# helper functions

def run(cmd, **kwargs):
    """Pass required arguments to grass commands (?)"""
    grass.run_command(cmd, quiet=True, **kwargs)

def tmp_map_name(**kwargs):
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
    temporary_filename = "tmp." + grass.basename(temporary_absolute_filename)  # use its basename
    if 'name' in kwargs:
        name = kwargs.get('name')
        temporary_filename = temporary_filename + '.' + str(name)
    return temporary_filename

def string_to_file(string, **kwargs):
    """
    """
    string = string.split(',')
    string = '\n'.join(string)
    # string = string.splitlines()

    msg = "String split in lines: {s}".format(s=string)
    grass.debug(_(msg))

    if 'name' in kwargs:
        name = kwargs.get('name')
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
        print "IOError :", error
        return

    finally:
        ascii_file.close()
        return filename  # how would that work with a file-like object?
        # Will be removed right after `.close()` -- How to possibly re-use it
            # outside the function?
        # Wrap complete main() in a `try` statement?

def cleanup():
    """Clean up temporary maps"""
    g.message("Removing temporary intermediate maps")
    g.remove(flags='f', type="raster", 
            pattern='tmp.{pid}*'.format(pid=os.getpid()),
            quiet=True)

    if remove_at_exit:
        g.remove(flags='f', type='raster', name=','.join(remove_at_exit),
                quiet=True)

    if grass.find_file(name='MASK', element='cell')['file']:
        r.mask(flags='r', verbose=True)

def draw_map(mapname, **kwargs):
    """
    Set the GRASS_RENDER_FILE and draw the requested raster map using
    Terminology's `tycat` utility.

    Parameters
    ----------
    mapname:
        Name of input raster map to draw on terminology

    width:
        Optional parameter to set the width

    height:
        Optional parameter to set the height

    Returns
    -------
    This function does not return any object

    Examples
    --------
    ..
    draw_map(raster_map_name)
    draw_map(raster_map_name, width='50', height='50')
    ..
    """
    if flags['d']:

        # Local globals
        width = 30
        height = 30

        # grass.message(_("Map name: {m}".format(m=mapname)))
        # Do not draw maps that are all 0
        minimum = grass.raster_info(mapname)['min']
        grass.debug(_("Minimum: {m}".format(m=minimum)))
        # grass.message(_("Minimum: {m}".format(m=minimum)))
        maximum = grass.raster_info(mapname)['max']
        grass.debug(_("Maximum: {m}".format(m=maximum)))
        # grass.message(_("Maximum: {m}".format(m=maximum)))

        if minimum == None and maximum == None:
            msg = "All cells in map '{name}' are NULL. "
            msg += "If unexpected, please check for processing errors."
            msg = msg.format(name=mapname)
            grass.warning(_(msg))
            return

        if minimum == 0 and maximum == 0:
            msg = "Map '{name}' is all 0. Not drawing".format(name=mapname)
            grass.warning(_(msg))
            return

        render_file = "{directory}/{prefix}{name}{suffix}.{extension}"
        if 'prefix' in kwargs:
            prefix = kwargs.get('prefix') + '_'
        else:
            prefix = ''

        if 'suffix' in kwargs:
            suffix = '_' + kwargs.get('suffix')
        else:
            suffix = ''

        render_file = render_file.format(
                directory = grass_render_directory,
                prefix=prefix,
                name = mapname,
                suffix=suffix,
                extension = 'png')

        os.putenv("GRASS_RENDER_FILE", render_file)

        run("d.erase", bgcolor='black', flags='f')
        run("d.rast", map=mapname)
        # run("d.rast.leg", map=mapname)

        if 'width' in kwargs and 'height' in kwargs:
            width = kwargs.get('width')
            height = kwargs.get('height')

        grass.message(_(" >>> Map file: {f}".format(f=render_file)))
        command = "tycat -g {w}x{h} {filename}"
        command = command.format(filename=render_file, w=width, h=height)
        subprocess.Popen(command.split())

def save_map(mapname):
    """Helper function to save some in-between maps, assisting in debugging

    Parameters
    ----------
    mapname :
        ...

    Returns
    -------
    newname :
        New name for the input raster map

    Examples
    --------
    """
    # run('r.info', map=mapname, flags='r')
    # run('g.copy', raster=(mapname, 'DebuggingMap'))

    #
    # Needs re-design!
    #

    newname = mapname
    if save_temporary_maps:
        newname = 'output_' + mapname
        run('g.rename', raster=(mapname, newname))
    return newname

def append_map_to_component(raster, component_name, component_list):
    """Appends raster map to given list of components

    Parameters
    ----------
    raster :
        Input raster map name

    component_name :
        Name of the component to add the raster map to

    component_list :
        List of raster maps to add the input 'raster' map

    Returns
    -------

    Examples
    --------
    ...
    """
    component_list.append(raster)
    msg = "Map {name} included in the '{component}' component"
    msg = msg.format(name=raster, component=component_name)
    grass.verbose(_(msg))

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
    univariate = grass.parse_command('r.univar', flags='g', map=raster)
    if info:
        minimum = univariate['min']
        mean = univariate['mean']
        maximum = univariate['max']
        variance = univariate['variance']
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
    grass.warning(_(msg))
    # Is this right?
    # ------------------------------------------

    r.recode(input=raster,
            rules=rules,
            output=output)

    r.colors(map=output,
            rules='-',
            stdin=SCORE_COLORS,
            quiet=True)

    # if save_temporary_maps:
    #     tmp_output = save_map(output)

    grass.verbose(_("Scored map {name}:".format(name=raster)))
    draw_map(output)

def float_to_integer(double):
    """Converts an FCELL or DCELL raster map into a CELL raster map

    Parameters
    ----------
    double:
            An 'FCELL' or 'DCELL' type raste map

    Returns
    -------
    This function does not return any value

    Examples
    --------
    ..
    """
    expression = 'int({double})'
    expression = expression.format(double=double)
    equation=equation.format(result=double, expression=expression)
    r.mapcalc(equation)

def get_coefficients(coefficients_string):
    """Returns coefficients from an input coefficients_string

    Parameters
    ----------
    coefficients_string:
        One string which lists a metric and coefficients separated by comma
        without spaces

    Returns
    -------
    metric:
        Metric to use an input option to the `r.grow.distance` module

    constant:
        A constant value for the 'attractiveness' function

    kappa:
        A Kappa coefficients for the 'attractiveness' function

    alpha:
        An alpha coefficient for the 'attractiveness' function

    score
        A score value to multiply by the generic 'attractiveness' function

    Examples
    --------
    ...
    """
    coefficients = coefficients_string.split(',')
    msg = "Distance function coefficients: "
    metric = coefficients[0]
    msg += "Metric='{metric}', ".format(metric=metric)
    constant = coefficients[1]
    msg += "Constant='{constant}', ".format(constant=constant)
    kappa = coefficients[2]
    msg += "Kappa='{Kappa}', ".format(Kappa=kappa)
    alpha = coefficients[3]
    msg += "Alpha='{alpha}', ".format(alpha=alpha)
    try:
        if coefficients[4]:
            score = coefficients[4]
            msg += "Score='{score}'".format(score=score)
            grass.verbose(_(msg))
            return metric, constant, kappa, alpha, score
    except IndexError:
        grass.verbose(_("Score not provided"))

    grass.verbose(_(msg))
    return metric, constant, kappa, alpha

def compute_attractiveness(raster, metric, constant, kappa, alpha, **kwargs):
    """
    Compute a raster map whose values follow an (euclidean) distance function
    ( {constant} + {kappa} ) / ( {kappa} + exp({alpha} * {distance}) ), where:

    Source: http://publications.jrc.ec.europa.eu/repository/bitstream/JRC87585/lb-na-26474-en-n.pd

    Parameters
    ----------
    constant : 1

    kappa :
        Another constant named K

    alpha :

    distance :
        A distance map based on the input raster.

    score :

    kwargs : output_name, optional
        Optional keyword arguments, such as output name for the computed
        proximity_name.

    Returns
    -------
    tmp_output :
        A temporary proximity to features raster map.

    Examples
    --------
    ...

    """
    draw_map(raster)

    distance_terms = [str(raster),
                      str(metric),
                      'distance',
                      str(constant),
                      str(kappa),
                      str(alpha)]

    if 'score' in kwargs:
        score = kwargs.get('score')
        grass.debug(_("Score for attractiveness equation: {s}".format(s=score)))
        distance_terms += str(score)

    # tmp_distance = tmp_map_name('_'.join(distance_terms))
    tmp_distance = tmp_map_name(name='_'.join([raster, metric]))
    r.grow_distance(input=raster,
            distance=tmp_distance,
            metric=metric,
            quiet=True,
            overwrite=True)

    if 'mask' in kwargs:
        mask = kwargs.get('mask')
        # global mask
        msg = "Masking NULL cells based on '{mask}'".format(mask=mask)
        grass.verbose(_(msg))
        r.mask(raster=mask, flags='i', overwrite=True, quiet=True)
        # draw_map(mask)

    draw_map(tmp_distance)

    numerator = "{constant} + {kappa}"
    numerator = numerator.format(constant = constant, kappa = kappa)

    denominator = "{kappa} + exp({alpha} * {distance})"
    denominator = denominator.format(kappa = kappa,
                                     alpha = alpha,
                                     distance = tmp_distance)

    distance_function = " ( {numerator} / {denominator} )"
    distance_function = distance_function.format(
            numerator = numerator,
            denominator = denominator)

    if 'score' in kwargs:
        score = kwargs.get('score')
        distance_function += " * {score}"  # need for float()?
        distance_function = distance_function.format(score = score)

    # temporary maps will be removed
    if 'output_name' in kwargs:
        tmp_distance_map = tmp_map_name(name=kwargs.get('output_name'))
    else:
        basename = '_'.join([raster, 'attractiveness'])
        tmp_distance_map = tmp_map_name(name=basename)

    distance_function = equation.format(result=tmp_distance_map,
            expression=distance_function)

    msg = "Distance function: {f}".format(f=distance_function)
    grass.verbose(_(msg))
    del(msg)

    grass.mapcalc(distance_function, overwrite=True)

    r.null(map=tmp_distance_map, null=0)  # Set NULLs to 0

    compress_status = grass.read_command('r.compress', flags='g', map=tmp_distance_map)
    grass.verbose(_("Compress status: {s}".format(s=compress_status)))

    del(numerator)
    del(denominator)
    del(distance_function)

    tmp_output = save_map(tmp_distance_map)
    draw_map(tmp_distance_map)
    return tmp_distance_map

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

    neighborhood_output = distance_map + '_' + method
    msg = "Neighborhood operator '{method}' and size '{size}' for input map '{name}'"
    msg = msg.format(method=method, size=size, name=neighborhood_output)
    grass.verbose(_(msg))

    r.neighbors(input=raster,
            output=neighborhood_output,
            method=method,
            size=size,
            overwrite=True)

    # ---------------------------------------------------------------
    msg = "In neighborhood_function(), output of r.neighbors: {name}"
    msg = msg.format(name=neighborhood_output)
    grass.debug(_(neighborhood_output))
    # ---------------------------------------------------------------

    scoring_function = "{neighborhood} * {distance}"
    scoring_function = scoring_function.format(
            neighborhood=neighborhood_output,
            distance=distance_map)

    # ---------------------------------------------------------------
    msg = "Scoring function: {f}".format(f=scoring_function)
    grass.debug(_(msg))
    # ---------------------------------------------------------------

    filtered_output = distance_map
    filtered_output += '_' + method + '_' + str(size)

    # ---------------------------------------------------------------
    msg = "Filtered output: {o}".format(o=filtered_output)
    grass.debug(_(msg))
    # ---------------------------------------------------------------

    neighborhood_function = equation.format(result=filtered_output,
            expression=scoring_function)
    # ---------------------------------------------------------------
    grass.verbose(_("Expression: {e}".format(e=neighborhood_function)))
    # ---------------------------------------------------------------
    grass.mapcalc(neighborhood_function, overwrite=True)

    draw_map(filtered_output)

    # tmp_distance_map = filtered_output

    # r.compress(distance_map, flags='g')

    del(method)
    del(size)
    del(neighborhood_output)
    del(scoring_function)
    # del(filtered_output)

    return filtered_output

def zerofy_small_values(raster, threshhold, output_name):
    """
    Set the input raster map cell values to 0 if they are smaller than the
    given threshhold

    Parameters
    ----------
    raster :
        Name of input raster map

    threshhold :
        Reference for which to flatten smaller raster pixel values to zero

    output_name :
        Name of output raster map

    Returns
    -------
        Does not return any value

    Examples
    --------
    ...
    """
    rounding='if({raster} < {threshhold}, 0, {raster})'
    rounding = rounding.format(raster=raster, threshhold=threshhold)
    rounding_equation = equation.format(result=output_name, expression=rounding)
    grass.mapcalc(rounding_equation, overwrite=True)

def normalize_map (raster, output_name):
    """
    Normalize all raster map cells by subtracting the raster map's minimum and
    dividing by the range.

    Parameters
    ----------
    raster :
        Name of input raster map

    output_name :
        Name of output raster map

    Returns
    -------

    Examples
    --------
    ...
    """

    # grass.debug(_("Input to normalize: {name}".format(name=raster)))
    # grass.debug(_("Ouput: {name}".format(name=output_name)))

    finding = grass.find_file(name=raster, element='cell')

    if not finding['file']:
        grass.fatal("Raster map {name} not found".format(name=raster))
    # else:
    #     grass.debug("Raster map {name} found".format(name=raster))

    # univar_string = grass.read_command('r.univar', flags='g', map=raster)
    # univar_string = univar_string.replace('\n', '| ').replace('\r', '| ')
    # msg = "Univariate statistics: {us}".format(us=univar_string)

    minimum = grass.raster_info(raster)['min']
    grass.debug(_("Minimum: {m}".format(m=minimum)))

    maximum = grass.raster_info(raster)['max']
    grass.debug(_("Maximum: {m}".format(m=maximum)))

    # if minimum is None or maximum is None:
    #     msg = "Minimum and maximum values of the <{raster}> map are 'None'. "
    #     msg += "The {raster} map may be empty "
    #     msg += "OR the MASK opacifies all non-NULL cells."
    #     grass.fatal(_(msg.format(raster=raster)))

    normalisation = 'float(({raster} - {minimum}) / ({maximum} - {minimum}))'
    normalisation = normalisation.format(raster=raster, minimum=minimum,
            maximum=maximum)

    # Maybe this can go in the parent function? The 'raster' names are too
    # long!
    if info:
        msg = "Normalization expression: "
        msg += normalisation
        grass.verbose(_(msg))
    #

    normalisation_equation = equation.format(result=output_name,
        expression=normalisation)
    grass.mapcalc(normalisation_equation, overwrite=True)

    draw_map(output_name)
    get_univariate_statistics(output_name)

    del(minimum)
    del(maximum)
    del(normalisation)
    del(normalisation_equation)

def zerofy_and_normalise_component(components, threshhold, output_name):
    """
    Sums up all maps listed in the given "components" object and derives a
    normalised output.

    To Do:

    * Improve `threshold` handling. What if threshholding is not desired? How
    to skip performing it?

    Parameters
    ----------
    components :
        Input list of raster maps (components)

    threshhold :
        Reference value for which to flatten all smaller raster pixel values to
        zero

    output_name :
        Name of output raster map

    Returns
    -------
    ...

    Examples
    --------
    ...
    """
    msg = "Normalising sum of: "
    msg += ','.join(components)
    grass.debug(_(msg))
    grass.verbose(_(msg))

    if len(components) > 1:

        # prepare string for mapcalc expression
        components = [ name.split('@')[0] for name in components ]
        components_string = spacy_plus.join(components).replace(' ', '').replace('+', '_')

        # temporary map names
        tmp_intermediate = tmp_map_name(name=components_string)
        tmp_output = tmp_map_name(name=components_string)

        # build mapcalc expression
        component_expression = spacy_plus.join(components)
        component_equation = equation.format(result=tmp_intermediate, expression=component_expression)

        grass.mapcalc(component_equation, overwrite=True)

        del(components_string)
        del(component_expression)
        del(component_equation)

    elif len(components) == 1:
        # temporary map names, if components contains one element
        tmp_intermediate = components[0]
        tmp_output = tmp_map_name(name=tmp_intermediate)

    if threshhold > THRESHHOLD_ZERO:
        msg = "Setting values < {threshhold} in '{raster}' to zero"
        grass.verbose(msg.format(threshhold=threshhold, raster=tmp_intermediate))
        zerofy_small_values(tmp_intermediate, threshhold, tmp_output)

    else:
        tmp_output = tmp_intermediate

    # grass.verbose(_("Temporary map name: {name}".format(name=tmp_output)))
    grass.debug(_("Output map name: {name}".format(name=output_name)))
    # r.info(map=tmp_output, flags='gre')
    
    ### FIXME

    normalize_map(tmp_output, output_name)

    ### FIXME

    del(tmp_intermediate)
    del(tmp_output)
    del(output_name)

def classify_recreation_component(component, rules, output_name):
    """
    Recode an input recreation component based on given rules

    To Do:

    - Potentially, test range of input recreation component, i.e. ranging in
      [0,1]

    Parameters
    ----------
    component :
        Name of input raster map

    rules :
        Rules for r.recode

    output_name :
        Name for output raster map

    Returns
    -------
        Does not return any value

    Examples
    --------
    ...

    """
    r.recode(input=component,
            rules='-',
            stdin=rules,
            output=output_name)
    draw_map(output_name)

def compute_anthropic_proximity(raster, distance_categories, **kwargs):
    """
    Compute proximity to anthropic surfaces

    1. Distance to features
    2. Classify distances

    Parameters
    ----------
    raster :
        Name of input raster map

    distance_categories :
        Category rules to recode the input distance map

    kwargs :
        Optional arguments: output_file

    Returns
    -------
    tmp_output :
        Name of the temporary output map for internal, in-script, re-use

    Examples
    --------
    ...
    """
    anthropic_distances = tmp_map_name(name=raster)

    grass.run_command("r.grow.distance",
            input = raster,
            distance = anthropic_distances,
            metric = EUCLIDEAN,
            quiet = True,
            overwrite = True)

    if 'output_name' in kwargs:
        tmp_output = tmp_map_name(name=kwargs.get('output_name'))  # temporary maps will be removed
        grass.debug(_("Pre-defined output map name {name}".format(name=tmp_output)))

    else:
        tmp_output = tmp_map_name(name='anthropic_proximity')
        grass.debug(_("Hardcoded temporary map name {name}".format(name=tmp_output)))

    msg = "Computing proximity to '{mapname}'"
    msg = msg.format(mapname=raster)
    grass.verbose(_(msg))
    grass.run_command("r.recode",
            input = anthropic_distances,
            output = tmp_output,
            rules = distance_categories,
            overwrite = True)

    output = grass.find_file(name=tmp_output, element='cell')
    if not output['file']:
        grass.fatal("Proximity map {name} not created!".format(name=raster))
#     else:
#         grass.message(_("Output map {name}:".format(name=tmp_output)))

    draw_map(tmp_output)

    return tmp_output

def anthropic_accessibility_expression(anthropic_proximity, roads_proximity):
    """
    Build an r.mapcalc compatible expression to compute accessibility to
    anthropic surfaces based on the following accessibility classification
    rules for anthropic surfaces:

    |-------------------+-------+------------+-------------+--------------+---------|
    | Anthropic / Roads | < 500 | 500 - 1000 | 1000 - 5000 | 5000 - 10000 | > 10000 |
    |-------------------+-------+------------+-------------+--------------+---------|
    | < 500             | 1     | 1          | 2           | 3            | 4       |
    |-------------------+-------+------------+-------------+--------------+---------|
    | 500 - 1000        | 1     | 1          | 2           | 3            | 4       |
    |-------------------+-------+------------+-------------+--------------+---------|
    | 1000 - 5000       | 2     | 2          | 2           | 4            | 5       |
    |-------------------+-------+------------+-------------+--------------+---------|
    | 5000 - 10000      | 3     | 3          | 4           | 5            | 5       |
    |-------------------+-------+------------+-------------+--------------+---------|
    | > 10000           | 3     | 4          | 4           | 5            | 5       |
    |-------------------+-------+------------+-------------+--------------+---------|


    Parameters
    ----------
    anthropic :
        Proximity to anthropic surfaces

    roads :
        Proximity to roads

    Returns
    -------
    expression
        Valid r.mapcalc expression


    Examples
    --------
    ...
    """
    expression = ('if( {anthropic} <= 2 && {roads} <= 2, 1,'
            ' \ \n if( {anthropic} == 1 && {roads} == 3, 2,'
            ' \ \n if( {anthropic} == 2 && {roads} == 3, 2,'
            ' \ \n if( {anthropic} == 3 && {roads} <= 3, 2,'
            ' \ \n if( {anthropic} <= 2 && {roads} == 4, 3,'
            ' \ \n if( {anthropic} == 4 && {roads} == 2, 3,'
            ' \ \n if( {anthropic} >= 4 && {roads} == 1, 3,'
            ' \ \n if( {anthropic} <= 2 && {roads} == 5, 4,'
            ' \ \n if( {anthropic} == 3 && {roads} == 4, 4,'
            ' \ \n if( {anthropic} >= 4 && {roads} == 3, 4,'
            ' \ \n if( {anthropic} == 5 && {roads} == 2, 4,'
            ' \ \n if( {anthropic} >= 3 && {roads} == 5, 5,'
            ' \ \n if( {anthropic} >= 4 && {roads} == 4, 5)))))))))))))')

    expression = expression.format(anthropic=anthropic_proximity,
            roads=roads_proximity)
    return expression


def compute_anthropic_accessibility(anthropic_proximity, roads_proximity, **kwargs):
    """Compute anthropic proximity

    Parameters
    ----------
    anthropic_proximity :
        Anthropic surfaces...

    roads_proximity :
        Road infrastructure

    kwargs :
        Optional input parameters

    Returns
    -------
    output :
        ...

    Examples
    --------
    ...
    """
    anthropic = grass.find_file(name=anthropic_proximity, element='cell')
    if not anthropic['file']:
        grass.fatal("Raster map {name} not found".format(name=anthropic_proximity))

    roads = grass.find_file(name=roads_proximity, element='cell')
    if not roads['file']:
        grass.fatal("Raster map {name} not found".format(name=roads_proximity))

    accessibility_expression = anthropic_accessibility_expression(anthropic_proximity, roads_proximity)
    if 'output_name' in kwargs:
        tmp_output = tmp_map_name(name=kwargs.get('output_name'))  # temporary maps will be removed
    else:
        basename = 'anthropic_accessibility'
        tmp_output = tmp_map_name(name=basename)

    accessibility_equation = equation.format(result=tmp_output,
            expression=accessibility_expression)

    if info:
        msg = "Equation for proximity to anthropic areas: \n"
        msg += accessibility_equation
        grass.debug(msg)
        del(msg)

    grass.verbose(_("Computing accessibility to anthropic surfaces"))
    grass.mapcalc(accessibility_equation, overwrite=True)

    del(accessibility_expression)
    del(accessibility_equation)

    draw_map(tmp_output)
    output = save_map(tmp_output)

    return output

def recreation_spectrum_expression(potential, opportunity):
    """
    Build and return a valid mapcalc expression for deriving
    the Recreation Opportunity Spectrum

    |-------------------------+------+----------+-----|
    | Potential / Opportunity | Near | Midrange | Far |
    |-------------------------+------+----------+-----|
    | Near                    | 1    | 2        | 3   |
    |-------------------------+------+----------+-----|
    | Midrange                | 4    | 5        | 6   |
    |-------------------------+------+----------+-----|
    | Far                     | 7    | 8        | 9   |
    |-------------------------+------+----------+-----|

    Questions:

    - Why not use `r.cross`?
    - Use DUMMY strings for potential and opportunity raster map names?

    Parameters
    ----------
    potential :
        Map depicting potential for recreation

    opportunity :
        Map depicting opportunity for recreation

    Returns
    -------
    expression :
        A valid r.mapcalc expression

    Examples
    --------
    ...
    """
    expression = ('if( {potential} == 1 && {opportunity} == 1, 1,'
            ' \ \n if( {potential} == 1 && {opportunity} == 2, 2,'
            ' \ \n if( {potential} == 1 && {opportunity} == 3, 3,'
            ' \ \n if( {potential} == 2 && {opportunity} == 1, 4,'
            ' \ \n if( {potential} == 2 && {opportunity} == 2, 5,'
            ' \ \n if( {potential} == 2 && {opportunity} == 3, 6,'
            ' \ \n if( {potential} == 3 && {opportunity} == 1, 7,'
            ' \ \n if( {potential} == 3 && {opportunity} == 2, 8,'
            ' \ \n if( {potential} == 3 && {opportunity} == 3, 9)))))))))')

    expression = expression.format(potential=potential,
            opportunity=opportunity)

    msg = "Recreation Spectrum expression: \n"
    msg += expression
    grass.debug(msg)
    del(msg)

    return expression

def compute_recreation_spectrum(potential, opportunity, spectrum):
    """
    Computes spectrum for recreation based on maps of potential and opportunity
    for recreation

    Parameters
    ----------
    potential :
        Name for input potential for recreation map

    opportunity :
        Name for input opportunity for recreation map

    Returns
    -------
    spectrum :
        Name for output spectrum of recreation map

    Examples
    --------
    ...
    """
    spectrum_expression = recreation_spectrum_expression(potential,
            opportunity)

    spectrum_equation = equation.format(result=spectrum,
            expression=spectrum_expression)

    # if info:
    #     msg = "Recreation Spectrum equation: \n"
    #     msg += spectrum_equation
    #     g.message(msg)
    #     del(msg)

    grass.mapcalc(spectrum_equation, overwrite=True)

    draw_map(spectrum)

    del(spectrum_expression)
    del(spectrum_equation)
    return spectrum

def update_meta(raster, title):
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
    history = '\n' + citation_recreation_potential
    description_string = 'Recreation {raster} map'
    description = description_string.format(raster=raster)

    title = '{title}'.format(title=title)
    units = 'Meters'

    source1 = 'Source 1'
    source2 = 'Source 2'

    r.support(map=raster, title=title, description=description, units=units,
            source1=source1, source2=source2, history=history)

    if timestamp:
        r.timestamp(map=raster, date=timestamp)

    del(history)
    del(description)
    del(title)
    del(units)
    del(source1)
    del(source2)

def build_mobility_function(constant, kappa, alpha, population, **kwargs):
    """
    Formula: if(L10<>0,(1+$D$3)/($D$3+exp(-$E$3*L10))*52,0)
    Source: Excel file provided by members of the MAES Team, Land Resources, D3

    -------------------------------------
    if L<>0; then
      # (1 + D) / (D + exp(-E * L)) * 52)

      # D: Kappa
      # E: Alpha
      # L: Population (in boundary, in distance buffer)
    -------------------------------------

    The basic function is identical to the one used in
    compute_attractiveness(), which is:

    ( {constant} + {kappa} ) / ( {kappa} + exp({alpha} * {distance}) )

    ToDo:
    -----
        Deduplication!  The same distance function is used elsewhere.

    Parameters
    ----------

    Returns
    -------

    Examples
    --------
    """

    # DUMMY_DISTANCE='DUMMY_DISTANCE'
    # basic formula:
        # ( {constant} + {kappa} ) / ( {kappa} + exp({alpha} * {population}) )

    numerator = "{constant} + {kappa}"
    numerator = numerator.format(constant = constant, kappa = kappa)

    denominator = "{kappa} + exp({alpha} * {population})"
    denominator = denominator.format(kappa = kappa,
                                     alpha = alpha,
                                     population = population)
                                     # distance to be formatter later

    function = " ( {numerator} / {denominator} )"
    function = function.format(
            numerator = numerator,
            denominator = denominator)
    grass.debug("Function without score: {f}".format(f=function))

    if 'score' in kwargs:
        score = kwargs.get('score')
        function += " * {score}"  # need for float()?
        function = function.format(score = score)
    grass.debug("Function after adding score: {f}".format(f=function))

    return function

def compute_mobility(distance_map, constant, coefficients, population, score):
    """
    Parameters
    ----------

    distance_map:
        Map of distance categories (aka 'buffer zones')

    constant:
        Constant for the mobility function

    coefficients:
        A dictionary with a set for coefficients for each distance category, as
        (the example) presented in the following table:

        |----------+---------+---------|
        | Distance | Kappa   | Alpha   |
        |----------+---------+---------|
        | 0 to 1   | 0.02350 | 0.00102 |
        |----------+---------+---------|
        | 1 to 2   | 0.02651 | 0.00109 |
        |----------+---------+---------|
        | 2 to 3   | 0.05120 | 0.00098 |
        |----------+---------+---------|
        | 3 to 4   | 0.10700 | 0.00067 |
        |----------+---------+---------|
        | >4       | 0.06930 | 0.00057 |
        |----------+---------+---------|

        Note, the last distance category is not considered in deriving the
        final "map of visits".

    population:
        A map with the distribution of the demand per distance category and
        predefined geometric boundaries (see `r.stats.zonal` deriving the
        'demand' map ).

    score:
        A score value for the mobility function

    Returns
    -------

    mobility_expression:
        A valid mapcalc expression to compute the mobility based on the
        predefined function `build_mobility_function`.

    Examples
    --------
    ...
    """
    expressions={}  # create a dictionary of expressions
    for distance, parameters in coefficients.items():

        kappa, alpha = parameters
        expressions['{distance}'.format(distance=distance)]=build_mobility_function(
                constant=constant,
                kappa=kappa,
                alpha=alpha,
                population=population,
                score=score)

        grass.debug(_("For distance {d}:".format(d=distance)))
        grass.debug(_(expressions['{distance}'.format(distance=distance)]))

    msg = "Expressions per distance category: {e}".format(e=expressions)
    grass.debug(_(msg))

    # build expressions -- explicit: use the'score' kwarg!

                  # ------------------------------------
                  # Distance category 4 not used!
                  # ' \ \n mobility_4 = {expression_4},'
                  # ' \ \n distance_4 = {distance} == 4,'
                  # ' \ \n if( distance_4, mobility_4,'
                  # ------------------------------------

    expression = ('eval( mobility_0 = {expression_0},'
                  ' \ \n mobility_1 = {expression_1},'
                  ' \ \n mobility_2 = {expression_2},'
                  ' \ \n mobility_3 = {expression_3},'
                  ' \ \n distance_0 = {distance} == 0,'
                  ' \ \n distance_1 = {distance} == 1,'
                  ' \ \n distance_2 = {distance} == 2,'
                  ' \ \n distance_3 = {distance} == 3,'
                  ' \ \n if( distance_0, mobility_0,'
                  ' \ \n if( distance_1, mobility_1,'
                  ' \ \n if( distance_2, mobility_2,'
                  ' \ \n if( distance_3, mobility_3,'
                  ' \ \n null() )))))')
    grass.debug(_("Mapcalc expression: {e}".format(e=expression)))

    # replace keywords appropriately
    mobility_expression = expression.format(
        expression_0 = expressions['0'],
        expression_1 = expressions['1'],
        expression_2 = expressions['2'],
        expression_3 = expressions['3'],
        expression_4 = expressions['4'],
        distance = distance_map)

    msg = "Big expression (after formatting): {e}".format(e=expression)
    grass.debug(_(msg))

    return mobility_expression

def compute_unmet_demand(distance_map, constant, coefficients, population, score):
    """
    Parameters
    ----------

    distance_map:
        Map of distance categories (aka 'buffer zones')

    constant:
        Constant for the mobility function

    coefficients:
        A tuple with coefficients for the last distance category, as
        (the example) presented in the following table:

        |----------+---------+---------|
        | Distance | Kappa   | Alpha   |
        |----------+---------+---------|
        | >4       | 0.06930 | 0.00057 |
        |----------+---------+---------|

        Note, this is the "last" distance category--see also the
        compute_mobility() function.

    population:
        A map with the distribution of the demand per distance category and
        predefined geometric boundaries (see `r.stats.zonal` deriving the
        'unmet demand' map ).

    score:
        A score value for the mobility function

    Returns
    -------

    mobility_expression:
        A valid mapcalc expression to compute the mobility based on the
        predefined function `build_mobility_function`.

    Examples
    --------
    ...
    """
    distance = 4
    kappa, alpha = coefficients
    unmet_demand_expression = build_mobility_function(
            constant=constant,
            kappa=kappa,
            alpha=alpha,
            population=population,
            score=score)

    msg = "Expression for distance category '{d}': {e}".format(d=distance,
            e=unmet_demand_expression)
    grass.debug(_(msg))

    # build expressions -- explicit: use the 'score' kwarg!
    expression = ('eval( unmet_demand = {expression},'
                  ' \ \n distance = {distance} == 4,'
                  ' \ \n if( distance, unmet_demand,'
                  ' \ \n null() ))')
    grass.debug(_("Mapcalc expression: {e}".format(e=expression)))

    # replace keywords appropriately
    unmet_demand_expression = expression.format(
        expression = unmet_demand_expression,
        distance = distance_map)

    msg = "Big expression (after formatting): {e}".format(
            e=unmet_demand_expression)
    grass.debug(_(msg))

    return unmet_demand_expression

def update_vector(vector, raster, methods, column_prefix):
    """

    Parameters
    ----------
    vector:
        Vector map whose attribute table to update with results of the
        v.rast.stats call

    raster:
        Source raster map for statistics

    methods:
        Descriptive statistics for the `v.rast.stats` call

    column_prefix:
        Prefix for the names of the columns created by the `v.rast.stats` call

    Returns
    -------
        This helper function executes `v.rast.stats`. It does not return any
        value.

    Examples
    --------
    ..
    """
    run('v.rast.stats',
            map=vector,
            flags='c',
            raster=raster,
            method=methods,
            column_prefix=raster,
            overwrite=True)
    grass.verbose(_("Updating vector map '{v}'".format(v=vector)))

def compute_supply_table(base, landcover, reclassification_rules,
        reclassified_landcover, title, recreation_spectrum, highest_spectrum,
        mobility, **kwargs):
    """
    Parameters
    ----------

    base:
        Base map for final zonal statistics

    landcover:
        Land cover map to use as a base map for intermediate zonal statistics
        ? FIXME

    reclassification_rules:
        Reclassification rules for the input landcover map

    reclassified_landcover:
        Name for the reclassified land cover map

    title:
        Title for the reclassified land cover map

    recreation_spectrum:
        Map scoring access to and quality of recreation

    highest_spectrum:
        Expected is a map of areas with highest recreational value (9)

    ?:  Why is this needed for? An output for the final table? FIXME
        Land cover class percentages in ROS9 (this is: relative percentage)

    mobility:
        Map of visits, derived from the mobility function, depicting the
        number of people living inside zones 0, 1, 2, 3. Used as a cover map
        for zonal statistics.

    output:
        Supply table (distribution of flow for each land cover class)

    **kwargs:
        Optional keyword arguments, such as: 'prefix'

    Returns
    -------
    This function produces a map to base the production of a supply table in
    form of CSV. It does not return any value.

    """
    r.mask(raster=highest_spectrum,
            overwrite=True,
            quiet=True)
    grass.verbose(_("MASKing areas of high recreational value"))

    mobility_in_base = mobility + '_in_' + base
    r.stats_zonal(base=base,
            flags='r',
            cover=mobility,
            method='sum',
            output=mobility_in_base,
            overwrite=True,
            quiet=True)

    r.colors(map=mobility_in_base,
        color=MOBILITY_COLORS,
        quiet=True)
    draw_map(mobility_in_base)

    '''Save mobility map?'''

    # if mobility:

    #     g.rename(raster=(mobility_in_base,mobility))
    #     save_map(mobility)
    '''-----------------------------------------------------------------'''

    r.reclass(input=landcover,
            rules=reclassification_rules,
            output=reclassified_landcover,
            title=title,
            quiet=True)
    remove_at_exit.append(reclassified_landcover)

    draw_map(reclassified_landcover)

    # land class percentage per zone
    landcover_fragment_patches = []

    # Don't break if categories are labeled!
    categories = grass.read_command('r.category', map=base).split('\n')[:-1]
    for category in categories:

        category = category.split('\t')[0]
        grass.debug(_("Base map category: {c}".format(c=category)))

        masking = 'if( {base} == {category} && '
        masking += '{spectrum} == {highest_spectrum}, '
        masking += '{landcover}, null())'
        masking = masking.format(
                base=base,
                category=category,
                spectrum=recreation_spectrum,
                highest_spectrum=HIGHEST_RECREATION_CATEGORY,
                landcover=reclassified_landcover)

        base_mask = '{spectrum}_{base}_{category}'
        base_mask = base_mask.format(
                spectrum=highest_spectrum,
                base=base,
                category=category)
        remove_at_exit.append(base_mask)  # NOTE

        masking_equation = equation.format(result=base_mask,
                expression=masking)
        grass.mapcalc(masking_equation, overwrite=True)

        # set MASK to super-category
        grass.verbose(_("Setting map '{r}' as a MASK".format(r=base_mask)))
        draw_map(base_mask)
        r.mask(raster=base_mask, overwrite=True, quiet=True)

        if info:
            r.report(map=(base,reclassified_landcover),
                    flags='hn',
                    units=units,
                    quiet=True)

        # FIXME
        statistics_filename = 'statistics_' + base + '_' + category

        # add prefix to output filename
        if 'prefix' in kwargs:
            prefix = kwargs.get('prefix') + '_'
            statistics_filename = prefix + statistics_filename

        r.stats(input=(base,reclassified_landcover),
                output=statistics_filename,
                flags='ncapl',
                separator=COMMA,
                quiet=True)
        del(statistics_filename)
        # FIXME: deal with empty output files!

        # derive statistics map
        landcover_fragment = reclassified_landcover + '_' + base_mask
        remove_at_exit.append(landcover_fragment)  # NOTE

        # build expression
        expression_fragment = "{fragment} = {landcover}"
        expression_fragment = expression_fragment.format(
                fragment=landcover_fragment,
                landcover=reclassified_landcover)
        fragment_equation = equation.format(result=landcover_fragment,
                expression=expression_fragment)

        # compute
        r.mapcalc(fragment_equation, overwrite=True)
        draw_map(landcover_fragment)

        # assign categories
        r.category(map=landcover_fragment,
                raster=reclassified_landcover,
                quiet=True)

        r.mask(flags='r', quiet=True)

def main():
    """
    Main program
    """

    '''Flags and Options'''

    global info, save_temporary_maps
    landuse_extent = flags['e']
    save_temporary_maps = flags['s']
    info = flags['i']

    global timestamp
    timestamp = options['timestamp']

    global remove_at_exit, remove_normal_files_at_exit
    remove_at_exit = []
    remove_normal_files_at_exit = []

    global metric, units
    metric = options['metric']
    units = options['units']
    if len(units) > 1:
        units = units.split(',')

    '''names for input, output, output suffix, options'''

    global mask
    mask = options['mask']

    '''
    following some hard-coded names -- review and remove!
    '''

    land = options['land']
    land_component_map_name = tmp_map_name(name='land_component')

    water = options['water']
    water_component_map_name = tmp_map_name(name='water_component')

    natural = options['natural']
    natural_component_map_name = tmp_map_name(name='natural_component')

    urban = options['urban']
    urban_component_map='urban_component'

    infrastructure = options['infrastructure']
    infrastructure_component_map_name = tmp_map_name(name='infrastructure_component')

    recreation = options['recreation']
    recreation_component_map_name = tmp_map_name(name='recreation_component')

    '''Land components'''

    landuse = options['landuse']
    if landuse:
        # Check datatype: a land use map should be categorical, i.e. of type CELL
        landuse_datatype = grass.raster.raster_info(landuse)['datatype']
        if landuse_datatype != 'CELL':
            msg = ("The '{landuse}' input map "
                    "should be a categorical one "
                    "and of type 'CELL'. "
                    "Perhaps you meant to use the 'land' input option instead?")
            grass.fatal(_(msg.format(landuse=landuse)))

    suitability_map_name = tmp_map_name(name='suitability')
    suitability_scores = options['suitability_scores']

    if landuse and suitability_scores and ':' not in suitability_scores:
        msg = "Suitability scores from file: {scores}."
        msg = msg.format(scores = suitability_scores)
        grass.verbose(_(msg))

    if landuse and not suitability_scores:
        msg = "Using internal rules to score land use classes in '{map}'"
        msg = msg.format(map=landuse)
        grass.message(_(msg))

        suitability_scores = string_to_file(SUITABILITY_SCORES,
                name=suitability_map_name)
        remove_normal_files_at_exit.append(suitability_scores)

    if landuse and suitability_scores and ':' in suitability_scores:
        msg = "Using provided string of rules to score land use classes in {map}"
        msg = msg.format(map=landuse)
        grass.verbose(_(msg))
        suitability_scores = string_to_file(suitability_scores,
                name=suitability_map_name)
        remove_normal_files_at_exit.append(suitability_scores)


    # FIXME -----------------------------------------------------------------

    # Use one landcover input if supply is requested
    # Use one set of land cover reclassification rules

    landcover = options['landcover']

    if not landcover:
        landcover = landuse
        msg = "Land cover map 'landcover' not given. "
        msg += "Attempt to use the '{landuse}' map to derive areal statistics"
        msg = msg.format(landuse=landuse)
        grass.verbose(_(msg))

    else:
        landcover = options['landcover']

    maes_landcover = 'maes_land_classes'
    landcover_reclassification_rules = options['land_classes']

    # if 'land_classes' is a file
    if landcover and landcover_reclassification_rules and ':' not in landcover_reclassification_rules:
        msg = "Land cover reclassification rules from file: {rules}."
        msg = msg.format(rules = landcover_reclassification_rules)
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
                URBAN_ATLAS_TO_MAES_NOMENCLATURE,
                name=maes_landcover)
        remove_normal_files_at_exit.append(landcover_reclassification_rules)

        # if landcover is a "MAES" land cover, no need to reclassify!

    if landuse and landcover_reclassification_rules and ':' in landcover_reclassification_rules:
        msg = "Using provided string of rules to reclassify the '{map}' map"
        msg = msg.format(map=landcover)
        grass.verbose(_(msg))
        landcover_reclassification_rules =  string_to_file(
                landcover_reclassification_rules,
                name=maes_land_classes)
        remove_normal_files_at_exit.append(landcover_reclassification_rules)

    # FIXME -----------------------------------------------------------------

    '''Water components'''

    lakes = options['lakes']
    lakes_coefficients = options['lakes_coefficients']
    lakes_proximity_map_name = 'lakes_proximity'
    coastline = options['coastline']
    coast_proximity_map_name = 'coast_proximity'
    coast_geomorphology = options['coast_geomorphology']
    # coast_geomorphology_coefficients = options['geomorphology_coefficients']
    coast_geomorphology_map_name = 'coast_geomorphology'
    bathing_water = options['bathing_water']
    bathing_water_coefficients = options['bathing_coefficients']
    bathing_water_proximity_map_name = 'bathing_water_proximity'

    '''Natural components'''

    protected = options['protected']
    protected_scores = options['protected_scores']
    protected_areas_map_name = 'protected_areas'

    '''Anthropic areas'''

    # Rename back to Urban?

    anthropic = options['anthropic']
    anthropic_proximity_map_name='anthropic_proximity'
    anthropic_distance_categories = options['anthropic_distances']

    roads = options['roads']
    roads_proximity_map_name = 'roads_proximity'
    roads_distance_categories = options['roads_distances']

    anthropic_accessibility_map_name='anthropic_accessibility'

    '''Devaluation'''

    devaluation = options['devaluation']

    '''Aggregational boundaries'''

    base = options['base']
    base_vector = options['base_vector']
    aggregation = options['aggregation']

    '''Population'''

    population = options['population']

    '''Outputs'''

    potential_title = "Recreation potential"
    recreation_potential = options['potential']  # intermediate / output
    recreation_potential_map_name = tmp_map_name(name='recreation_potential')

    opportunity_title = "Recreation opportunity"
    recreation_opportunity=options['opportunity']
    recreation_opportunity_map_name='recreation_opportunity'

    spectrum_title = "Recreation spectrum"
    # if options['spectrum']:
    recreation_spectrum = options['spectrum']  # output
    # else:
    #     recreation_spectrum = 'recreation_spectrum'
    # recreation_spectrum_component_map_name =
    #       tmp_map_name(name='recreation_spectrum_component_map')

    spectrum_distance_categories = options['spectrum_distances']
    if ':' in spectrum_distance_categories:
        spectrum_distance_categories = string_to_file(spectrum_distance_categories,
                name=recreation_spectrum)
        # remove_at_exit.append(spectrum_distance_categories) -- Not a map!
        remove_normal_files_at_exit.append(spectrum_distance_categories)

    highest_spectrum = 'highest_recreation_spectrum'
    crossmap = 'crossmap'  # REMOVEME

    # if options['demand']:
    demand = options['demand']
    # else:
    #     demand = 'demand'

    # if options['unmet']:
    unmet_demand = options['unmet']
    # else:
    #     unmet_demand = 'unmet_demand'

    mobility = options['mobility']
    if mobility:
        demand = 'demand'
    mobility_map_name = 'mobility'

    supply = options['supply']  # use as CSV filename prefix

    """ First, care about the computational region"""

    if mask:
        msg = "Masking NULL cells based on '{mask}'".format(mask=mask)
        grass.verbose(_(msg))
        r.mask(raster=mask, overwrite=True, quiet=True)
        draw_map(mask)

    if landuse_extent:
        grass.use_temp_region()  # to safely modify the region
        g.region(flags='p', raster=landuse) # Set region to 'mask'
        msg = "|! Computational resolution matched to {raster}"
        msg = msg.format(raster=landuse)
        g.message(_(msg))

    """Land Component
            or Suitability of Land to Support Recreation Activities (SLSRA)"""

    land_component = []  # a list, use .extend() wherever required

    if land:

        draw_map(land)
        land_component = land.split(',')

    if landuse and suitability_scores:

        draw_map(landuse)
        msg = "Deriving land suitability from '{landuse}' based on '{rules}'"
        grass.verbose(msg.format(landuse=landuse, rules=suitability_scores))

        # suitability = suitability_map_name
        recode_map(raster=landuse,
                rules=suitability_scores,
                colors=SCORE_COLORS,
                output=suitability_map_name)

        append_map_to_component(suitability_map_name, 'land', land_component)

    '''Water Component'''

    water_component = []
    water_components = []

    if water:

        water_component = water.split(',')

        if len(water_component) > 1:
            for component in water_component:
                draw_map(component)
        if len(water_component) == 1:
            draw_map(water_component)

        msg = "Water component includes currently: {component}"
        msg = msg.format(component=water_component)
        grass.debug(_(msg))
        # grass.verbose(_(msg))

    if lakes:

        draw_map(lakes)

        if lakes_coefficients:
            metric, constant, kappa, alpha, score = get_coefficients(lakes_coefficients)

        lakes_proximity = compute_attractiveness(
                raster = lakes,
                metric = EUCLIDEAN,
                constant = constant,
                kappa = kappa,
                alpha = alpha,
                score = score,
                mask = lakes)
        del(constant)
        del(kappa)
        del(alpha)
        del(score)
        append_map_to_component(lakes_proximity, 'water', water_components)

    if coastline:

        draw_map(coastline)
        coast_proximity = compute_attractiveness(
                raster = coastline,
                metric = EUCLIDEAN,
                constant = water_proximity_constant,
                alpha = water_proximity_alpha,
                kappa = water_proximity_kappa,
                score = water_proximity_score)
        append_map_to_component(coast_proximity, 'water', water_components)

    if coast_geomorphology:

        try:

            if not coastline:
                msg = "The coastline map is required in order to compute attractiveness based on the coast geomorphology raster map"
                msg = msg.format(c=water_component)
                grass.fatal(_(msg))

        except NameError:
            grass.fatal(_("No coast proximity"))

        coast_attractiveness = neighborhood_function(
                raster=coast_geomorphology,
                method = NEIGHBORHOOD_METHOD,
                size = NEIGHBORHOOD_SIZE,
                distance_map=coast_proximity)
        append_map_to_component(coast_attractiveness, 'water', water_components)

    if bathing_water:

        draw_map(bathing_water)

        if bathing_water_coefficients:
            metric, constant, kappa, alpha = get_coefficients(bathing_water_coefficients)

        bathing_water_proximity = compute_attractiveness(
                raster = bathing_water,
                metric = EUCLIDEAN,
                constant = constant,
                kappa = kappa,
                alpha = alpha)
        del(constant)
        del(kappa)
        del(alpha)
        append_map_to_component(bathing_water_proximity, 'water',
                water_components)

    # merge water component related maps in one list
    water_component += water_components

    '''Natural Component'''

    natural_component = []
    natural_components = []

    if natural:

        natural_component = natural.split(',')

        if len(natural_component) > 1:
            for component in natural_component:
                draw_map(component)
        if len(natural_component) == 1:
            draw_map(natural_component)

    if protected:
        msg = "Scoring protected areas '{protected}' based on '{rules}'"
        grass.verbose(_(msg.format(protected=protected, rules=protected_scores)))
        draw_map(protected)

        protected_areas = protected_areas_map_name

        recode_map(raster=protected,
                rules=protected_scores,
                colors=SCORE_COLORS,
                output=protected_areas)

        append_map_to_component(protected_areas, 'natural', natural_components)

    # merge natural resources component related maps in one list
    natural_component += natural_components

    """ Normalize land, water, natural inputs
    and add them to the recreation potential component"""

    recreation_potential_component = []

    if land_component:

        for dummy_index in land_component:

            '''
            This section sets NULL cells to 0.
            Because `r.null` operates on the complete input raster map,
            manually subsetting the input map is required.
            '''

            # remove and add later after processing
            land_map = land_component.pop(0)
            suitability_map = tmp_map_name(name=land_map)

            msg = "Subsetting {subset} map".format(subset=suitability_map)
            grass.debug(_(msg))
            del(msg)

            subset_land = equation.format(result = suitability_map,
                    expression = land_map)

            msg = "Expression for Suitability map: {expression}"
            msg = msg.format(expression = subset_land)
            grass.debug(_(msg))
            del(msg)
            r.mapcalc(subset_land)

            grass.debug(_("Setting NULL cells to 0"))
            r.null(map=suitability_map, null=0)  # Set NULLs to 0

            msg = "\nAdding land suitability map '{suitability}' to 'Recreation Potential' component\n"
            msg = msg.format(suitability = suitability_map)
            grass.verbose(_(msg))
            land_component.append(suitability_map)

    if len(land_component) > 1:
        grass.verbose(_("\nNormalize 'Land' component\n"))
        zerofy_and_normalise_component(land_component, THRESHHOLD_ZERO,
                land_component_map_name)
        recreation_potential_component.extend(land_component)
    else:
        recreation_potential_component.extend(land_component)
    remove_at_exit.extend(land_component)

    if len(water_component) > 1:
        grass.verbose(_("\nNormalize 'Water' component\n"))
        zerofy_and_normalise_component(water_component, THRESHHOLD_ZERO,
                water_component_map_name)
        recreation_potential_component.append(water_component_map_name)
    else:
        recreation_potential_component.extend(water_component)
    remove_at_exit.append(water_component_map_name)

    if len(natural_component) > 1:
        grass.verbose(_("\nNormalize 'Natural' component\n"))
        zerofy_and_normalise_component(natural_component, THRESHHOLD_ZERO,
                natural_component_map_name)
        recreation_potential_component.append(natural_component_map_name)
    else:
        recreation_potential_component.extend(natural_component)
    remove_at_exit.append(natural_component_map_name)

    """ Recreation Potential [Output] """

    tmp_recreation_potential = tmp_map_name(name=recreation_potential_map_name)
    msg = "Computing an intermediate potential map '{potential}'"
    grass.debug(_(msg.format(potential=tmp_recreation_potential)))
    # msg +="\n---------------------------------------------------------------\n"
    # grass.message(_(msg.format(potential=tmp_recreation_potential)))

    grass.verbose(_("\nNormalize 'Recreation Potential' component\n"))
    grass.debug(_("Maps: {maps}".format(maps=recreation_potential_component)))

    zerofy_and_normalise_component(recreation_potential_component,
            THRESHHOLD_ZERO, tmp_recreation_potential)

    if recreation_potential:

        msg = "\nReclassifying '{potential}' map"
        msg = msg.format(potential=tmp_recreation_potential)
        grass.verbose(_(msg))
        tmp_recreation_potential_categories = tmp_map_name(name=recreation_potential)
        classify_recreation_component(
                component = tmp_recreation_potential,
                rules = recreation_potential_categories,
                output_name = tmp_recreation_potential_categories)

        # Update category labels ---------------------------------
        potential_categories = 'categories_of_'
        potential_categories += recreation_potential
        # remove_normal_files_at_exit.append(potential_categories)

        potential_category_descriptions = string_to_file(
                POTENTIAL_CATEGORY_LABELS,
                name=potential_categories)

        r.category(map=tmp_recreation_potential_categories,
                rules=potential_category_descriptions,
                separator=':')
        # --------------------------------------------------------

        msg = "\nWriting '{potential}' map\n"
        msg = msg.format(potential=recreation_potential)
        grass.verbose(_(msg))
        g.rename(raster=(tmp_recreation_potential_categories,recreation_potential),
                quiet=True)

        update_meta(recreation_potential, potential_title)
        r.colors(map=recreation_potential, rules='-', stdin = POTENTIAL_COLORS,
                quiet=True)

        del(msg)
        del(tmp_recreation_potential_categories)

    # Infrastructure to access recreational facilities, amenities, services
    # Required for recreation opportunity and successively recreation spectrum

    if infrastructure and not any([recreation_opportunity,
        recreation_spectrum, demand, mobility, supply]):
        msg = ("Infrastructure is not required "
        "to derive the 'potential' recreation map.")
        grass.warning(_(msg))

    if any([recreation_opportunity, recreation_spectrum, demand, mobility,
        supply]):

        infrastructure_component = []
        infrastructure_components = []

        if infrastructure:
            draw_map(infrastructure)
            infrastructure_component.append(infrastructure)

        '''Anthropic surfaces (includung Roads)'''

        if anthropic and roads:

            msg = "Roads distance categories: {c}"
            msg = msg.format(c=roads_distance_categories)
            grass.debug(_(msg))
            roads_proximity = compute_anthropic_proximity(
                    raster = roads,
                    distance_categories = roads_distance_categories,
                    output_name = roads_proximity_map_name)

            msg = "Anthropic distance categories: {c}"
            msg = msg.format(c=anthropic_distance_categories)
            grass.debug(_(msg))
            anthropic_proximity = compute_anthropic_proximity(
                    raster = anthropic,
                    distance_categories = anthropic_distance_categories,
                    output_name = anthropic_proximity_map_name)

            anthropic_accessibility = compute_anthropic_accessibility(
                    anthropic_proximity,
                    roads_proximity,
                    output_name = anthropic_accessibility_map_name)

            infrastructure_components.append(anthropic_accessibility)

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

    if any([recreation_spectrum, demand, mobility, supply]):

        recreation_opportunity_component = []

        # input
        zerofy_and_normalise_component(infrastructure_component,
                THRESHHOLD_ZERO, infrastructure_component_map_name)
        recreation_opportunity_component.append(infrastructure_component_map_name)
        remove_at_exit.append(infrastructure_component_map_name)

        # # input
        # print "Recreation component:", recreation_component
        # print

        # zerofy_and_normalise_component(recreation_component,
        #         THRESHHOLD_0001, recreation_component_map_name)
        # recreation_opportunity_component.append(recreation_component_map_name)
        # remove_at_exit.append(recreation_component_map_name)

        # intermediate
        # ----------------------------------------------------------------------
        # Why threshhold 0.0003? How and why it differs from 0.0001?
        if not recreation_opportunity:
            recreation_opportunity = recreation_opportunity_map_name

        zerofy_and_normalise_component(
                recreation_opportunity_component,
                THRESHHOLD_0003,
                recreation_opportunity)
        # ----------------------------------------------------------------------

        # recode recreation_potential
        tmp_recreation_potential_categories = tmp_map_name(name=tmp_recreation_potential)
        classify_recreation_component(component = tmp_recreation_potential,
                rules = recreation_potential_categories,
                output_name = tmp_recreation_potential_categories)

        # recode opportunity_component
        tmp_recreation_opportunity_categories = tmp_map_name(name=recreation_opportunity)

        msg = "Reclassifying '{opportunity}' map"
        msg = "Computing recreation opportunity {opportunity}"
        msg +="\n---------------------------------------------------------------\n"
        grass.debug(msg.format(opportunity=tmp_recreation_opportunity_categories))
        # grass.message(_(msg.format(opportunity=tmp_recreation_opportunity_categories)))
        del(msg)

        classify_recreation_component(
                component = recreation_opportunity,
                rules = recreation_opportunity_categories,
                output_name = tmp_recreation_opportunity_categories)

        if recreation_opportunity:

            msg = "Writing '{opportunity}' map"
            grass.verbose(msg.format(opportunity=recreation_opportunity))
            del(msg)

            # Update category labels -----------------------------------
            opportunity_categories = 'categories_of_'
            opportunity_categories += recreation_opportunity
            # remove_normal_files_at_exit.append(opportunity_categories)

            opportunity_category_descriptions = string_to_file(
                    OPPORTUNITY_CATEGORY_LABELS,
                    name=opportunity_categories)

            r.category(map=tmp_recreation_opportunity_categories,
                    rules=opportunity_category_descriptions,
                    separator=':')
            # ---------------------------------------------------------

            g.copy(raster=(tmp_recreation_opportunity_categories,
                recreation_opportunity), quiet=True)

            update_meta(recreation_opportunity, opportunity_title)
            r.colors(map=recreation_opportunity, rules='-', stdin =
                    OPPORTUNITY_COLORS, quiet=True)

        # Recreation Spectrum: Potential + Opportunity [Output]

        if not recreation_spectrum and any([demand, mobility, supply]):
            recreation_spectrum = 'recreation_spectrum'
            remove_at_exit.append(recreation_spectrum)

        recreation_spectrum = compute_recreation_spectrum(
                potential = tmp_recreation_potential_categories,
                opportunity = tmp_recreation_opportunity_categories,
                spectrum = recreation_spectrum)

        msg = "Writing '{spectrum}' map"
        msg = msg.format(spectrum=recreation_spectrum)
        grass.verbose(_(msg))
        del(msg)
        get_univariate_statistics(recreation_spectrum)

        # Update category labels --------------------------------
        spectrum_categories = 'categories_of_'
        spectrum_categories += recreation_spectrum
        # remove_normal_files_at_exit.append(spectrum_categories)

        spectrum_category_labels = string_to_file(
                SPECTRUM_CATEGORY_LABELS,
                name=spectrum_categories)

        r.category(map=recreation_spectrum,
                rules=spectrum_category_labels,
                separator=':')
        # -------------------------------------------------------

        update_meta(recreation_spectrum, spectrum_title)
        r.colors(map=recreation_spectrum, rules='-', stdin = SPECTRUM_COLORS,
                quiet=True)

        if base_vector:
            update_vector(vector=base_vector,
                    raster=recreation_spectrum,
                    methods=METHODS,
                    column_prefix='spectrum')

    """Valuation Tables"""

    if demand or mobility or supply:

        '''Highest Recreation Spectrum == 9'''

        expression = "if({spectrum} == {highest_recreation_category}, {spectrum}, null())"
        highest_spectrum_expression = expression.format(
                spectrum=recreation_spectrum,
                highest_recreation_category=HIGHEST_RECREATION_CATEGORY)
        highest_spectrum_equation = equation.format(result=highest_spectrum,
                expression=highest_spectrum_expression)
        r.mapcalc(highest_spectrum_equation, overwrite=True)
        draw_map(highest_spectrum)

        '''Distance map'''

        distance_to_highest_spectrum = tmp_map_name(name=highest_spectrum)
        r.grow_distance(input=highest_spectrum,
                distance=distance_to_highest_spectrum,
                metric=metric,
                quiet=True,
                overwrite=True)
        draw_map(distance_to_highest_spectrum)

        '''Distance categories'''

        distance_categories_to_highest_spectrum = 'categories_of_'
        distance_categories_to_highest_spectrum += distance_to_highest_spectrum
        remove_at_exit.append(distance_categories_to_highest_spectrum)  # FIXME

        recode_map(raster=distance_to_highest_spectrum,
                rules=spectrum_distance_categories,
                colors=SCORE_COLORS,
                output=distance_categories_to_highest_spectrum)

        draw_map(distance_categories_to_highest_spectrum)

        spectrum_distance_category_descriptions = string_to_file(
                SPECTRUM_DISTANCE_CATEGORY_LABELS,
                name=distance_categories_to_highest_spectrum)
        remove_normal_files_at_exit.append(spectrum_distance_category_descriptions)

        r.category(map=distance_categories_to_highest_spectrum,
                rules=spectrum_distance_category_descriptions,
                separator=':')

        '''Combine Base map and Distance Categories'''

        tmp_crossmap = tmp_map_name(name=crossmap)
        r.cross(input=(distance_categories_to_highest_spectrum, base),
                flags='z',
                output=tmp_crossmap,
                quiet=True)
        draw_map(tmp_crossmap)
        remove_at_exit.append(tmp_crossmap)

        # Saving the map derived via `r.cross` -------------------------------
        crossmap_expression = "{crossmap} = {tmp_crossmap}"
        crossmap_expression = crossmap_expression.format(crossmap=crossmap,
                tmp_crossmap=tmp_crossmap)
        crossmap_equation = equation.format(result=crossmap,
                expression=crossmap_expression)
        r.mapcalc(crossmap_equation, overwrite=True)
        draw_map(crossmap)
        # Saving the map derived via `r.cross`--------------------------------

        grass.use_temp_region()  # to safely modify the region
        g.region(raster=population)  # Resolution should match 'population'
        msg = "|! Computational extent & resolution matched to {raster}"
        msg = msg.format(raster=landuse)
        grass.verbose(_(msg))

        population_statistics = get_univariate_statistics(population)
        population_total = population_statistics['sum']
        msg = "|i Population statistics: {s}".format(s=population_total)
        grass.verbose(_(msg))

        #
        ## Reset region resolution
        #
        if not demand and supply:
            demand = 'demand'
            remove_at_exit.append(demand)

        r.stats_zonal(base=crossmap,
                flags='r',
                cover=population,
                method='sum',
                output=demand,
                overwrite=True,
                quiet=True)
        draw_map(demand)

        if base_vector:

            update_vector(vector=base_vector,
                    raster=demand,
                    methods=METHODS,
                    column_prefix='demand')

        '''Mobility function'''

        mobility_expression = compute_mobility(
                distance_map=distance_categories_to_highest_spectrum,
                constant=MOBILITY_CONSTANT,
                coefficients=MOBILITY_COEFFICIENTS,
                population=demand,
                score=MOBILITY_SCORE)
        grass.debug(_("Mobility function: {f}".format(f=mobility_expression)))

        mobility_equation = equation.format(result=mobility_map_name,
                expression=mobility_expression)
        r.mapcalc(mobility_equation, overwrite=True)
        draw_map(mobility_map_name, width='45', height='45')

        if base_vector:

            update_vector(vector=base_vector,
                    raster=mobility_map_name,
                    methods=METHODS,
                    column_prefix='mobility')

        if unmet_demand:

            '''Unmet Demand'''
            unmet_demand_expression = compute_unmet_demand(
                    distance_map=distance_categories_to_highest_spectrum,
                    constant=MOBILITY_CONSTANT,
                    coefficients=MOBILITY_COEFFICIENTS[4],
                    population=demand,
                    score=MOBILITY_SCORE)
            grass.debug(_("Unmet demand function: {f}".format(f=unmet_demand_expression)))

            unmet_demand_equation = equation.format(result=unmet_demand,
                    expression=unmet_demand_expression)
            r.mapcalc(unmet_demand_equation, overwrite=True)
            draw_map(unmet_demand, width='45', height='45')

            if base_vector:

                update_vector(vector=base_vector,
                        raster=unmet_demand,
                        methods=METHODS,
                        column_prefix='unmet')

    '''Supply Table'''

    if supply:

        grass.del_temp_region()  # restoring previous region settings
        grass.verbose("Original Region restored")

        compute_supply_table(base=base,
                landcover=landcover,
                reclassification_rules=landcover_reclassification_rules,
                reclassified_landcover=maes_landcover,
                title="MAES land class nomenclature",
                recreation_spectrum=recreation_spectrum,
                highest_spectrum=highest_spectrum,
                mobility=mobility_map_name,
                prefix=supply)

    '''Aggregate per region'''

    if aggregation:

        r.mask(raster=highest_spectrum, overwrite=True, quiet=True)

        mobility_in_landcover = mobility + '_' + landcover
        r.stats_zonal(base=maes_landcover,
                flags='r',
                cover=mobility_map_name,
                method='sum',
                output=mobility_in_landcover,
                overwrite=True)

        r.colors(map=mobility_in_landcover,
            color=MOBILITY_COLORS,
            quiet=True)
        draw_map(mobility_in_landcover)

        region_fragment_patches = []  # FIXME REMOVEME

        regions = grass.read_command('r.category', map=aggregation).split()
        for region in regions:

            grass.debug(_("Region: {r}".format(r=region)))

            # grass.use_temp_region()  # to safely modify the region

            g.region(raster=aggregation, quiet=True)  # Set region to 'mask'
            msg = "|! Computational resolution matched to {raster} [{region}]"
            msg = msg.format(raster=aggregation, region=region)
            grass.debug(_(msg))

            # MASK region
            grass.verbose(_("Setting map '{r}' as a MASK".format(r=aggregation)))
            r.mask(raster=aggregation,
                    maskcats=region,
                    overwrite=True,
                    quiet=True)

            # zoom to MASK
            g.region(zoom='MASK', quiet=True)

            # r.stats mobility_per_land_class -cap
            draw_map(mobility_in_landcover, suffix=region)

            statistics_filename = 'statistics_' + mobility_in_landcover + '_' + region
            r.stats(input=mobility_in_landcover,
                    output=statistics_filename,
                    flags='nacpl',
                    separator=COMMA,
                    quiet=True)
            del(statistics_filename)

            # remove MASK
            r.mask(flags='r', quiet=True)

    # restore region
    if landuse_extent:
        grass.del_temp_region()  # restoring previous region settings
        grass.verbose("Original Region restored")

    # print citation
    if info:
        citation = 'Citation: ' + citation_recreation_potential
        g.message(citation)

    # if remove_at_exit:
    #     g.message("Removing temporary intermediate maps")
    #     g.remove(flags='f', type='raster', name=','.join(remove_at_exit),
    #             quiet=True)
    #     g.message("*** Please remove the grass_render_file ***")

    if remove_normal_files_at_exit:
        for item in remove_normal_files_at_exit:
            os.unlink(item)

if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    sys.exit(main())
