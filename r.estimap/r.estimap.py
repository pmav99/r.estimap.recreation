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
#% key_desc: map names
#% label: Maps scoring access to and suitability of land resources for recreation
#% description: Arbitrary number of maps scoring access to and land resources suitability of land use classes to support recreation activities
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: water
#% key_desc: map names
#% label: Maps scoring access to and quality of water resources
#% description: Arbitrary number of maps scoring access to and quality of water resources
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: natural
#% key_desc: map names
#% label: Maps scoring access to and quality of inland natural resources
#% description: Arbitrary number of maps scoring access to and quality of inland natural resources
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: urban
#% key_desc: map names
#% description: Maps scoring recreational value of urban surfaces
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: infrastructure
#% type: string
#% key_desc: map names
#% label: Maps scoring infrastructure to reach locations of recreation activities
#% description: Infrastructure to reach locations of recreation activities [required to derive recreation spectrum map]
#% required: no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: recreation
#% type: string
#% key_desc: map names
#% label: Maps scoring recreational facilities, amenities and services
#% description: Recreational opportunities facilities, amenities and services [required to derive recreation spectrum map]
#% required: no
#% guisection: Components
#%end

'''Land'''

#%option G_OPT_R_INPUT
#% key: landuse
#% type: string
#% key_desc: map name
#% label: Land use map from which to derive suitability for recreation
#% description: Input to derive suitability of land use classes to support recreation activities. Requires scores, overrides suitability.
#% required : no
#% guisection: Land
#%end

#%option G_OPT_F_INPUT
#% key: suitability_scores
#% type: string
#% key_desc: map name
#% label: Recreational suitability scores for the classes of the 'landuse' map
#% description: Scores for suitability of land to support recreation activities. Expected are rules for `r.recode` that correspond to classes of the input land use map. If 'landuse' map given and 'suitability_scores' not provided, the module will use internal rules for the CORINE land classes
#% required: no
#% guisection: Land
#%end

'''Water'''

#%option G_OPT_R_INPUT
#% key: lakes
#% key_desc: map name
#% label: Lakes map for which to score accessibility
#% description: Lakes map to compute proximity for, score accessibility based on a distance function
#% required : no
#% guisection: Water
#%end

#%option
#% key: lakes_coefficients
#% key_desc: Coefficients
#% label: Distance function coefficients
#% description: Distance function coefficients to compute proximity: distance metric, constant, kappa, alpha and score. Refer to the manual for details.
#% multiple: yes
#% required: no
#% guisection: Water
#% answer: euclidean,1,30,0.008,1
#%end

#%option G_OPT_R_INPUT
#% key: marine
#% key_desc: map name
#% label: Map scoring access to marine natural provided areas
#% description: Access to marine natural protected areas
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: coastline
#% key_desc: map name
#% label: Sea coast map for which to compute proximity
#% label: Map scoring access to coast
#% description: Input map to compute coast proximity, scored based on a distance function
#% description: Coast proximity, scored based on a distance function
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
#% key_desc: map name
#% label: Map scoring recreation potential in coast
#% description: Coastal geomorphology, scored as suitable to support recreation activities
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: water_clarity
#% key_desc: map name
#% label: Water clarity
#% description: Water clarity. The higher, the greater the recreation value.
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: bathing_water
#% key_desc: filename
#% label: Map scoring bathing water quality
#% description: Bathing Water Quality Index. The higher, the greater is the recreational value.
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: riparian
#% key_desc: map name
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
#% key: forest
#% key_desc: filename
#% label: Forested areas
#% description: Access to forested areas
#% required : no
#% guisection: Natural
#%end

#%rules
#% exclusive: natural, protected
#% exclusive: protected, natural
##% requires: protected, protected_scores
#%end

'''Anthropic areas'''

