#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 MODULE:       r.estimap.recreation

 AUTHOR(S):    Nikos Alexandris <nik@nikosalexandris.net>

               Grazia Zulian <Grazia.Zulian@ec.europa.eu>
               First implementation in Python

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
#%  description:  Implementation of ESTIMAP to support mapping and modelling of ecosystem services (Zulian, 2014)
#%  keywords: estimap
#%  keywords: ecosystem services
#%  keywords: recreation potential
#%End

#%flag
#%  key: i
#%  description: Print out citation
#%end

#%flag
#%  key: f
#%  description: Filter input map before...
#%end

#%option G_OPT_R_INPUT
#% key: suitability
#% type: string
#% key_desc: name
#% description: Suitability of land use classes to support recreation activities
#% required: no
#% guisection: Land
#%end

#%option G_OPT_R_INPUT
#% key: landuse
#% type: string
#% key_desc: name
#% description: Land use as an input to derive suitability of land use classes to support recreation activities
#% required : no
#% guisection: Land
#%end

#%option G_OPT_F_INPUT
#% key: suitability_scores
#% type: string
#% key_desc: name
#% description: Scores, in form of recoding rules, for suitability of land use classes to support recreation activities. Should correspond to the given landuse classification map.
#% required: no
#% guisection: Land
#%end

#%rules
#% exclusive: suitability, landuse, suitability_scores
#% requires: landuse, suitability_scores
#%end

#%option G_OPT_R_INPUTS
#% key: land_component
#% key_desc: names
#% description: Maps scoring access to water resources
#% required : no
#% guisection: Land
#%end

#%option G_OPT_R_INPUT
#% key: lakes
#% key_desc: filename
#% description: Accessibility to lakes, scored based on a distance function
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: water_clarity
#% key_desc: map name
#% description: Water clarity. The higher, the greater the recreation value.
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: coast_proximity
#% key_desc: map name
#% description: Coastal proximity, scored based on a distance function
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: coast_geomorphology
#% key_desc: map name
#% description: Coastal geomorphology, scored as suitable to support recreation activities
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: bathing_water
#% key_desc: filename
#% description: Bathing Water Quality Index. The higher, the greater is the recreational value.
#% required : yes
#% guisection: Water
#%end

#%option G_OPT_R_INPUT
#% key: marine
#% key_desc: map name
#% description: Access to marine natural protected areas
#% required : no
#% guisection: Water
#%end

#%option G_OPT_R_INPUTS
#% key: water_component
#% key_desc: filename
#% description: Maps scoring access to and quality of water resources
#% required : no
#% guisection: Water
#%end

#%rules
#%  excludes: water_component, coast_geomorphology, water_clarity, coast_proximity, marine, lakes, bathing_water
#%end

#%option G_OPT_R_INPUT
#% key: protected
#% key_desc: filename
#% description: Natural Protected Areas
#% required : yes
#% guisection: Natural
#%end

#%option G_OPT_R_INPUT
#% key: forest
#% key_desc: filename
#% description: Access to forested areas.
#% required : yes
#% guisection: Natural
#%end

#%option G_OPT_R_INPUTS
#% key: natural_component
#% key_desc: filename
#% description: Maps scoring access to  and quality of inland natural resources
#% required : no
#% guisection: Natural
#%end

#%option G_OPT_R_INPUT
#% key: urban_green
#% key_desc: map name
#% description: Urban green areas
#% required : no
#% guisection: Urban
#%end

#%option G_OPT_R_INPUT
#% key: green_infrastructure
#% key_desc: filename
#% description: Maps scoring urban green infrastructure
#% required : no
#% guisection: Urban
#%end

#%option G_OPT_R_INPUT
#% key: roads
#% key_desc: map name
#% description: Road network
#% required : no
#% guisection: Urban
#%end

#%option G_OPT_R_INPUTS
#% key: urban_component
#% key_desc: map name
#% description: Maps scoring recreational value of urban components
#% required : no
#% guisection: Natural
#%end

#%option G_OPT_R_INPUTS
#% key: devaluation
#% key_desc: map name
#% description: Devaluing elements. Maps hindering accessibility to and degrading quality of various resources or infrastructure
#% required : no
#% guisection: Devaluation
#%end

#%option G_OPT_R_OUTPUT
#% key: potential
#% key_desc: map name
#% description: Recreation Potential Map
#% required: yes
#% answer: recreation_potential
#%end

# required librairies
import os
import sys
import subprocess
import datetime, time

import atexit
import grass.script as grass
from grass.exceptions import CalledModuleError
from grass.pygrass.modules.shortcuts import general as g

# from scoring_schemes import corine

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

# def add_timestamp(mtl_filename, outname):
#     """
#     Retrieve metadata from MTL file.
#     """
#     import datetime
#     metadata = Landsat8_MTL(mtl_filename)

#     # required format is: day=integer month=string year=integer time=hh:mm:ss.dd
#     acquisition_date = str(metadata.date_acquired)  ### FixMe ###
#     acquisition_date = datetime.datetime.strptime(acquisition_date, '%Y-%m-%d').strftime('%d %b %Y')
#     acquisition_time = str(metadata.scene_center_time)[0:8]
#     date_time_string = acquisition_date + ' ' + acquisition_time

#     #msg = "Date and time of acquisition: " + date_time_string
#     #grass.verbose(msg)

#     run('r.timestamp', map=outname, date=date_time_string)

#     del(date_time_string)

