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

               This program is free software under the GNU General Public
               License (>=v2). Read the file COPYING that comes with GRASS
               for details.
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

#%option G_OPT_R_INPUTS
#% key: land
#% type: string
#% key_desc: name
#% label: Maps scoring access to and suitability of land resources for recreation
#% description: Arbitrary number of maps scoring access to and land resources suitability of land use classes to support recreation activities
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: water
#% key_desc: name
#% label: Maps scoring access to and quality of water resources
#% description: Arbitrary number of maps scoring access to and quality of water resources such as lakes, sea, bathing waters and riparian zones
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUT
#% key: marine
#% key_desc: name
#% label: Map scoring access to marine natural provided areas
#% description: Access to marine natural protected areas
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUTS
#% key: natural
#% key_desc: name
#% label: Maps scoring access to and quality of inland natural resources
#% description: Arbitrary number of maps scoring access to and quality of inland natural resources
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: urban
#% key_desc: name
#% description: Maps scoring recreational value of urban surfaces
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: infrastructure
#% type: string
#% key_desc: name
#% label: Maps scoring infrastructure to reach locations of recreation activities
#% description: Infrastructure to reach locations of recreation activities [required to derive recreation spectrum map]
#% required: no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: recreation
#% type: string
#% key_desc: name
#% label: Maps scoring recreational facilities, amenities and services
#% description: Recreational opportunities facilities, amenities and services [required to derive recreation spectrum map]
#% required: no
#% guisection: Components
#%end

'''Land'''

#%option G_OPT_R_INPUT
#% key: landuse
#% type: string
#% key_desc: name
#% label: Land use map from which to derive suitability for recreation
#% description: Input to derive suitability of land use classes to support recreation activities. Requires scores, overrides suitability.
#% required : no
#% guisection: Land
#%end

#%option G_OPT_F_INPUT
#% key: suitability_scores
#% type: string
#% key_desc: filename
#% label: Recreational suitability scores for the classes of the 'landuse' map
#% description: Scores for suitability of land to support recreation activities. Expected are rules for `r.recode` that correspond to classes of the input land use map. If 'landuse' map given and 'suitability_scores' not provided, the module will use internal rules for the CORINE land classes
#% required: no
#% guisection: Land
#%end

'''Water'''

#%option G_OPT_R_INPUT
#% key: lakes
#% key_desc: name
#% label: Lakes map for which to score accessibility
#% description: Lakes map to compute proximity for, score accessibility based on a distance function
#% required : no
#% guisection: Water
#%end

#%option
#% key: lakes_coefficients
#% type: string
#% key_desc: Coefficients
#% label: Distance function coefficients
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
#% label: Sea coast map for which to compute proximity
#% description: Input map to compute coast proximity, scored based on a distance function
#% required : no
#% guisection: Water
#%end

#%option
#% key: coastline_coefficients
#% key_desc: Coefficients
#% label: Distance function coefficients
#% description: Distance function coefficients to compute proximity: distance metric, constant, kappa, alpha and score. Refer to the manual for details.
#% multiple: yes
#% required: no
#% guisection: Water
#% answer: euclidean,1,30,0.008,1
#%end

#%option G_OPT_R_INPUT
#% key: coast_geomorphology
#% key_desc: name
#% label: Map scoring recreation potential in coast
#% description: Coastal geomorphology, scored as suitable to support recreation activities
#% required : no
#% guisection: Water
#%end

#%option
#% key: geomorphology_coefficients
#% key_desc: Coefficients
#% label: Distance function coefficients
#% description: Distance function coefficients to compute proximity: distance metric, constant, kappa, alpha and score. Refer to the manual for details.
#% multiple: yes
#% required: no
#% guisection: Water
#% answer: euclidean,1,30,0.008,1
#%end

#%option G_OPT_R_INPUT
#% key: water_clarity
#% key_desc: name
#% label: Water clarity
#% description: Water clarity. The higher, the greater the recreation value.
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: bathing_water
#% key_desc: filename
#% label: Bathing water quality
#% description: Bathing Water Quality Index. The higher, the greater is the recreational value.
#% required : no
#% guisection: Water
#%end

#%option
#% key: bathing_coefficients
#% type: string
#% key_desc: Coefficients
#% label: Distance function coefficients
#% description: Distance function coefficients to compute proximity to bathing waters: distance metric, constant, kappa and alpha. Refer to the manual for details.
#% multiple: yes
#% required: no
#% guisection: Water
#% answer: euclidean,1,5,0.01101
#%end

#%rules
#%  requires: bathing_water, bathing_coefficients
#%end

