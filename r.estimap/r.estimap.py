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
#%  key: i
#%  description: Print out citation and other information
#%end

# Components section

#%option G_OPT_R_INPUTS
#% key: land
#% key_desc: names
#% label: Maps scoring access to land resources
#% description: Arbitrary number of maps scoring access to land resources
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: water
#% key_desc: filename
#% label: Maps scoring access to and quality of water resources
#% description: Arbitrary number of maps scoring access to and quality of water resources
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: natural
#% key_desc: filename
#% label: Maps scoring access to and quality of inland natural resources
#% description: Arbitrary number of maps scoring access to and quality of inland natural resources
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: urban
#% key_desc: map name
#% description: Maps scoring recreational value of urban components
#% required : no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: infrastructure
#% type: string
#% key_desc: name
#% label: Infrastructure to reach locations of recreation activities
#% description: Infrastructure to reach locations of recreation activities [required to derive recreation spectrum map]
#% required: no
#% guisection: Components
#%end

#%option G_OPT_R_INPUTS
#% key: recreation
#% type: string
#% key_desc: name
#% label: Recreational facilities, amenities and services
#% description: Recreational opportunities facilities, amenities and services [required to derive recreation spectrum map]
#% required: no
#% guisection: Components
#%end

# Land

#%option G_OPT_R_INPUT
#% key: suitability
#% type: string
#% key_desc: name
#% label: Land suitability for recreation
#% description: Suitability of land use classes to support recreation activities
#% required: no
#% guisection: Land
#%end

#%option G_OPT_R_INPUT
#% key: landuse
#% type: string
#% key_desc: name
#% label: Map to derive land suitability for recreation
#% description: Input to derive suitability of land use classes to support recreation activities. Requires scores, overrides suitability.
#% required : no
#% guisection: Land
#%end

#%option G_OPT_F_INPUT
#% key: suitability_scores
#% type: string
#% key_desc: name
#% label: Land suitability scores for recreation
#% description: Scores for suitability of land to support recreation activities. Expected are rules for `r.recode` that correspond to classes of the input land use map.
#% required: no
#% guisection: Land
#%end

#%rules
#% exclusive: suitability, landuse
#% exclusive: suitability, suitability_scores
#% requires: landuse, suitability_scores
#%end

# Water

#%option G_OPT_R_INPUT
#% key: lakes
#% key_desc: filename
#% label: Map scoring access to lakes
#% description: Lake proximity, scored based on a distance function
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: water_clarity
#% key_desc: map name
#% label: Map scoring water clarity
#% description: Water clarity. The higher, the greater the recreation value.
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: coast_proximity
#% key_desc: map name
#% label: Map scoring access to coast
#% description: Coast proximity, scored based on a distance function
#% required : no
#% guisection: Water
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
#% key: bathing_water
#% key_desc: filename
#% label: Map scoring bathing water quality
#% description: Bathing Water Quality Index. The higher, the greater is the recreational value.
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: marine
#% key_desc: map name
#% label: Map scoring access to marine natural provided areas
#% description: Access to marine natural protected areas
#% required : no
#% guisection: Water
#%end

#%rules
#%  excludes: water, coast_geomorphology, water_clarity, coast_proximity, marine, lakes, bathing_water
#%end

# Natural

#%option G_OPT_R_INPUT
#% key: protected
#% key_desc: filename
#% label: Protected areas
#% description: Natural Protected Areas
#% required : yes
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

# Urban

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

# Roads

#%option G_OPT_R_INPUT
#% key: roads
#% key_desc: map name
#% label: Primary road network
#% description: Primary road network
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

#%option G_OPT_R_INPUT
#% key: osm_lines
#% key_desc: map name
#% description: OpenStreetMap linear features
#% required : no
#% guisection: Recreation
#%end

#%option G_OPT_R_INPUT
#% key: osm_points
#% key_desc: map name
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

# Devaluation

#%option G_OPT_R_INPUTS
#% key: devaluation
#% key_desc: map name
#% label: Devaluing elements
#% description: Maps hindering accessibility to and degrading quality of various resources or infrastructure relating to recreation
#% required : no
#% guisection: Devaluation
#%end

# Output

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
    print "You must be in GRASS GIS to run this program."
    sys.exit(1)

# from scoring_schemes import corine

# globals

global equation, citation, spacy_plus
citation_recreation_potential='Zulian (2014)'
spacy_plus = ' + '
equation = "{result} = {expression}"  # basic equation for mapcalc

