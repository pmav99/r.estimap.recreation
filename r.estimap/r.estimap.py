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

#%option G_OPT_R_INPUTS
#% key: land_component
#% key_desc: names
#% label: Maps scoring access to land resources
#% description: Arbitrary number of maps scoring access to land resources
#% required : no
#% guisection: Components
#%end

# Land

#%option G_OPT_R_INPUT
#% key: suitability
#% type: string
#% key_desc: name
#% label: Suitability of land to support recreation
#% description: Suitability of land use classes to support recreation activities
#% required: no
#% guisection: Land
#%end

#%option G_OPT_R_INPUT
#% key: landuse
#% type: string
#% key_desc: name
#% label: Map to derive suitability of land to support recreation
#% description: Input to derive suitability of land use classes to support recreation activities
#% required : no
#% guisection: Land
#%end

#%option G_OPT_F_INPUT
#% key: suitability_scores
#% type: string
#% key_desc: name
#% label: Scores for suitability of land to support recreation
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

#%option G_OPT_R_INPUTS
#% key: water_component
#% key_desc: filename
#% label: Maps scoring access to and quality of water resources
#% description: Arbitrary number of maps scoring access to and quality of water resources
#% required : no
#% guisection: Components
#%end

#%rules
#%  excludes: water_component, coast_geomorphology, water_clarity, coast_proximity, marine, lakes, bathing_water
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

#%option G_OPT_R_INPUTS
#% key: natural_component
#% key_desc: filename
#% label: Maps scoring access to and quality of inland natural resources
#% description: Arbitrary number of maps scoring access to and quality of inland natural resources
#% required : no
#% guisection: Components
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
#% guisection: Urban Green
#%end

#%option G_OPT_R_INPUTS
#% key: urban_component
#% key_desc: map name
#% description: Maps scoring recreational value of urban components
#% required : no
#% guisection: Components
#%end

# Roads

#%option G_OPT_R_INPUT
#% key: roads
#% key_desc: map name
#% label: Primary road network
#% description: Primary road network
#% required : no
#% guisection: Roads
#%end

#%option G_OPT_R_INPUT
#% key: roads_secondary
#% key_desc: map name
#% label: Secondary road network
#% description: Secondary network including arterial and collector roads
#% required : no
#% guisection: Roads
#%end

#%option G_OPT_R_INPUT
#% key: roads_local
#% key_desc: map name
#% label: Local road network
#% description: Local roads and streets
#% required : no
#% guisection: Roads
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

#%option G_OPT_R_INPUTS
#% key: facility_component
#% type: string
#% key_desc: name
#% description: Infrastructure to reach locations of recreation activities
#% required: no
#% guisection: Components
#%end

## Review the following item's "parsing rules"!

#%rules
#%  excludes: facility_component, roads
#%end

#%option G_OPT_R_INPUTS
#% key: recreation_component
#% type: string
#% key_desc: name
#% description: Recreational facilities and amenities
#% required: no
#% guisection: Components
#%end

#%option G_OPT_R_INPUT
#% key: osmlines
#% key_desc: map name
#% description: OpenStreetMap linear features
#% required : no
#% guisection: OpenStreetMap
#%end

#%option G_OPT_R_INPUT
#% key: osmpoints
#% key_desc: map name
#% description: OpenStreetMap point features
#% required : no
#% guisection: OpenStreetMap
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
#% description: Recreation potential map
#% required: no
#% guisection: Output
#%end

#%option G_OPT_R_OUTPUT
#% key: opportunity_component
#% key_desc: map name
#% description: Recreation opportunity spectrum map
#% required: no
#% guisection: Output
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
citation_recreation_potential='Zulian (2014)'

# helper functions
def cleanup():
    """
    Clean up temporary maps
    """
    grass.run_command('g.remove', flags='f', type="rast",
                      pattern='tmp.{pid}*'.format(pid=os.getpid()), quiet=True)

    if grass.find_file(name='MASK', element='cell')['file']:
        r.mask(flags='r', verbose=True)

def run(cmd, **kwargs):
    """
    Pass required arguments to grass commands (?)
    """
    grass.run_command(cmd, quiet=True, **kwargs)