#%option G_OPT_R_INPUT
#% key: riparian
#% key_desc: name
#% label: Riparian zones
#% description: Riparian zones
#% required : no
#% guisection: Water
#%end

##%rules
##%  exclusive: lakes
##%  exclusive: coastline
##%  excludes: water, coast_geomorphology, water_clarity, coast_proximity, marine, lakes, lakes_proximity, bathing_water
##%end

'''Natural'''

#%option G_OPT_R_INPUT
#% key: protected
#% key_desc: filename
#% label: Protected areas
#% description: Natural Protected Areas
#% required : no
#% guisection: Natural
#%end

#%option G_OPT_R_INPUT
#% key: protected_scores
#% type: string
#% key_desc: rules
#% label: Recreational value scores for the classes of the 'protected' map
#% description: Scores for recreational value of designated areas. Expected are rules for `r.recode` that correspond to classes of the input land use map. If the 'protected' map is given and 'protected_scores' are not provided, the module will use internal rules for the IUCN categories.
#% required : no
#% guisection: Anthropic
#% answer: 11:11:0\n12:12:0.6\n2:2:0.8\n3:3:0.6\n4:4:0.6\n5:5:1\n6:6:0.8\n7:7:0\n8:8:0\n9:9:0
#%end

#%option G_OPT_R_INPUT
#% key: forest
#% key_desc: filename
#% label: Forested areas
#% description: Access to forested areas
#% required : no
#% guisection: Natural
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
#% label: Map of artificial surfaces and agricultural areas
#% description: Partial input map to compute anthropic areas proximity, scored via a distance function
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: distance_classes
#% type: string
#% key_desc: rules
#% label: Distance classification rules
#% description: Classes for distance to anthropic surfaces. Expected are rules for `r.recode` that correspond to classes of the input land use map.
#% required : no
#% guisection: Anthropic
#% answer: 0:500:1\n500.000001:1000:2\n1000.000001:5000:3\n5000.000001:10000:4\n10000.00001:*:5
#%end

#%option G_OPT_R_INPUT
#% key: green_urban
#% key_desc: name
#% label: Urban green surfaces
#% description: Map scoring urban green surfaces
#% required : no
#% guisection: Urban
#%end

#%option G_OPT_R_INPUT
#% key: green_infrastructure
#% key_desc: filename
#% label: Urban green infrastructure
#% description: Map scoring urban green infrastructure
#% required : no
#% guisection: Urban
#%end

'''Roads'''

#%option G_OPT_R_INPUT
#% key: roads
#% key_desc: name
#% label: Primary road network
#% description: Input map to compute roads proximity, scored based on a distance function
#% required : no
#% guisection: Infrastructure
#%end

#%option G_OPT_F_INPUT
#% key: roads_scores
#% type: string
#% key_desc: name
#% label: Roads classification rules
#% description: Rules to compute proximity to roads. Expected are rules for `r.recode` that correspond to classes of the input land use map.
#% required: no
#% guisection: Land
#%end

#%option G_OPT_R_INPUT
#% key: roads_secondary
#% key_desc: name
#% label: Secondary road network
#% description: Secondary network including arterial and collector roads
#% required : no
#% guisection: Infrastructure
#%end

#%option G_OPT_R_INPUT
#% key: roads_local
#% key_desc: name
#% label: Local road network
#% description: Local roads and streets
#% required : no
#% guisection: Infrastructure
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

#%option G_OPT_R_INPUTS
#% key: osm_lines
#% key_desc: name
#% label: OpenStreetMap linear features
#% description: OpenStreetMap linear features
#% required : no
#% guisection: Recreation
#%end

#%option G_OPT_R_INPUTS
#% key: osm_points
#% key_desc: name
#% label: OpenStreetMap point features
#% description: OpenStreetMap point features
#% required : no
#% guisection: Recreation
#%end

#%option G_OPT_R_INPUT
#% key: blue_flags
#% key_desc: name
#% label: Moorings with blue flag distinction
#% description: Moorings with blue flag distinction
#% required : no
#% guisection: Recreation
#%end

'''Devaluation'''

#%option G_OPT_R_INPUTS
#% key: devaluation
#% key_desc: name
#% label: Devaluing elements
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
#% label: Recreation potential output map
#% description: Recreation potential map classified in 3 categories
#% required: no
#% guisection: Output
#%end

#%option G_OPT_R_OUTPUT
#% key: opportunity
#% key_desc: name
#% label: Recreation opportunity output map
#% description: Recreation opportunity map classified in 3 categories
#% required: no
#% guisection: Output
#%end