global threshhold_0001, threshhold_0003
threshhold_0001 = 0.0001
threshhold_0003 = 0.0003

recreation_potential_classification_rules='0.0:0.2:1\n0.2:0.4:2\n0.4:*:3'
recreation_opportunity_classification_rules=recreation_potential_classification_rules

color_recreation_potential = """ # Cubehelix color table generated using:
#   r.colors.cubehelix -dn ncolors=3 map=recreation_potential nrotations=0.33 gamma=1.5 hue=0.9 dark=0.3 output=recreation_potential.colors
0.000% 55:29:66
33.333% 55:29:66
33.333% 157:85:132
66.667% 157:85:132
66.667% 235:184:193
100.000% 235:184:193"""

color_recreation_opportunity = """# Cubehelix color table generated using:
#   r.colors.cubehelix -dn ncolors=3 map=recreation_potential nrotations=0.33 gamma=1.5 hue=0.9 dark=0.3 output=recreation_potential.colors
0.000% 55:29:66
33.333% 55:29:66
33.333% 157:85:132
66.667% 157:85:132
66.667% 235:184:193
100.000% 235:184:193"""

color_recreation_spectrum = """# Cubehelix color table generated using:
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

def cleanup():
    """
    Clean up temporary maps
    """
    grass.run_command('g.remove', flags='f', type="rast",
                      pattern='tmp.{pid}*'.format(pid=os.getpid()), quiet=True)

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

def run(cmd, **kwargs):
    """
    Pass required arguments to grass commands (?)
    """
    grass.run_command(cmd, quiet=True, **kwargs)

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

    # univar_string = grass.read_command('r.univar', flags='g', map=raster)
    # print "Univariate statistics:", univar_string

    minimum = grass.raster_info(raster)['min']
    # print "Minimum:", minimum

    maximum = grass.raster_info(raster)['max']
    # print "Maximum:", maximum

    if minimum is None or maximum is None:
        msg = "Minimum and maximum values of the <{raster}> map are 'None'. "
        msg += "Perhaps the MASK (<{mask}> map), opacifies all non-NULL cells of the <{raster}> map?."
        grass.fatal(_(msg.format(raster=raster, mask=mask)))

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

def normalise_component(components, output_name):
    """
    Sums up all maps listed in the given "components" object and derives a
    normalised output.
    """

    msg = "Normalising sum of: "
    msg += ', '.join(components)
    g.message(msg)

    components = [ name.split('@')[0] for name in components ]
    components_string = spacy_plus.join(components).replace(' ', '').replace('+', '_')
    tmp_sum = tmp_map_name(components_string)

    component_sum = spacy_plus.join(components)
    component_sum_equation = equation.format(result=tmp_sum,
            expression=component_sum)

    # if info:
    #     msg = "Equation:"
    #     msg += component_equation
    #     g.message(msg)

    grass.mapcalc(component_sum_equation, overwrite=True)
    # output_name = tmp_map_name(output_name)
    normalize_map(tmp_sum, output_name)

    del(components_string)
    del(tmp_sum)
    del(component_sum)
    del(component_sum_equation)
    del(output_name)

def zerofy_and_normalise_component(components, threshhold, output_name):
    """
    Sums up all maps listed in the given "components" object and derives a
    normalised output.
    """

    msg = "Normalising maps: "
    msg += ', '.join(components)
    g.message(msg)


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

        # if info:
        #     msg = "Equation:"
        #     msg += component_equation
        #     g.message(msg)

        grass.mapcalc(component_equation, overwrite=True)

        del(components_string)
        del(component_expression)
        del(component_equation)

    else:
        # temporary map names, if components contains one element
        tmp_intermediate = components[0]
        tmp_output = tmp_map_name(tmp_intermediate)

    #
    # The following is just an extra step as compared to the normalise_component()
    # function
    zerofy_small_values(tmp_intermediate, threshhold, tmp_output)
    # Is the duplication worth?
    #

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

def recreation_spectrum_expression(potential, opportunity):
    """
    Build and return a valid mapcalc expression for deriving
    the Recreation Opportunity Spectrum

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
    ' \ \n if( {potential} == 3 && {opportunity} == 3,'
    ' 9)))))))))')

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
        print msg
        # g.message(msg)
        del(msg)

    grass.mapcalc(spectrum_equation, overwrite=True)

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
    Main program: get names for input, output suffix, options and flags
    """

    # flags

    global info
    info = flags['i']
    landuse_extent = flags['e']

    # names for inputs from options

    # following some hard-coded names -- review and remove!

    land = options['land']
    land_component_map='land_component'

    water = options['water']
    water_component_map_name = tmp_map_name('water_component')

    natural = options['natural']
    natural_component_map_name = tmp_map_name('natural_component')

    urban = options['urban']
    urban_component_map='urban_component'

    infrastructure = options['infrastructure']
    infrastructure_component_map_name = tmp_map_name('infrastructure_component')

    recreation = options['recreation']
    # recreation_component='recreation'
    recreation_component_map_name = tmp_map_name('recreation_component')

    suitability = options['suitability']
    suitability_map_name = tmp_map_name('suitability')
    landuse = options['landuse']
    suitability_scores = options['suitability_scores']

    lakes = options['lakes']
    water_clarity = options['water_clarity']
    coast_proximity = options['coast_proximity']
    coast_geomorphology = options['coast_geomorphology']
    bathing_water = options['bathing_water']
    marine = options['marine']

    protected = options['protected']
    forest = options['forest']

    green_urban = options['green_urban']
    green_infrastructure = options['green_infrastructure']

    roads = options['roads']
    roads_secondary = options['roads_secondary']
    roads_local = options['roads_local']

    mask = options['mask']

    osm_lines = options['osm_lines']
    osm_points = options['osm_points']

    blue_flags = options['blue_flags']

    devaluation = options['devaluation']

    # names for outputs from options

    potential_title = "Recreation potential"
    recreation_potential = options['potential']  # intermediate / output
    recreation_potential_map_name = tmp_map_name('recreation_potential')

    opportunity_title = "Recreation opportunity"
    recreation_opportunity='recreation_opportunity'
    # recreation_opportunity_component_map='recreation_opportunity_map'

    spectrum_title = "Recreation spectrum"
    recreation_spectrum = options['spectrum']  # output
    # recreation_spectrum_component_map_name = tmp_map_name('recreation_spectrum_component_map')

    global timestamp
    timestamp = options['timestamp']
    remove_at_exit = []

    """ First, care about the computational region"""

    if mask:
        # global mask
        g.message("|! Masking out non-NULL cells of {mask}".format(mask=mask))
        r.mask(flags='i', raster=mask, overwrite=True)

    if landuse_extent:
        grass.use_temp_region()  # to safely modify the region
        g.region(flags='p', rast=mask) # Set region to 'mask'
        g.message("|! Computational resolution matched to {raster}".format(raster=landuse))

    """Land Component
            or Suitability of Land to Support Recreation Activities (SLSRA)"""

    land_component = []
    land_components = []

    if land:
        land_component = land

    if suitability:
        land_components.append(suitability)

    if not suitability and landuse and suitability_scores:
        suitability = suitability_map_name

        msg = "Deriving land suitability map from {landuse} based on {rules}"
        g.message(msg.format(landuse=landuse, rules=suitability_scores))

        r.recode(input = landuse,
                rules = suitability_scores,
                output = suitability)

        land_components.append(suitability)

    # merge land component related maps in one list
    land_component += land_components

    """Water Component"""

    water_component = []
    water_components = []

    if water:
        water_component = water.split(',')

        # Avoid going through the rest?
        # Should water_component  AND  water_components be exclusive!

    if lakes:
        lakes_proximity = lakes
        water_components.append(lakes_proximity)

    if water_clarity:
        water_components.append(water_clarity)

    if coast_geomorphology:
        water_components.append(coast_geomorphology)

    if coast_proximity:
        water_components.append(coast_proximity)

    if bathing_water:
        water_components.append(bathing_water)

    if marine:
        water_components.append(marine)

    # merge water component related maps in one list
    water_component += water_components

    """ Protected Areas  ( or Natural Component ? ) """

    natural_component = []
    natural_components = []

    if natural:
        natural_component = natural

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

    r.null(map=suitability, null=0)  # Set NULLs to 0
    recreation_potential_component.append(suitability)

    normalise_component(water_component, water_component_map_name)
    recreation_potential_component.append(water_component_map_name)
    remove_at_exit.append(water_component_map_name)

    normalise_component(natural_component, natural_component_map_name)
    recreation_potential_component.append(natural_component_map_name)
    remove_at_exit.append(natural_component_map_name)

    """ Recreation Potential [Output] """

    tmp_recreation_potential = tmp_map_name(recreation_potential_map_name)
    msg = "Computing an intermediate map <{potential}>"
    g.message(msg.format(potential=tmp_recreation_potential))
    normalise_component(recreation_potential_component,
            tmp_recreation_potential)

    if recreation_potential:

        msg = "Reclassifying <{potential}> map"
        g.message(msg.format(potential=tmp_recreation_potential))
        tmp_recreation_potential_classes = tmp_map_name(recreation_potential)
        classify_recreation_component(tmp_recreation_potential,
                recreation_potential_classification_rules,
                tmp_recreation_potential_classes)
        msg = "Writing <{potential}> map"
        g.message(msg.format(potential=tmp_recreation_potential_classes))
        g.rename(raster=(tmp_recreation_potential_classes,recreation_potential))
        update_meta(recreation_potential, potential_title)
        r.colors(map=recreation_potential, rules='-', stdin =
                color_recreation_potential)

        del(msg)
        del(tmp_recreation_potential_classes)

    # Infrastructure to access recreational facilities, amenities, services

    infrastructure_component = []
    infrastructure_components = []

    if infrastructure:
        infrastructure_component = infrastructure

    if roads:
        infrastructure_components.append(roads)

    if roads_secondary:
        infrastructure_components.append(roads_secondary)

    if roads_local:
        infrastructure_components.append(roads_local)

    # merge infrastructure component related maps in one list
    infrastructure_component += infrastructure_components

    # Recreational facilities, amenities, services

    recreation_component = []
    recreation_components = []

    if recreation:
        recreation_component.append(recreation)

    if osm_lines:
        recreation_components.append(osm_lines)

    if osm_points:
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
                threshhold_0001, infrastructure_component_map_name)
        recreation_opportunity_component.append(infrastructure_component_map_name)
        remove_at_exit.append(infrastructure_component_map_name)

        # input
        zerofy_and_normalise_component(recreation_component,
                threshhold_0001, recreation_component_map_name)
        recreation_opportunity_component.append(recreation_component_map_name)
        remove_at_exit.append(recreation_component_map_name)

        # intermediate
        # ----------------------------------------------------------------------
        # Why threshhold 0.0003? How and why it differs from 0.0001?
        zerofy_and_normalise_component(recreation_opportunity_component,
                threshhold_0003, recreation_opportunity)
        # ----------------------------------------------------------------------

        # recode recreation_potential
        tmp_recreation_potential_classes = tmp_map_name(tmp_recreation_potential)
        classify_recreation_component(tmp_recreation_potential,
                recreation_potential_classification_rules,
                tmp_recreation_potential_classes)

        # recode opportunity_component
        tmp_recreation_opportunity_classes = tmp_map_name(recreation_opportunity)

        msg = "Reclassifying <{opportunity}> map"
        g.message(msg.format(opportunity=recreation_opportunity))
        del(msg)

        classify_recreation_component(recreation_opportunity,
                recreation_opportunity_classification_rules,
                tmp_recreation_opportunity_classes)

        if recreation_opportunity:

            msg = "Writing <{opportunity}> map"
            g.message(msg.format(opportunity=tmp_recreation_opportunity_classes))
            g.copy(raster=(tmp_recreation_opportunity_classes,recreation_opportunity))

            update_meta(recreation_opportunity, opportunity_title)
            r.colors(map=recreation_opportunity, rules='-', stdin =
                    color_recreation_opportunity)

            del(msg)

        # Recreation Spectrum: Potential + Opportunity [Output]
        compute_recreation_spectrum(tmp_recreation_potential_classes,
                tmp_recreation_opportunity_classes, recreation_spectrum)

        msg = "Writing requested <{spectrum}> map"
        g.message(msg.format(spectrum=recreation_spectrum))

        update_meta(recreation_spectrum, spectrum_title)
        r.colors(map=recreation_spectrum, rules='-', stdin=color_recreation_spectrum)

    # restore region
    if landuse_extent:
        grass.del_temp_region()  # restoring previous region settings
        g.message("|! Original Region restored")

    # print citation
    if info:
        citation = '\nCitation: ' + citation_recreation_potential
        g.message(citation)

    if remove_at_exit:
        g.message("Removing intermediate maps")
        g.remove(flags='f', type='raster', name=','.join(remove_at_exit))

if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    sys.exit(main())