def tmp_map_name(name):
    """
    Return a temporary map name

    Example:
    tmp_output = tmp + '.output'
    """
    temporary_file = grass.tempfile()
    tmp = "tmp." + grass.basename(temporary_file)  # use its basename
    return tmp + '.' + str(name)

def zero_small_values(raster, output_name):
    """
    Set the input raster map cell values to 0 if they are smaller than 0.0001
    """
    threshhold = 0.0001
    rounding='if({raster} < {threshhold}, 0, {raster})'
    rounding = rounding.format(raster=raster, threshhold=threshhold)
    rounding_equation = equation.format(result=output_name, expression=rounding)
    grass.mapcalc(rounding_equation, overwrite=True)
    
    # Unless the input raster map has to be retained as is, the following is
    # not required and the result can overwrite the input raster map itself.
    #
    # run('g.remove', flags='f', type='raster', name=raster, quiet=True)
    #

def normalize_map (raster, output_name):
    """
    Normalize a raster map
    """
    minimum = grass.raster_info(raster)['min']
    maximum = grass.raster_info(raster)['max']

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

    # Why delete a map here?
    # Unless the input raster map has to be retained as is, the following is
    # not required and the result can overwrite the input raster map itself.
    #
    # run('g.remove', flags='f', type='raster', name=raster, quiet=True)
    #

def normalise_component(components, output_name):
    """
    Sums up all maps listed in the given "components" object and derives a
    normalised output.
    """

    msg = "Normalising maps: "
    msg += ', '.join(components)
    g.message(msg)

    components = [ name.split('@')[0] for name in components ]
    components_string = spacy_plus.join(components).replace(' ', '').replace('+', '_')
    tmp_output = tmp_map_name(components_string)

    component_expression = spacy_plus.join(components)
    component_equation = equation.format(result=tmp_output, expression=component_expression)

    # if info:
    #     msg = "Equation:"
    #     msg += component_equation
    #     g.message(msg)

    grass.mapcalc(component_equation, overwrite=True)
    normalize_map(tmp_output, output_name)

    del(components_string)
    del(tmp_output)
    del(component_expression)
    del(component_equation)
    del(output_name)

def update_meta(raster):
    """
    """
    # strings for metadata
    history_recreation_potential = '\n' + citation_recreation_potential
    description_recreation_potential = ('Recreation Potential Map')

    title_recreation_potential = 'Recreation Potential'
    units_recreation_potential = 'Meters'

    source1_recreation_potential = 'Source 1'
    source2_recreation_potential = 'Source 2'

    # history entry
    run('r.support', map=raster, title=title_recreation_potential,
        units=units_recreation_potential, description=description_recreation_potential,
        source1=source1_recreation_potential, source2=source2_recreation_potential,
        history=history_recreation_potential)

    if options['timestamp']:
        timestamp = options['timestamp']
        run('r.timestamp', map=raster, date=timestamp)

    del(history_recreation_potential)
    del(description_recreation_potential)
    del(title_recreation_potential)
    del(units_recreation_potential)
    del(source1_recreation_potential)
    del(source2_recreation_potential)

def main():
    """
    Main program: get names for input, output suffix, options and flags
    """

    # basic equation for mapcalc
    global equation, citation, spacy_plus
    spacy_plus = ' + '
    equation = "{result} = {expression}"

    # flags
    global info
    info = flags['i']

    # names for normalised component maps
    land_component_map_name='land_component'
    water_component_map='water_component'
    natural_component_map='natural_component'
    # recreation_potential_component_map='recreation_potential'
    normalised_suffix='normalised'

    #
    # names for maps related to recreation opportunity
    #
    facility_component='facility_component'
    recreation_component='recreation_component'
    osm_lines='osm_lines'
    osm_points='osm_points'
    opportunity_component='opportunity_component'

# ------------------------------------------------------------------------------
    landuse_extent = flags['e']
