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
#%  keywords: recreation
#%End

#%option G_OPT_R_INPUT
#% key: landcover
#% key_desc: map name
#% description: Land cover map
#% required : no
#%end

#%option G_OPT_R_INPUT
#% key: landuse
#% key_desc: map name
#% description: Land use map
#% required : no
#%end

#%option G_OPT_F_INPUT
#% key: suitability
#% key_desc: map name
#% description: Suitability of land to support recreation activities
#% required: no
#%end

#%rules
#% exclusive: landcover, suitability
#%end

#%option G_OPT_R_INPUT
#% key: coast_geomorphology
#% key_desc: map name
#% description: Score of coastal geomorphology to support recreation activities
#% required : no
#%end

#%option G_OPT_R_INPUT
#% key: water_clarity
#% key_desc: map name
#% description: Water clarity
#% required : no
#%end

#%option G_OPT_R_INPUT
#% key: coast_proximity
#% key_desc: map name
#% description: Score of proximity to coast based on a distance function
#% required : no
#%end

#%option G_OPT_R_INPUT
#% key: marine
#% key_desc: map name
#% description: Marine protected natural areas
#% required : no
#%end

#%option G_OPT_R_INPUT
#% key: lakes
#% key_desc: filename
#% description: Score of access to lakes based on a distance function
#% required : no
#%end

#%option G_OPT_R_INPUT
#% key: bathing_water
#% key_desc: filename
#% description: Bathing Water Quality Index
#% required : yes
#%end

#%option G_OPT_R_INPUT
#% key: water_component
#% key_desc: filename
#% description: Maps scoring access to water resources
#% required : no
#%end

#%rules
#%  excludes: water_component, coast_geomorphology, water_clarity, coast_proximity, marine, lakes, bathing_water
#%end

#%option G_OPT_R_INPUT
#% key: natural
#% key_desc: filename
#% description: Natural Protected Areas
#% required : yes
#%end

#%option G_OPT_R_INPUT
#% key: forest
#% key_desc: filename
#% description: High Resolution Forest
#% required : yes
#%end

#%option G_OPT_R_INPUT
#% key: natural_component
#% key_desc: filename
#% description: Maps scoring access to inland natural resources
#% required : no
#%end

#%option G_OPT_R_INPUT
#% key: urban_green
#% key_desc: map name
#% description: Urban green areas
#% required : no
#%end

#%option G_OPT_R_INPUT
#% key: green_infrastructure
#% key_desc: filename
#% description: Maps scoring urban green infrastructure
#% required : no
#%end

#%option G_OPT_R_INPUT
#% key: roads
#% key_desc: map name
#% description: Roads
#% required : no
#%end

#%option G_OPT_R_INPUT
#% key: negative_elements
#% key_desc: map name
#% description: Roads
#% required : no
#%end

#%option G_OPT_F_INPUT
#% key: suitability_scores
#% key_desc: filename
#% description: Scores of suitability to support recreation activities in form of reccoding rules for the CORINE land cover classification
#% required: no
#%end

######################
# #%rules
# #% requires: landuse, suitability_scores
# #%end
#######################

#%option G_OPT_R_OUTPUT
#% key: potential
#% key_desc: map name
#% description: Recreation Potential Map
#% required: no
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

def add_timestamp(mtl_filename, outname):
    """
    Retrieve metadata from MTL file.
    """
    import datetime
    metadata = Landsat8_MTL(mtl_filename)

    # required format is: day=integer month=string year=integer time=hh:mm:ss.dd
    acquisition_date = str(metadata.date_acquired)  ### FixMe ###
    acquisition_date = datetime.datetime.strptime(acquisition_date, '%Y-%m-%d').strftime('%d %b %Y')
    acquisition_time = str(metadata.scene_center_time)[0:8]
    date_time_string = acquisition_date + ' ' + acquisition_time

    #msg = "Date and time of acquisition: " + date_time_string
    #grass.verbose(msg)

    run('r.timestamp', map=outname, date=date_time_string)

    del(date_time_string)


def normalize (raster, output_name):
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

    # # grass.run_command('g.remove', flags='f', type='raster', name=inras, quiet=True)
    # run('g.remove', flags='f', type='raster', name=raster, quiet=True)