def set_null_to_zero(input_raster, output_raster):
    """
    """
    zero = 0
    zero_expression = 'float(if(isnull({input_raster}), {zero}, {input_raster}))'
    zero_expression = zero_expression.format(input_raster=suitability, zero=zero)
    zero_equation = equation.format(result=suitability, expression=zero_expression)
    grass.mapcalc(zero_equation, overwrite=True)
    del(zero_equation)
    del(zero_expression)

def normalize_map (raster, output_name):
    """
    Normalize a raster map

    #
    # deletes the input raster map
    #

    ### Why delete a map here?
    """
    minimum = grass.raster_info(raster)['min']
    maximum = grass.raster_info(raster)['max']

    expression = 'float(({raster} - ${minimum}) / ({maximum} - {minimum}))'
    expression = expression.format(input_map=raster, minimum=minimum, maximum=maximum)
    normalisation_equation = equation.format(result=output_map,
        expression=normalisation_expression)
    grass.mapcalc(normalisation_equation, overwrite=True)

    del(minimum)
    del(maximum)
    del(expression)
    del(normalisation_equation)

    # # grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)
    # run('g.remove', flags='f', type='raster', name=raster, quiet=True)

def tmp_map_name(name):
    """
    Return a temporary map name, for example:

    tmp_avg_lse = tmp + '.avg_lse'
    """
    temporary_file = grass.tempfile()
    tmp = "tmp." + grass.basename(temporary_file)  # use its basename
    return tmp + '.' + str(name)

def normalise_component(components, output_name):
    """
    Sums up all maps listed in the components object and derives a normalised output.
    """

    components_string = spacy_plus.join(components).replace(' ', '').replace('+', '_')
    tmp_output = tmp_map_name(components_string)

    component_expression = spacy_plus.join(components)
    component_equation = equation.format(result=tmp_output, expression=component_expression)
    grass.mapcalc(component_equation, overwrite=True)
    normalize(tmp_output, output_name)

    del(components_string)
    del(tmp_output)
    del(component_expression)
    del(component_equation)
    del(output_name)

def main():
    """
    Main program: get names for input, output suffix, options and flags
    """

    # basic equation for mapcalc
    global equation, citation
    spacy_plus = ' + '
    equation = "{result} = {expression}"
    recreation_potential_components = []

    # Land Component
    #  or Suitability of Land to Support Recreation Activities (SLSRA)

    if options['land_component']:
        land_component = options['land_component']

    else:
        land_components = []

        if options['landuse'] and options['suitability_scores']:

            landuse = options['landuse']
            suitability_scores = options['suitability_scores']
            suitability = 'suitability'
            run('r.recode', input = landcover, rules = suitability_scores, output = suitability)

        if not options['landuse'] and not options['suitability_scores']:

            if options['suitability']:
                suitability = options['suitability']

            else:
                suitability = 'suitability'

        land_components.append(suitability)

        # # provided land components in one string
        # land_component = spacy_plus.join(land_components)

    # Water Component

    if options['water_component']:
        water_component = options['water_component']

    else:
        water_components = []

        if options['lakes']:
            lakes = options['lakes']
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

        # # provided water components in one string
        # water_component = spacy_plus.join(water_components)

    # Protected Areas  ( or Natural Component ? )

    if options['natural_component']:
        natural_component = options['natural_component']

    else:
        natural_components = []

        if options['protected']:
            protected_areas = options['protected']
            natural_components.append(protected_areas)

        if options['forest']:
            forest = options['forest']
            natural_components.append(forest)

        # # provided natural components in one string
        # natural_component = spacy_plus.join(natural_components)

    # Output

    if not options['potential']:
        recreation_potential = "recreation_potential"
    else:
        recreation_potential = options['potential']

    # Mask out lakes
    if lakes:
        r.mask(raster=lakes, overwrite=True)

    #
    # set computational region  # ?  To smallest in extent among given maps?
    #

    grass.use_temp_region()  # to safely modify the region
    run('g.region', flags='p', rast=mask) # Set region to 'mask'
    g.message("|! Computational resolution matched to mask's ({p})".format(p=mask))

    # Normalize inputs and add them as recreation potential components

    ## Land Use Component
    # Set NULLs to 0 -- why not: run('r.null', map=suitability, null=0)
    set_null_to_zero(suitability, suitability_null_to_zero)
    recreation_potential_components.append(suitability)

    ## Water Component
    normalise_component(water_component, water_component_normalised)
    recreation_potential_components.append(water_component_normalised)

    ## Natural Components
    normalise_component(natural_component, natural_component_normalised)
    recreation_potential_components.append(natural_component_normalised)

    # Recreation Potential
    normalise_component(recreation_potential_components,
            recreation_potential_components_normalised)


    # Time Stamping ?

    # Apply Color Table(s) ?

    # ToDo: helper function for r.support

    # strings for metadata
    history_recreation_potential = '\n' + citation_recreation_potential
    description_recreation_potential = ('Recreation Potential Map derived from ... . ')

    title_recreation_potential = 'Recreation Potential'
    # units_recreation_potential = ''

    source1_recreation_potential = 'Source 1'
    source2_recreation_potential = 'Source 2'

    # history entry
    run("r.support", map=recreation_potential_output, title=title_recreation_potential,
        units=units_recreation_potential, description=description_recreation_potential,
        source1=source1_recreation_potential, source2=source2_recreation_potential,
        history=history_recreation_potential)

    # # restore region
    # if scene_extent:
    #     grass.del_temp_region()  # restoring previous region settings
    #     g.message("|! Original Region restored")

    # print citation
    if info:
        print '\nCitatin: ' + citation_recreation_potential

if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    sys.exit(main())