#%option G_OPT_R_INPUT
#% key: anthropic
#% key_desc: map name
#% label: Map of artificial surfaces and agricultural areas
#% description: Partial input map to compute anthropic areas proximity, scored via a distance function
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: proximity_scores
#% key_desc: map name
#% label: Map scoring access to anthropic areas
#% description: Anthropic areas proximity, scored based on a distance function
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: green_urban
#% key_desc: map name
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
#% key_desc: map name
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
#% key: roads_proximity
#% key_desc: map name
#% label: Primary road network
#% description: Roads proximity, scored based on a distance function
#% required : no
#% guisection: Infrastructure
#%end

#%option G_OPT_R_INPUT
#% key: roads_secondary
#% key_desc: map name
#% label: Secondary road network
#% description: Secondary network including arterial and collector roads
#% required : no
#% guisection: Infrastructure
#%end

#%option G_OPT_R_INPUT
#% key: roads_local
#% key_desc: map name
#% label: Local road network
#% description: Local roads and streets
#% required : no
#% guisection: Infrastructure
#%end

'''Various'''

#%option G_OPT_R_INPUT
#% key: mask
#% key_desc: name
#% description: A raster map to apply as an inverted MASK
#% required : no
#%end


#######################################################################
# Offer input for potential?

# #%option G_OPT_R_OUTPUT
# #% key: recreation_potential
# #% key_desc: map name
# #% description: Recreation potential map
# #% required: no
# #% answer: recreation_potential
# #% guisection: Components
# #%end

#
#######################################################################

## Review the following item's "parsing rules"!

#%rules
#%  excludes: infrastructure, roads
#%end

#%option G_OPT_R_INPUTS
#% key: osm_lines
#% key_desc: map name
#% label: OpenStreetMap linear features
#% description: OpenStreetMap linear features
#% required : no
#% guisection: Recreation
#%end

#%option G_OPT_R_INPUTS
#% key: osm_points
#% key_desc: map name
#% label: OpenStreetMap point features
#% description: OpenStreetMap point features
#% required : no
#% guisection: Recreation
#%end

#%option G_OPT_R_INPUT
#% key: blue_flags
#% key_desc: map name
#% label: Moorings with blue flag distinction
#% description: Moorings with blue flag distinction
#% required : no
#% guisection: Recreation
#%end

'''Devaluation'''

#%option G_OPT_R_INPUTS
#% key: devaluation
#% key_desc: map name
#% label: Devaluing elements
#% description: Maps hindering accessibility to and degrading quality of various resources or infrastructure relating to recreation
#% required : no
#% guisection: Devaluation
#%end

'''Output'''

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

#%option G_OPT_R_OUTPUT
#% key: potential
#% key_desc: map name
#% label: Recreation potential map
#% description: Recreation potential map classified in 3 categories
#% required: no
#% guisection: Output
#%end

#%option G_OPT_R_OUTPUT
#% key: opportunity
#% key_desc: map name
#% label: Recreation opportunity map
#% description: Recreation opportunity map classified in 3 categories
#% required: no
#% guisection: Output
#%end

#%option G_OPT_R_OUTPUT
#% key: spectrum
#% key_desc: map name
#% label: Recreation spectrum map
#% description: Recreation spectrum map classified by default in 9 categories
#% required: no
#% guisection: Output
#%end

#%rules
#%  required: potential, spectrum
#%  requires: spectrum, infrastructure, roads, roads_secondary, roads_local
#%  requires: spectrum, recreation, osm_lines, osm_points, blue_flags
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
water_proximity_alpha=30
water_proximity_kappa=0.008
water_proximity_score=1

suitability_classification_classes=''
recreation_potential_classes='''0.0:0.2:1
0.2:0.4:2
0.4:*:3'''
anthropic_proximity_classes='0:500:1\n500.000001:1000:2\n1000.000001:5000:3\n5000.000001:10000:4\n10000.00001:*:5'
recreation_opportunity_classes=recreation_potential_classes

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
    """
    Pass required arguments to grass commands (?)
    """
    grass.run_command(cmd, quiet=True, **kwargs)

