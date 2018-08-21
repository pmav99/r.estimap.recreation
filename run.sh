#!/bin/bash - 
#===============================================================================
#
#          FILE: run.sh
# 
#         USAGE: ./run.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Nikos Alexandris (), nik@nikosalexandris.net
#  ORGANIZATION: 
#       CREATED: 07/13/2018 17:16
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

cd /geo/projects/maes/natcapes/r.estimap/ && grasstrunk-make-module &&

# r.estimap \
# land=slsra_0AT001L2 \
# water=waternAT001L2 \
# natural=cdda_AT001L2 \
# anthropic=anthropic_surfaces_AT001L2 \
# anthropic_distances=reclassification_rules/anthropic_proximity_categories.rules \
# roads=r345_AT001L2 \
# roads_distances=reclassification_rules/anthropic_proximity_categories.rules \
# lakes=lakes_AT001L2 \
# bathing_water=bathing_water_quality_2006_AT001L2 \
# bathing_coefficients='euclidean,1,5,0.01101' \
# protected=cdda_v15_iso3_aut \
# protected_scores=reclassification_rules/designated_areas_classes.scores \
# spectrum_distances=reclassification_rules/recreation_spectrum_distance_categories.rules \
# potential=potential \
# opportunity=opportunity \
# spectrum=spectrum \
# demand=test_demand \
# base=local_administrative_units \
# population=ghsl_population_2015_AT001L2 \
# metric=manhattan \
# units=me,p

r.estimap \
land=slsra_0AT001L2 \
water=waternAT001L2 \
natural=cdda_AT001L2 \
anthropic=anthropic_surfaces_AT001L2 \
anthropic_distances=reclassification_rules/anthropic_proximity_categories.rules \
roads=r345_AT001L2 \
roads_distances=reclassification_rules/anthropic_proximity_categories.rules \
lakes=lakes_AT001L2 \
spectrum_distances=reclassification_rules/recreation_spectrum_distance_categories.rules \
potential=potential \
opportunity=opportunity \
spectrum=spectrum \
demand=test_demand \
base=local_administrative_units \
population=ghsl_population_2015_AT001L2 \
metric=euclidean \
units=me,p

# r.estimap \
# land=slsra_0AT001L2 \
# water=waternAT001L2 \
# natural=cdda_AT001L2 \
# anthropic=anthropic_surfaces_AT001L2 \
# anthropic_distances=reclassification_rules/anthropic_proximity_categories.rules \
# roads=r345_AT001L2 \
# roads_distances=reclassification_rules/anthropic_proximity_categories.rules \
# lakes=lakes_AT001L2 \
# bathing_water=bathing_water_quality_2006_AT001L2 \
# bathing_coefficients='euclidean,1,5,0.01101' \
# protected=cdda_v15_iso3_aut \
# protected_scores=reclassification_rules/designated_areas_classes.scores \
# spectrum_distances=reclassification_rules/recreation_spectrum_distance_categories.rules \
# potential=potential \
# opportunity=opportunity \
# spectrum=spectrum \
# demand=test_demand \
# base=local_administrative_units \
# population=ghsl_population_2015_AT001L2 \
# metric=manhattan \
# units=me,p