#%option G_OPT_R_OUTPUT
#% key: spectrum
#% key_desc: name
#% label: Recreation spectrum output map
#% description: Recreation spectrum map classified by default in 9 categories
#% required: no
#% guisection: Output
#%end

#%rules
#%  required: potential, spectrum
#%  requires: spectrum, infrastructure, roads, roads_secondary, roads_local
#%  requires: spectrum, recreation, osm_lines, osm_points, blue_flags
#%end

'''Various'''

#%option
#% key: metric
#% key_desc: Metric
#% label: Distance metric for proximity
#% description: Distance metric to base proximity computations
#% multiple: yes
#% options: euclidean,squared,maximum,manhattan,geodesic
#% required: no
#% guisection: Output
#% answer: euclidean
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
# grass_render_file = grass_render_directory + 'grass_render_file.png'  # REMOVE ME

global equation, citation, spacy_plus
citation_recreation_potential='Zulian (2014)'
spacy_plus = ' + '
equation = "{result} = {expression}"  # basic equation for mapcalc

global THRESHHOLD_ZERO, THRESHHOLD_0001, THRESHHOLD_0003
THRESHHOLD_ZERO = 0
THRESHHOLD_0001 = 0.0001
THRESHHOLD_0003 = 0.0003

euclidean='euclidean'
water_proximity_constant=1
water_proximity_kappa=30
water_proximity_alpha=0.008
water_proximity_score=1
bathing_water_proximity_constant=1
bathing_water_proximity_kappa=5
bathing_water_proximity_alpha=0.1101

suitability_classification_classes=''
recreation_potential_classes='''0.0:0.2:1
0.2:0.4:2
0.4:*:3'''
anthropic_distance_classes='0:500:1\n500.000001:1000:2\n1000.000001:5000:3\n5000.000001:10000:4\n10000.00001:*:5'
recreation_opportunity_classes=recreation_potential_classes

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

# helper functions

def run(cmd, **kwargs):
    """Pass required arguments to grass commands (?)"""
    grass.run_command(cmd, quiet=True, **kwargs)

def tmp_map_name(name):
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
    temporary_filename = temporary_filename + '.' + str(name)
    return temporary_filename

def cleanup():
    """Clean up temporary maps"""
    run('g.remove', flags='f', type="rast",
            pattern='tmp.{pid}*'.format(pid=os.getpid()))

    if grass.find_file(name='MASK', element='cell')['file']:
        r.mask(flags='r', verbose=True)