def save_map(mapname):
    """
    Helper function to save some in-between maps, assisting in debugging
    """
    # run('r.info', map=mapname, flags='r')
    # run('g.copy', raster=(mapname, 'DebuggingMap'))
    newname = 'output_' + mapname

    run('g.rename', raster=(mapname, newname))

    return newname

def cleanup():
    """
    Clean up temporary maps
    """
    run('g.remove', flags='f', type="rast",
            pattern='tmp.{pid}*'.format(pid=os.getpid()))

    if grass.find_file(name='MASK', element='cell')['file']:
        r.mask(flags='r', verbose=True)

def tmp_map_name(name):
    """
    Return a temporary map name, for example:

    tmp_map_name(potential) will return:

    tmp.SomeTemporaryString.potential
    """
    temporary_file = grass.tempfile()
    tmp = "tmp." + grass.basename(temporary_file)  # use its basename
    return tmp + '.' + str(name)

def compute_attractiveness(raster, metric, constant, alpha, kappa, score, **kwargs):
    """
    Source: http://publications.jrc.ec.europa.eu/repository/bitstream/JRC87585/lb-na-26474-en-n.pdf

    Compute a raster map whose values follow an (euclidean) distance function
    ( {constant} + {kappa} ) / ( {kappa} + exp({alpha} * {distance}) ), where:

    'constant' is: 1

    'kappa' is:

    'alpha' is:

    'distance' is: distances for the input raster map

    'score' is:

    Following, optional keyword arguments, might be the output_name of the
    computed proximity_name.
    """

    distance_terms = [str(raster),
                      str(metric),
                      'distance',
                      str(constant),
                      str(kappa),
                      str(alpha),
                      str(score)]
    tmp_distance = tmp_map_name('_'.join(distance_terms))

    grass.run_command('r.grow.distance',
                      input = raster,
                      distance = tmp_distance,
                      value = "cat",
                      metric = metric,
                      overwrite = True)

    # print "Inputs:", raster, metric, constant, kappa, alpha, score

    numerator = "{constant} + {kappa}"
    numerator = numerator.format(constant = constant, kappa = kappa)

    denominator = "{kappa} + exp({alpha} * {distance_map})"
    denominator = denominator.format(kappa = kappa,
                                     alpha = alpha,
                                     distance_map = tmp_distance)

    distance_function = " ( {numerator} / {denominator} ) * {score}"  # need for float()?
    distance_function = distance_function.format(numerator = numerator,
                                                 denominator = denominator,
                                                 score = score)
    if info:
        msg = "Distance function: {f}".format(f=distance_function)
        grass.message(_(msg))

    if 'output_name' in kwargs:
        tmp_output = tmp_map_name(kwargs.get('output_name'))  # temporary maps will be removed

    else:
        tmp_output = tmp_map_name('attractiveness_map')

    distance_function = equation.format(result=tmp_output,
            expression=distance_function)
    grass.mapcalc(distance_function, overwrite=True)

    r.null(map=tmp_output, null=0)  # Set NULLs to 0
    r.compress(tmp_output, flags='p')

    del(numerator)
    del(denominator)
    del(distance_function)

    # Maybe the user can request the output of this temporary map!
    if save_temporary_maps:
        tmp_output = save_map(tmp_output)

    return tmp_output

    del(tmp_output)

def zerofy_small_values(raster, threshhold, output_name):
    """
    Set the input raster map cell values to 0 if they are smaller than the
    given threshhold
    """
    rounding='if({raster} < {threshhold}, 0, {raster})'
    rounding = rounding.format(raster=raster, threshhold=threshhold)
    rounding_equation = equation.format(result=output_name, expression=rounding)
    grass.mapcalc(rounding_equation, overwrite=True)