def main():
    """
    Main program: get names for input, output suffix, options and flags
    """

    # basic equation for mapcalc
    global equation, citation
    equation = "{result} = {expression}"
    recreation_potential_components = []

    # ?

    slsra_rules = options['image'].split(',')


    # 1

    mask = "mask" #'lakes3' #"
    #mask = 'testmask'

    # 2

    listfinalNATURE =[]
    deleterlist=[]
    deletevlist=[]

    # 3

    landcover = options['landcover']
    # computationlist=['clc2012']

    # 4 -- DONE --

    # --------------------------------------------------------------------------
    grass.use_temp_region()  # to safely modify the region
    run('g.region', flags='p', rast=mask) # Set region to 'mask'
    g.message("|! Region's resolution matched to mask's ({p})".format(p=mask))
    # --------------------------------------------------------------------------

    # 5 # Suitability of Land to support recreation activities

    # Reclass rules for corine land cover
    # SLSRA_rules = "/natcapes_nfs/grassdb/INCA_R/scores/recodeCLC.txt"
    suitability_scores = options['suitability_scores']

    # 6

    # for raster in computationlist:  # Not required since the list contains
    # only one map!

    # # Fix Me
    # year = raster[-4:]  # This was extracting the year from the name of
    # the corine map.  Not required.
    #

    # ?
    # SLSRA = 'SLSRA_'+year

    if not suitability:
        suitability = 'suitability'
        suitability_scores = options['suitability_scores']

    #recode CLC
    # grass.run_command("r.recode", input= r, output= SLSRA, rules = SLSRA_rules, overwrite=True)
    
    # r has been replaced here with the 'landcover'
    # SLSRA: recreation_suitability

        run('r.recode',
                input = landcover,
                rules = suitability_scores,
                output = suitability)

    # Set NULLs to 0

    # setnull_0('SLSRA_'+year, 'SLSRA0_'+year)  # Why not use r.null?

    zero_expression = 'float(if(isnull({input_raster}), {zero}, {input_raster}))'
    zero_expression = zero_expression.format(input_raster=suitability, zero=zero)
    zero_equation = equation.format(result=suitability, expression=zero_expression)
    grass.mapcalc(zero_equation, overwrite=True)

    # masklak('SLSRA0_'+year,'SLSRA1_'+year,mask)

    # 7 # mask RA with recode industry

    # for r in computationlist:  # Not required, since list consists of one
    # map.


    # Fix Me
    # year = r[-4:]  # Not required.
    # print year

    ## Water Component
    water_components = []

    # WaterL.append('F_statagperc1') add bathing water here

    # WaterL.append('bathing_water_quality_2006_gscores')
    ### Score access to bathing waters as a distance function
    if options['bathing_water']:
        bathing_water = options['bathing_water']
        water_component.append(bathing_water)

    # WaterL.append('fd_coastD')
    ### Coast:  Score access to the coast as a distance function
    if options['coast_proximity']:
        coast_proximity = options['coast_proximity']
        water_components.append(coast_proximity)

    # WaterL.append('Lake_D')
    ### Lakes:  Score access to lakes as a distance function
    if options['lakes']:
        lakes_proximity = options['lakes']
        water_components.append(lakes_proximity)

    # WaterL.append('geo_coast')
    ### Coast Geomorphology: Score coastal areas as a function of their geomorphology
    if options['coast_geomorphology']:
        coast_geomorphology = options['coast_geomorphology']
        water_components.append(coast_geomorphology)

    # laststring = " + ".join(WaterL)
    water_component = ' + '.join(water_components)

    water_component_expression = 'water_component * lakes3'

    water_component_equation =  water_component_expression.format(result=water_component,
            expression=water_component_expression)

    grass.mapcalc(water_component_equation, overwrite=True)

    #

    # normalize ('Wat'+year,'Wat_N'+year)
    normalize(water_component, water_component_normalised)

    # 8 # final inputs for Recreation Potential

    # for r in computationlist:  # Not required

    # Fix Me
    year = r[-4:]

    # if year == '2012':  # Not required

    ## Land Use Component

    finalRP.append('SLSRA0_'+year) #land use
    finalRP.append('Wat_N'+year)  #Fresh Water

    ## Natural Protected Areas

    if options['natural']:
        natural_protected_areas = options['natural']
        recreation_potential_components.append(natural)

    # laststring = " + ".join(finalRP)
    # RP = 'RP00V3'+year+' = ('+ laststring+')'
    recreation_potential_expression = ' + '.join(recreation_potential_components)

    if not options['potential']:
        recreation_potential = "recreation_potential"
    else:
        recreation_potential = options['potential']

    recreation_potential_equation = equation.format(result=recreation_potential,
            expression=recreation_potential_expression)

    # grass.mapcalc(RP, quiet=False, verbose=False, overwrite=True)
    grass.mapcalc(recreation_potential_equation, overwrite=True)

    # normalize recreation potential map
    normalize (recreation_potential, recreation_potential_normalised)


# Input :: Components

# Inter
if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    sys.exit(main())