def draw_map(mapname):
    """Set the GRASS_RENDER_FILE and draw the requested raster map"""
    if flags['d']:
        render_file = "{directory}/{name}.{extension}"
        render_file = render_file.format(
                directory = grass_render_directory,
                name = mapname,
                extension = 'png')

        os.putenv("GRASS_RENDER_FILE", render_file)

        run("d.erase", bgcolor='black', flags='f')
        run("d.rast", map=mapname)
        # run("d.rast.leg", map=mapname)

        grass.verbose(_(">>> {filename}".format(filename=render_file)))
        command = "tycat -g 30x30 {filename}"
        command = command.format(filename=render_file)
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
        ...
    
    component_name :
        ...
        
    component_list :
        List of raster maps to add the input 'raster' map
        
    Returns
    -------
    
    Examples
    --------
    ...
    """
    component_list.append(raster)
    msg = "Map {name} added for inclusion in the {component}"
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

    r.null(map=output, null=0)  # Set NULLs to 0

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
    tmp_distance = tmp_map_name('_'.join([raster, metric]))
    grass.run_command('r.grow.distance',
                      input=raster,
                      distance=tmp_distance,
                      metric=metric,
                      quiet=True,
                      overwrite=True)

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

    # if info:
    #     msg = "Distance function: {f}".format(f=distance_function)
    #     grass.message(_(msg))

    # temporary maps will be removed
    if 'output_name' in kwargs:
        tmp_distance_map = tmp_map_name(kwargs.get('output_name'))  
    else:
        tmp_distance_map = tmp_map_name('attractiveness_map')

    # print "tmp_distance_map", tmp_distance_map

    distance_function = equation.format(result=tmp_distance_map,
            expression=distance_function)
    if info:
        msg = "Distance function: {f}".format(f=distance_function)
        grass.message(_(msg))

    grass.mapcalc(distance_function, overwrite=True)


    r.null(map=tmp_distance_map, null=0)  # Set NULLs to 0

    if 'filter_method' in kwargs:
        neighborhood_method = kwargs.get('filter_method')
        # grass.verbose(_("Filter method {m}".format(m=neighborhood_method)))

        if 'filter_size' in kwargs:
            neighborhood_size = kwargs.get('filter_size')
        else:
            neighborhood_size = 11

        # grass.verbose(_("Filter size {s}".format(s=neighborhood_size)))

        neighborhood_output = tmp_distance_map + '_' + neighborhood_method
        msg = "Neighborhood operator {method} (size: {size}) for {name}"
        msg = msg.format(method=neighborhood_method, size=neighborhood_size,
                name=neighborhood_output)
        grass.verbose(_(msg))
        r.neighbors(input=tmp_distance_map,
                output=neighborhood_output,
                method=neighborhood_method,
                size=neighborhood_size,
                overwrite=True)

        neighborhood_function = "{neighborhood} * {distance}"
        neighborhood_function = neighborhood_function.format(neighborhood=neighborhood_output,
                distance=tmp_distance_map)

        filtered_output = tmp_distance_map + '_' + neighborhood_method + '_' + neighborhood_size
        neighborhood_function = equation.format(result=filtered_output,
                expression=neighborhood_function)
        grass.mapcalc(neighborhood_function, overwrite=True)

        draw_map(filtered_output)
        tmp_distance_map = filtered_output

        del(neighborhood_method)
        del(neighborhood_size)
        del(neighborhood_output)
        del(neighborhood_function)
        del(filtered_output)

    #
    # Supress print of message when verbose=False
    #
    r.compress(tmp_distance_map, flags='g')

    del(numerator)
    del(denominator)
    del(distance_function)

    tmp_output = save_map(tmp_distance_map)
    draw_map(tmp_distance_map)
    return tmp_distance_map

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

    if minimum is None or maximum is None:
        msg = "Minimum and maximum values of the <{raster}> map are 'None'. "
        msg += "The {raster} map may be empty "
        msg += "OR the MASK opacifies all non-NULL cells."
        grass.fatal(_(msg.format(raster=raster)))

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
    # grass.verbose(_(msg))

    if len(components) > 1:

        # prepare string for mapcalc expression
        components = [ name.split('@')[0] for name in components ]
        components_string = spacy_plus.join(components).replace(' ', '').replace('+', '_')

        # temporary map names
        tmp_intermediate = tmp_map_name(components_string)
        tmp_output = tmp_map_name(components_string)

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
        tmp_output = tmp_map_name(tmp_intermediate)

    if threshhold > THRESHHOLD_ZERO:
        msg = "Setting values < {threshhold} in '{raster}' to zero"
        grass.verbose(msg.format(threshhold=threshhold, raster=tmp_intermediate))
        zerofy_small_values(tmp_intermediate, threshhold, tmp_output)

    else:
        tmp_output = tmp_intermediate

    # grass.verbose(_("Temporary map name: {name}".format(name=tmp_output)))
    grass.debug(_("Output map name: {name}".format(name=output_name)))
    # r.info(map=tmp_output, flags='gre')
    normalize_map(tmp_output, output_name)

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

def compute_anthropic_proximity(raster, distance_classes, **kwargs):
    """
    Compute proximity to anthropic surfaces

    1. Distance to features
    2. Classify distances

    Parameters
    ----------
    raster :
        Name of input raster map

    distance_classes :
        Distance classes for ...

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
    anthropic_distances = tmp_map_name(raster)

    grass.run_command("r.grow.distance",
            input = raster,
            distance = anthropic_distances,
            metric = euclidean,
            quiet = True,
            overwrite = True)

    if 'output_name' in kwargs:
        tmp_output = tmp_map_name(kwargs.get('output_name'))  # temporary maps will be removed
        grass.debug(_("Pre-defined output map name {name}".format(name=tmp_output)))

    else:
        tmp_output = tmp_map_name('anthropic_proximity')
        grass.debug(_("Hardcoded temporary map name {name}".format(name=tmp_output)))

    #
    # Fix Here! Above & Below!
    #

    # msg = "Output map name: {proximity}"
    # msg = msg.format(proximity=anthropic_proximity_map_name)
    # grass.debug(_(msg))

    # compute proximity to roads
    msg = "Computing proximity to '{mapname}'"
    msg = msg.format(mapname=raster)
    grass.verbose(_(msg))
    grass.run_command("r.recode",
            input = anthropic_distances,
            output = tmp_output,
            rules = distance_classes,
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
        tmp_output = tmp_map_name(kwargs.get('output_name'))  # temporary maps will be removed

    else:
        tmp_output = tmp_map_name('anthropic_accessibility')

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

    spectrum :
        Name for Spectrum of Recreation map

    Returns
    -------
        Does not return any value
    
    Examples
    --------
    ...
    """
    spectrum_expression = recreation_spectrum_expression(potential,
            opportunity)

    spectrum_equation = equation.format(result=spectrum,
            expression=spectrum_expression)

    if info:
        msg = "Recreation Spectrum equation: \n"
        msg += spectrum_equation
        g.message(msg)
        del(msg)

    grass.mapcalc(spectrum_equation, overwrite=True)

    draw_map(spectrum)

    del(spectrum_expression)
    del(spectrum_equation)

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
    remove_at_exit = []

    '''names for input, output, output suffix, options'''

    # following some hard-coded names -- review and remove!

    land = options['land']
    land_component_map_name = tmp_map_name('land_component')

    water = options['water']
    water_component_map_name = tmp_map_name('water_component')

    natural = options['natural']
    natural_component_map_name = tmp_map_name('natural_component')

    urban = options['urban']
    urban_component_map='urban_component'

    infrastructure = options['infrastructure']
    infrastructure_component_map_name = tmp_map_name('infrastructure_component')

    recreation = options['recreation']
    recreation_component_map_name = tmp_map_name('recreation_component')

    '''Land components'''

    landuse = options['landuse']
    suitability_scores = options['suitability_scores']
    if suitability_scores:
        msg = "Suitability scores from file: {scores}."
        msg = msg.format(scores = suitability_scores)
        grass.verbose(_(msg))

    suitability_map_name = tmp_map_name('suitability')
    if landuse and not suitability_scores:
        msg = "Using internal rules to score land use classes in {map}"
        msg = msg.format(map=landuse)
        g.message(_(msg))
        suitability_scores = recreation_potential_classes

    '''Water components'''

    lakes = options['lakes']
    lakes_coefficients = options['lakes_coefficients']
    lakes_proximity_map_name = 'lakes_proximity'
    water_clarity = options['water_clarity']
    coastline = options['coastline']
    coast_proximity_map_name = 'coast_proximity'
    coast_geomorphology = options['coast_geomorphology']
    coast_geomorphology_coefficients = options['geomorphology_coefficients']
    coast_geomorphology_map_name = 'coast_geomorphology'
    bathing_water = options['bathing_water']
    bathing_water_coefficients = options['bathing_coefficients']
    bathing_water_proximity_map_name = 'bathing_water_proximity'
    marine = options['marine']
    riparian = options['riparian']

    '''Natural components'''

    protected = options['protected']
    protected_scores = options['protected_scores']
    protected_areas_map_name = 'protected_areas'
    forest = options['forest']

    '''Anthropic areas'''

    anthropic = options['anthropic']
    anthropic_proximity_map_name='anthropic_proximity'

    green_urban = options['green_urban']
    green_infrastructure = options['green_infrastructure']

    roads = options['roads']
    roads_proximity_map_name = 'roads_proximity'
    roads_secondary = options['roads_secondary']
    roads_local = options['roads_local']

    anthropic_distance_classes = options['distance_classes']
    roads_distance_classes = anthropic_distance_classes  # re-use anthropic's
    anthropic_accessibility_map_name='anthropic_accessibility'

    mask = options['mask']

    osm_lines = options['osm_lines']
    osm_points = options['osm_points']

    blue_flags = options['blue_flags']

    devaluation = options['devaluation']

    '''Outputs'''

    potential_title = "Recreation potential"
    recreation_potential = options['potential']  # intermediate / output
    recreation_potential_map_name = tmp_map_name('recreation_potential')

    opportunity_title = "Recreation opportunity"
    recreation_opportunity=options['opportunity']
    recreation_opportunity_map_name='recreation_opportunity'

    spectrum_title = "Recreation spectrum"
    recreation_spectrum = options['spectrum']  # output
    # recreation_spectrum_component_map_name =
    #       tmp_map_name('recreation_spectrum_component_map')

    """ First, care about the computational region"""

    if mask:
        # global mask
        msg = "Masking NULL cells based on '{mask}'".format(mask=mask)
        grass.verbose(_(msg))
        r.mask(raster=mask, overwrite=True, quiet=True)
        draw_map(mask)

    if landuse_extent:
        grass.use_temp_region()  # to safely modify the region
        g.region(flags='p', rast=mask) # Set region to 'mask'
        msg = "|! Computational resolution matched to {raster}"
        msg = msg.format(raster=landuse)
        g.message(_(msg))

    """Land Component
            or Suitability of Land to Support Recreation Activities (SLSRA)"""

    land_component = []  # is a list, take care to use .extend() where required

    if land:

        draw_map(land)
        land_component = land.split(',')

    if landuse and suitability_scores:

        msg = "Deriving land suitability from '{landuse}' based on '{rules}'"
        g.message(msg.format(landuse=landuse, rules=suitability_scores))
        draw_map(landuse)

        suitability = suitability_map_name

        recode_map(raster=landuse,
                rules=suitability_scores,
                colors=SCORE_COLORS,
                output=suitability)

        append_map_to_component(suitability, 'land', land_component)

    # 'land' and 'suitability' input maps are *now* programmaticaly exclusive
    # Below, an old approach merging land component related maps in one list.
    # Which, in turn, implies the option to use both the 'land' and 'landuse'
    # input options.
    # land_component += land_components

    '''Water Component'''

    water_component = []
    water_components = []

    if water:
        water_component = water.split(',')
        msg = "Water component holds currently: {component}"
        msg = msg.format(component=water_component)
        grass.verbose(_(msg))

        # Avoid going through the rest?
        # Should water_component  AND  water_components be exclusive!

    if lakes:

        if lakes_coefficients:
            lakes_coefficients = lakes_coefficients.split(',')
            lakes_proximity_metric = lakes_coefficients[0]
            lakes_proximity_constant = lakes_coefficients[1]
            lakes_proximity_kappa = lakes_coefficients[2]
            lakes_proximity_alpha = lakes_coefficients[3]
            lakes_proximity_score = lakes_coefficients[4]
            msg = "Distance function coefficients: "
            msg += "Metric='{metric}', "
            msg += "Constant='{constant}', "
            msg += "Kappa='{Kappa}', "
            msg += "Alpha='{alpha}', "
            msg += "Score='{score}'"
            msg = msg.format(metric=lakes_proximity_metric,
                             constant=lakes_proximity_constant,
                             Kappa=lakes_proximity_kappa,
                             alpha=lakes_proximity_alpha,
                             score=lakes_proximity_score)
            msg = msg.format(coefficients=lakes_coefficients)
            grass.verbose(_(msg))

        lakes_proximity = compute_attractiveness(
                raster = lakes,
                metric = euclidean,
                constant = lakes_proximity_constant,
                alpha = lakes_proximity_alpha,
                kappa = lakes_proximity_kappa,
                score = lakes_proximity_score,
                output_name = lakes_proximity_map_name)

        # ----------------------------------------------------------
        # what is the purpose of the 'output_name' if the
        # `compute_attractiveness()` function creates internally a
        # temporary map name, which will be removed at the end of the
        # script?
        # ----------------------------------------------------------

        append_map_to_component(lakes_proximity, 'water', water_components)

    if water_clarity:
        append_map_to_component(water_clarity, 'water', water_components)

    if coastline:
        coast_proximity = compute_attractiveness(
                raster = coastline,
                metric = euclidean,
                constant = water_proximity_constant,
                alpha = water_proximity_alpha,
                kappa = water_proximity_kappa,
                score = water_proximity_score,
                output_name = coast_proximity_map_name)

        # ----------------------------------------------------------
        # what is the purpose of the 'output_name' if the
        # `compute_attractiveness()` function creates internally a
        # temporary map name, which will be removed at the end of the
        # script?
        # ----------------------------------------------------------

        append_map_to_component(coast_proximity, 'water', water_components)

    if coast_geomorphology:

        if coast_geomorphology_coefficients:
            coast_geomorphology_coefficients = coast_geomorphology_coefficients.split(',')
            coast_geomorphology_metric = coast_geomorphology_coefficients[0]
            coast_geomorphology_constant = coast_geomorphology_coefficients[1]
            coast_geomorphology_kappa = coast_geomorphology_coefficients[2]
            coast_geomorphology_alpha = coast_geomorphology_coefficients[3]
            coast_geomorphology_score = coast_geomorphology_coefficients[4]
            msg = "Distance function coefficients: "
            msg += "Metric='{metric}', "
            msg += "Constant='{constant}', "
            msg += "Kappa='{Kappa}', "
            msg += "Alpha='{alpha}', "
            msg = msg.format(metric=coast_geomorphology_metric,
                             constant=coast_geomorphology_constant,
                             Kappa=coast_geomorphology_kappa,
                             alpha=coast_geomorphology_alpha)
            msg = msg.format(coefficients=coast_geomorphology_coefficients)
            grass.verbose(_(msg))

        coast_geomorphology = compute_attractiveness(
                raster = coast_geomorphology,
                metric = euclidean,
                constant = coast_geomorphology_constant,
                kappa = coast_geomorphology_kappa,
                alpha = coast_geomorphology_alpha,
                score = coast_geomorphology_score,
                filter_method = 'mode',
                filter_size = '11',
                output_name = coast_geomorphology_map_name)

        # ----------------------------------------------------------
        # what is the purpose of the 'output_name' if the
        # `compute_attractiveness()` function creates internally a
        # temporary map name, which will be removed at the end of the
        # script?
        # ----------------------------------------------------------

        append_map_to_component(coast_geomorphology, 'water', water_components)

    if bathing_water:

        if bathing_water_coefficients:
            bathing_water_coefficients = bathing_water_coefficients.split(',')
            bathing_water_proximity_metric = bathing_water_coefficients[0]
            bathing_water_proximity_constant = bathing_water_coefficients[1]
            bathing_water_proximity_kappa = bathing_water_coefficients[2]
            bathing_water_proximity_alpha = bathing_water_coefficients[3]
            msg = "Distance function coefficients: "
            msg += "Metric='{metric}', "
            msg += "Constant='{constant}', "
            msg += "Kappa='{Kappa}', "
            msg += "Alpha='{alpha}', "
            msg = msg.format(metric=bathing_water_proximity_metric,
                             constant=bathing_water_proximity_constant,
                             Kappa=bathing_water_proximity_kappa,
                             alpha=bathing_water_proximity_alpha)
            msg = msg.format(coefficients=bathing_water_coefficients)
            grass.verbose(_(msg))

        bathing_water_proximity = compute_attractiveness(
                raster = bathing_water,
                metric = euclidean,
                constant = bathing_water_proximity_constant,
                alpha = bathing_water_proximity_alpha,
                kappa = bathing_water_proximity_kappa,
                output_name = bathing_water_proximity_map_name)

        # ----------------------------------------------------------
        # what is the purpose of the 'output_name' if the
        # `compute_attractiveness()` function creates internally a
        # temporary map name, which will be removed at the end of the
        # script?
        # ----------------------------------------------------------

        append_map_to_component(bathing_water_proximity, 'water',
                water_components)

    if marine:
        append_map_to_component(marine, 'water', water_components)

    if riparian:
        append_map_to_component(riparian, 'water', water_components)

    # merge water component related maps in one list
    water_component += water_components

    '''Natural Component'''

    natural_component = []
    natural_components = []

    if natural:
        natural_component = natural.split(',')

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

    if forest:
        natural_components.append(forest)

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
            suitability_map = tmp_map_name(land_map)

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

    tmp_recreation_potential = tmp_map_name(recreation_potential_map_name)
    msg = "Computing an intermediate potential map '{potential}'"
    grass.debug(_(msg.format(potential=tmp_recreation_potential)))

    grass.verbose(_("\nNormalize 'Recreation Potential' component\n"))
    grass.debug(_("Maps: {maps}".format(maps=recreation_potential_component)))

    zerofy_and_normalise_component(recreation_potential_component,
            THRESHHOLD_ZERO, tmp_recreation_potential)

    if recreation_potential:

        msg = "\nReclassifying '{potential}' map"
        msg = msg.format(potential=tmp_recreation_potential)
        grass.verbose(_(msg))
        tmp_recreation_potential_classes = tmp_map_name(recreation_potential)
        classify_recreation_component(
                tmp_recreation_potential,
                recreation_potential_classes,
                tmp_recreation_potential_classes)

        msg = "\nWriting <{potential}> map\n"
        msg = msg.format(potential=recreation_potential)
        grass.verbose(_(msg))
        g.rename(raster=(tmp_recreation_potential_classes,recreation_potential),
                quiet=True)

        update_meta(recreation_potential, potential_title)
        r.colors(map=recreation_potential, rules='-', stdin = POTENTIAL_COLORS,
                quiet=True)

        del(msg)
        del(tmp_recreation_potential_classes)

    # Infrastructure to access recreational facilities, amenities, services
    # Required for recreation opportunity and successively recreation spectrum

    if infrastructure and not any([recreation_opportunity, recreation_spectrum]):
        msg = "Infrastructure is only required to derive "
        msg += "the recreation opportunity and, successively, "
        msg += "the recreation spectrum!"
        grass.warning(_(msg))

    if any([recreation_opportunity, recreation_spectrum]):

        infrastructure_component = []
        infrastructure_components = []

        if infrastructure:
            infrastructure_component.append(infrastructure)

        '''Anthropic surfaces (includung Roads)'''

        if anthropic and roads_secondary:
            g.message(_("Computing proximity to secondary roads"))
            compute_anthropic_proximity(roads_secondary,
                    output_name=roads_secondary_proximity)
            # infrastructure_components.append(roads_secondary_proximity)

        if anthropic and roads_local:
            g.message(_("Computing proximity to local roads"))
            compute_anthropic_proximity(roads_local,
                    output_name=roads_local_proximity)
            # infrastructure_components.append(roads_local_proximity)

        if anthropic and roads:

            roads_proximity = compute_anthropic_proximity(
                    raster = roads,
                    distance_classes = roads_distance_classes,
                    output_name=roads_proximity_map_name)

            try:
                if roads_secondary_proximity:
                    print "Do something"

                if roads_local_proximity:
                    print "Do something"
            except:
                pass

            anthropic_proximity = compute_anthropic_proximity(
                    raster = anthropic,
                    distance_classes = anthropic_distance_classes,
                    output_name=anthropic_proximity_map_name)

            anthropic_accessibility = compute_anthropic_accessibility(
                    anthropic_proximity,
                    roads_proximity,
                    output_name=anthropic_accessibility_map_name)

            infrastructure_components.append(anthropic_accessibility)

        # merge infrastructure component related maps in one list
        infrastructure_component += infrastructure_components

    # Recreational facilities, amenities, services

    recreation_component = []
    recreation_components = []

    if recreation:
        recreation_component.append(recreation)

    if osm_lines:
        if len(osm_lines) > 1:
            osm_lines = osm_lines.split(',')
            recreation_component += osm_lines
        else:
            print "Adding:", osm_lines
            recreation_components.append(osm_lines)

    if osm_points:
        if len(osm_points) > 1:
            osm_points = osm_points.split(',')
            recreation_components += osm_points
        else:
            recreation_components.append(osm_points)

    if blue_flags:
        recreation_components.append(blue_flags)

    # merge recreation component related maps in one list
    recreation_component += recreation_components

    """ Recreation Spectrum """

    if recreation_spectrum:

        recreation_opportunity_component = []

        # input
        zerofy_and_normalise_component(infrastructure_component,
                THRESHHOLD_ZERO, infrastructure_component_map_name)
        recreation_opportunity_component.append(infrastructure_component_map_name)
        remove_at_exit.append(infrastructure_component_map_name)

        # input
        zerofy_and_normalise_component(recreation_component,
                THRESHHOLD_0001, recreation_component_map_name)
        recreation_opportunity_component.append(recreation_component_map_name)
        remove_at_exit.append(recreation_component_map_name)

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
        tmp_recreation_potential_classes = tmp_map_name(tmp_recreation_potential)
        classify_recreation_component(tmp_recreation_potential,
                recreation_potential_classes,
                tmp_recreation_potential_classes)

        # recode opportunity_component
        tmp_recreation_opportunity_classes = tmp_map_name(recreation_opportunity)

        msg = "Reclassifying '{opportunity}' map"
        grass.debug(msg.format(opportunity=recreation_opportunity))
        del(msg)

        classify_recreation_component(
                component = recreation_opportunity,
                rules = recreation_opportunity_classes,
                output_name = tmp_recreation_opportunity_classes)

        if recreation_opportunity:

            msg = "Writing '{opportunity}' map"
            grass.verbose(msg.format(opportunity=recreation_opportunity))
            del(msg)

            g.copy(raster=(tmp_recreation_opportunity_classes,
                recreation_opportunity), quiet=True)

            update_meta(recreation_opportunity, opportunity_title)
            r.colors(map=recreation_opportunity, rules='-', stdin =
                    OPPORTUNITY_COLORS, quiet=True)

        # Recreation Spectrum: Potential + Opportunity [Output]
        compute_recreation_spectrum(
                potential = tmp_recreation_potential_classes,
                opportunity = tmp_recreation_opportunity_classes,
                spectrum = recreation_spectrum)

        msg = "Writing '{spectrum}' map"
        msg = msg.format(spectrum=recreation_spectrum)
        grass.verbose(_(msg))
        del(msg)

        update_meta(recreation_spectrum, spectrum_title)
        r.colors(map=recreation_spectrum, rules='-', stdin = SPECTRUM_COLORS,
                quiet=True)

    # restore region
    if landuse_extent:
        grass.del_temp_region()  # restoring previous region settings
        grass.verbose("Original Region restored")

    # print citation
    if info:
        citation = 'Citation: ' + citation_recreation_potential
        g.message(citation)

    if remove_at_exit:
        g.message("Removing temporary intermediate maps")
        g.remove(flags='f', type='raster', name=','.join(remove_at_exit),
                quiet=True)
        g.message("*** Please remove the grass_render_file ***")

if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    sys.exit(main())