def normalize_map (raster, output_name):
    """
    Normalize all raster map cells by subtracting the raster map's minimum and
    dividing by the range.
    """

    # print "Input:", raster
    # print "Output:", output_name

    univar_string = grass.read_command('r.univar', flags='g', map=raster)
    # print "Univariate statistics:", univar_string

    minimum = grass.raster_info(raster)['min']
    # print "Minimum:", minimum

    maximum = grass.raster_info(raster)['max']
    # print "Maximum:", maximum

    if minimum is None or maximum is None:
        msg = "Minimum and maximum values of the <{raster}> map are 'None'. "
        # msg += "Perhaps the MASK (<{mask}> map), opacifies all non-NULL cells of the <{raster}> map?."
        msg += "Perhaps the MASK opacifies all non-NULL cells of the <{raster}> map?."
        grass.fatal(_(msg.format(raster=raster)))

    normalisation = 'float(({raster} - {minimum}) / ({maximum} - {minimum}))'
    normalisation = normalisation.format(raster=raster, minimum=minimum,
            maximum=maximum)

    normalisation_equation = equation.format(result=output_name,
        expression=normalisation)
    grass.mapcalc(normalisation_equation, overwrite=True)

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
    """

    msg = "Normalising sum of: "
    msg += ', '.join(components)
    g.message(_(msg), flags='d')

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

        if info:
            msg = "Equation: "
            msg += component_equation
            g.message(_(msg), flags='v')

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
        g.message(msg.format(threshhold=threshhold, raster=tmp_intermediate),
                flags='v')
        zerofy_small_values(tmp_intermediate, threshhold, tmp_output)

    else:
        tmp_output = tmp_intermediate

    g.message(_("Temporary map name: {name}".format(name=tmp_output)), flags='v')
    g.message(_("Output map name: {name}".format(name=output_name)), flags='d')
    normalize_map(tmp_output, output_name)

    del(tmp_intermediate)
    del(tmp_output)
    del(output_name)

def classify_recreation_component(recreation_component, rules, output_name):
    """
    Recode an input recreation component based on given rules

    To Do:

    - Potentially, test range of input recreation component, i.e. ranging in
      [0,1]

    """

    r.recode(input=recreation_component, rules='-',
            stdin=rules, output=output_name)

def anthropic_accessibility_expression(anthropic_proximity, roads_proximity):
    """
    Build an r.mapcalc compatible expression to compute accessibility to
    anthropic surfaces.

    Input:

        - 'anthropic': Proximity to anthropic surfaces
        - 'roads': Proximity to roads
        - Accessibility classification rules for anthropic surfaces:

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

    Output:

        - Valid r.mapcalc expression

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
            ' \ \n if( {anthropic} => 4 && {roads} == 4, 5)))))))))')

    expression.format(anthropic=anthropic, roads=roads)
    return expression

def compute_anthropic_proximity(raster, proximity_rules, **kwargs):
    """
    """

    # compute distance to roads
    grass.run_command("r.grow.distance",
            input = anthropic,
            distance = anthropic_distances,
            metric = euclidean,
            overwrite = True)

    # compute proximity to roads
    grass.run_command("r.recode",
            input = anthropic_distances,
            output = anthropic_proximity,
            rules = proximity_rules,
            overwrite = True)

    if 'output_name' in kwargs:
        tmp_output = tmp_map_name(kwargs.get('output_name'))  # temporary maps will be removed

    else:
        tmp_output = tmp_map_name('anthropic_proximity')

    return anthropic_proximity