# ------------------------------------------------------------------------------

    recreation_potential_component = []

    # Land Component
    #  or Suitability of Land to Support Recreation Activities (SLSRA)

    if options['land_component']:
        land_component = options['land_component']

    else:
        land_components = []

        if options['landuse'] and options['suitability_scores']:

            # landuse = options['landuse']
            # suitability_scores = options['suitability_scores']
            # suitability = 'suitability'
            # run('r.recode',
            #         input = landuse,
            #         rules = suitability_scores,
            #         output = suitability)
            r.recode(input = landuse,
                    rules = suitability_scores,
                    output = suitability)

        if not options['landuse'] and not options['suitability_scores']:

            if options['suitability']:
                suitability = options['suitability']

            else:
                suitability = 'suitability'

        land_components.append(suitability)

        # # provided land components in one string
        # land_component = spacy_plus.join(land_components)

    # Water Component

    # one list to hold arbitrary water component related maps
    water_component = []

    if options['water_component']:
        water_component = options['water_component'].split(',')

        # How to avoid going through the rest... if?

          # Should water_component  AND water_components be exclusive!

    # one list for explicitly defined water component related maps
    water_components = []

    if options['lakes']:
        lakes_proximity = options['lakes']
        water_components.append(lakes_proximity)

    if options['water_clarity']:
        water_clarity = options['water_clarity']
        water_components.append(water_clarity)

    if options['coast_geomorphology']:
        coast_geomorphology = options['coast_geomorphology']
        water_components.append(coast_geomorphology)

    if options['coast_proximity']:
        coast_proximity = options['coast_proximity']
        water_components.append(coast_proximity)

    if options['bathing_water']:
        bathing_water = options['bathing_water']
        water_components.append(bathing_water)

    if options['marine']:
        marine = options['marine']
        water_components.append(marine)

    # merge water component related maps in one list
    water_component += water_components

    # Protected Areas  ( or Natural Component ? )

    natural_component = []
    natural_components = []

    if options['natural_component']:
        natural_component = options['natural_component']

    else:
        natural_components = []  # Is this necessary?

        if options['protected']:
            protected_areas = options['protected']
            natural_components.append(protected_areas)

        if options['forest']:
            forest = options['forest']
            natural_components.append(forest)

    natural_component += natural_components

    # Output

    if not options['potential']:
        recreation_potential = "recreation_potential"
    else:
        recreation_potential = options['potential']

    if not options['opportunity']:
        recreation_opportunity = "recreation_opportunity"
    else:
        recreation_opportunity = options['opportunity']

    if options['mask']:
        mask = options['mask']
        r.mask(raster=mask, overwrite=True)

    if landuse_extent:
        grass.use_temp_region()  # to safely modify the region
        # run('g.region', flags='p', rast=mask) # Set region to 'mask'
        g.region(flags='p', rast=mask) # Set region to 'mask'
        g.message("|! Computational resolution matched to {raster}".format(raster=landuse))

    # Normalize inputs and add them as recreation potential components

    ## Land Use Component
    # run('r.null', map=suitability, null=0)  # Set NULLs to 0
    r.null( map=suitability, null=0)  # Set NULLs to 0
    recreation_potential_component.append(suitability)

    ## Water Component
    normalise_component(water_component, water_component_map)
    recreation_potential_component.append(water_component_map)

    ## Natural Components
    normalise_component(natural_component, natural_component_map)
    recreation_potential_component.append(natural_component_map)

    # Recreation Potential
    normalise_component(recreation_potential_component,
            recreation_potential)

    # Recreation Opportunity Spectrum
    if options['recreation_opportunity']:
        recreation_opportunity=options['recreation_opportunity']

        # input

            # round values of
                # - features_to_reach
                # - features_to_enjoy

            # normalise values of
                # - features_to_reach
                # - features_to_enjoy

        # inter

            # Add normalised raster maps

            # Sums up

            # Set Input Raster Cells to NULL if they are < 0.0003
                # Why this threshhold?

            # Normalise sum of all raster maps

            # Recode
                # recreation_potential
                    # rules?
                # opportunity_component
                    # rules?

        # output

            # Recreation Opportunity Spectrum
                # Combination of Potential and Opportunity
                # Why `r.mapcalc` instead of (now fixed) `r.cross`?



    # Time Stamping ?

    # Apply Color Table(s) ?

    update_meta(recreation_potential)

    # restore region
    if landuse_extent:
        grass.del_temp_region()  # restoring previous region settings
        g.message("|! Original Region restored")

    # print citation
    if info:
        citation = '\nCitation: ' + citation_recreation_potential
        g.message(citation)

if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    sys.exit(main())