def compute_anthropic_accessibility(anthropic_proximity, roads_proximity, **kwargs):
    """
    Inputs: anthropic areas, roads
    Output: anthropic_proximity
    """

    accessibility_expression = anthropic_accessibility_expression( a_input, b_input)
    accessibility_expression = accessibility_expression.format(anthropic = anthropic,
            roads = roads)

    if 'output_name' in kwargs:
        tmp_output = tmp_map_name(kwargs.get('output_name'))  # temporary maps will be removed

    else:
        tmp_output = tmp_map_name('anthropic_accessibility')

    anthropic_areas_equation = equation.format(result=tmp_output,
            expression=anthropic_areas_expression)

    if info:
        msg = "Equation for proximity to anthropic areas: \n"
        msg += proximity_equation
        g.message(msg, flags='v')
        del(msg)

    grass.mapcalc(anthropic_areas_equation, overwrite=True)
    del(anthropic_areas_expression)
    del(anthropic_areas_equation)

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

    expression.format(potential=potential, opportunity=opportunity)
    return expression

def compute_recreation_spectrum(potential, opportunity, spectrum):
    """
    Computes recreation opportunity spectrum based on recreation potential and
    recreation opportunity maps.

    Input: Recreation potential, Recreation opportunity
    Output: Recreation spectrum
    """

    spectrum_expression = recreation_spectrum_expression(potential, opportunity)
    spectrum_expression = spectrum_expression.format(potential=potential,
            opportunity=opportunity)
    spectrum_equation = equation.format(result=spectrum,
            expression=spectrum_expression)

    if info:
        msg = "Recreation Spectrum equation: \n"
        msg += spectrum_equation
        g.message(msg)
        del(msg)

    grass.mapcalc(spectrum_equation, overwrite=True)

    del(spectrum_expression)
    del(spectrum_equation)

def update_meta(raster, title):
    """
    Update metadata of given raster map
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
        g.message(_(msg), flags='v')

    suitability_map_name = tmp_map_name('suitability')
    if landuse and not suitability_scores:
        msg = "Using internal rules to score land use classes in {map}"
        msg = msg.format(map=landuse)
        g.message(_(msg))
        suitability_scores = recreation_potential_classes

    '''Water components'''

    lakes = options['lakes']
    lakes_coefficients = options['lakes_coefficients']
    lakes_proximity_map_name='lakes_proximity'
    water_clarity = options['water_clarity']
    coastline = options['coastline']
    coast_proximity_map_name='coast_proximity'
    coast_geomorphology = options['coast_geomorphology']
    bathing_water = options['bathing_water']
    marine = options['marine']
    riparian = options['riparian']

    '''Natural components'''

    protected = options['protected']
    forest = options['forest']

    '''Anthropic areas'''

    anthropic = options['anthropic']

    green_urban = options['green_urban']
    green_infrastructure = options['green_infrastructure']

    roads = options['roads']
    roads_proximity = options['roads_proximity']
    roads_secondary = options['roads_secondary']
    roads_local = options['roads_local']

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
    # recreation_spectrum_component_map_name = tmp_map_name('recreation_spectrum_component_map')

    """ First, care about the computational region"""

    if mask:
        # global mask
        msg = "Masking non-NULL cells based on <{mask}>".format(mask=mask)
        g.message(_(msg), flags='v')
        r.mask(flags='i', raster=mask, overwrite=True, quiet=True)

    if landuse_extent:
        grass.use_temp_region()  # to safely modify the region
        g.region(flags='p', rast=mask) # Set region to 'mask'
        g.message("|! Computational resolution matched to {raster}".format(raster=landuse))

    """Land Component
            or Suitability of Land to Support Recreation Activities (SLSRA)"""

    land_component = []  # is a list, take care to use .extend() where required

    if land:
        land_component = land.split(',')

    if not land and landuse and suitability_scores:
        suitability = suitability_map_name

        msg = "Deriving land suitability map from '{landuse}' based on '{rules}'"
        g.message(msg.format(landuse=landuse, rules=suitability_scores))

        r.recode(input = landuse,
                rules = suitability_scores,
                output = suitability)

        land_component.append(suitability)

    # The 'land' and 'suitability' input maps are *now* programmaticaly exclusive
    # Below, an old approach merging land component related maps in one list.
    # Which, in turn, implies the option to use both the 'land' and 'landuse'
    # input options.
    # land_component += land_components

    '''Water Component'''

    water_component = []
    water_components = []

    if water:
        water_component = water.split(',')

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
            msg = "Distance function coefficients:\n"
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

                # what is the purpose of the 'output_name' if the
                # `compute_attractiveness()` function creates internally a
                # temporary map name, which will be removed at the end of the
                # script?

        water_components.append(lakes_proximity)

    if water_clarity:
        water_components.append(water_clarity)

    if coastline:
        coast_proximity = compute_attractiveness(
                raster = coastline,
                metric = euclidean,
                constant = water_proximity_constant,
                alpha = water_proximity_alpha,
                kappa = water_proximity_kappa,
                score = water_proximity_score,
                output_name = coast_proximity_map_name)

        water_components.append(coast_proximity)

    if coast_geomorphology:
        #
        # Process to compute geomorphology required here!
        # See Water2_1.py
        #
        water_components.append(coast_geomorphology)

    if bathing_water:
        water_components.append(bathing_water)

    if marine:
        water_components.append(marine)

    if riparian:
        water_components.append(riparian)

    # merge water component related maps in one list
    water_component += water_components

    '''Natural Component'''

    natural_component = []
    natural_components = []

    if natural:
        natural_component = natural.split(',')

    if protected:
        protected_areas = protected
        natural_components.append(protected_areas)

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
            g.message(_(msg), flags='d')
            del(msg)

            subset_land = equation.format(result = suitability_map,
                    expression = land_map)

            msg = "Expression for Suitability map: {expression}"
            msg = msg.format(expression = subset_land)
            g.message(_(msg), flags='d')
            del(msg)
            r.mapcalc(subset_land)

            g.message(_("Setting NULL cells to 0"), flags='d')
            r.null(map=suitability_map, null=0)  # Set NULLs to 0

            msg = "\nAdding land suitability map '{suitability}' to 'Recreation Potential' component\n"
            msg = msg.format(suitability = suitability_map)
            g.message(_(msg), flags='v')
            land_component.append(suitability_map)

    if len(land_component) > 1:
        g.message(_("\nNormalize 'Land' component\n"), flags='v')
        zerofy_and_normalise_component(land_component, THRESHHOLD_ZERO,
                land_component_map_name)
        recreation_potential_component.extend(land_component)
        remove_at_exit.extend(land_component)

    else:
        recreation_potential_component.extend(land_component)

    if water_component:
        g.message(_("\nNormalize 'Water' component\n"), flags='v')
        zerofy_and_normalise_component(water_component, THRESHHOLD_ZERO,
                water_component_map_name)
        recreation_potential_component.append(water_component_map_name)
        remove_at_exit.append(water_component_map_name)

    if natural_component:
        g.message(_("\nNormalize 'Natural' component\n"), flags='v')
        zerofy_and_normalise_component(natural_component, THRESHHOLD_ZERO,
                natural_component_map_name)
        recreation_potential_component.append(natural_component_map_name)
        remove_at_exit.append(natural_component_map_name)

    """ Recreation Potential [Output] """

    tmp_recreation_potential = tmp_map_name(recreation_potential_map_name)
    msg = "Computing an intermediate map <{potential}>"
    g.message(_(msg.format(potential=tmp_recreation_potential)), flags='v')

    g.message(_("\nNormalize 'Recreation Potential' component\n"), flags='v')
    g.message(_("Maps: {maps}".format(maps=recreation_potential_component)), flags='d')

    zerofy_and_normalise_component(recreation_potential_component,
            THRESHHOLD_ZERO, tmp_recreation_potential)

    if recreation_potential:

        msg = "\nReclassifying <{potential}> map"
        msg = msg.format(potential=tmp_recreation_potential)
        g.message(_(msg), flags='v')
        tmp_recreation_potential_classes = tmp_map_name(recreation_potential)
        classify_recreation_component(tmp_recreation_potential,
                recreation_potential_classes,
                tmp_recreation_potential_classes)

        msg = "\nWriting <{potential}> map\n"
        msg = msg.format(potential=recreation_potential)
        g.message(_(msg), flags='v')
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
        g.message(_("Infrastructure is only required to derive the recreation opportunity and, successively, the recreation spectrum"), flags='w')

    if any([recreation_opportunity, recreation_spectrum]):

        infrastructure_component = []
        infrastructure_components = []

        if infrastructure:
            infrastructure_component.append(infrastructure)

        '''Anthropic surfaces (includung Roads)'''

        if anthropic and roads:

            compute_anthropic_proximity(anthropic,
                    anthropic_proximity_classes,
                    output_name=anthropic_proximity)
            infrastructure_components.append(anthropic_proximity)

            compute_anthropic_proximity(roads,
                    anthropic_proximity_classes,
                    output_name=roads_proximity)
            infrastructure_components.append(roads_proximity)

            compute_anthropic_accessibility(anthropic_proximity, roads_proximity,
                    output_name=anthropic_accessibility)

            infrastructure_components.append(anthropic_accessibility)

        if roads_secondary:
            compute_anthropic_proximity(roads_secondary,
                    output_name=roads_secondary_proximity)
            infrastructure_components.append(roads_secondary_proximity)

        if roads_local:
            compute_anthropic_proximity(roads_local,
                    output_name=roads_local_proximity)
            infrastructure_components.append(roads_local_proximity)

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

        zerofy_and_normalise_component(recreation_opportunity_component,
                THRESHHOLD_0003, recreation_opportunity)
        # ----------------------------------------------------------------------

        # recode recreation_potential
        tmp_recreation_potential_classes = tmp_map_name(tmp_recreation_potential)
        classify_recreation_component(tmp_recreation_potential,
                recreation_potential_classes,
                tmp_recreation_potential_classes)

        # recode opportunity_component
        tmp_recreation_opportunity_classes = tmp_map_name(recreation_opportunity)

        msg = "Reclassifying <{opportunity}> map"
        g.message(msg.format(opportunity=recreation_opportunity), flags='v')
        del(msg)

        classify_recreation_component(recreation_opportunity,
                recreation_opportunity_classes,
                tmp_recreation_opportunity_classes)

        if recreation_opportunity:

            msg = "Writing requested <{opportunity}> map"
            g.message(msg.format(opportunity=recreation_opportunity), flags='v')
            del(msg)

            g.copy(raster=(tmp_recreation_opportunity_classes,recreation_opportunity),
                    quiet=True)

            update_meta(recreation_opportunity, opportunity_title)
            r.colors(map=recreation_opportunity, rules='-', stdin =
                    OPPORTUNITY_COLORS, quiet=True)

        # Recreation Spectrum: Potential + Opportunity [Output]
        compute_recreation_spectrum(tmp_recreation_potential_classes,
                tmp_recreation_opportunity_classes, recreation_spectrum)

        msg = "Writing requested <{spectrum}> map"
        msg = msg.format(spectrum=recreation_spectrum)
        g.message(_(msg), flags='v')
        del(msg)

        update_meta(recreation_spectrum, spectrum_title)
        r.colors(map=recreation_spectrum, rules='-', stdin = SPECTRUM_COLORS,
                quiet=True)

    # restore region
    if landuse_extent:
        grass.del_temp_region()  # restoring previous region settings
        g.message("Original Region restored")

    # print citation
    if info:
        citation = 'Citation: ' + citation_recreation_potential
        g.message(citation)

    if remove_at_exit:
        g.message("Removing temporary intermediate maps")
        g.remove(flags='f', type='raster', name=','.join(remove_at_exit),
                quiet=True)

if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    sys.exit(main())
