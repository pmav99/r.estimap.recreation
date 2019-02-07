#!/usr/bin/env bash

set -xeuo pipefail

# Before starting to refactor we need to have a "known working state".
# These are the maps and the files that we will use as a "known working state"
map_names=( demand flow spectrum unmet_demand potential opportunity flow_corine_land_cover_2006 maes_ecosystem_types maes_ecosystem_types_flow )
csv_names=( supply.csv use.csv )

# # This for-loop will create this state.
#map_names=( demand flow spectrum unmet_demand potential opportunity flow_corine_land_cover_2006 maes_ecosystem_types maes_ecosystem_types_flow )
#for name in "${map_names[@]}"
#do
#  rm -rf "${name}".master
#  r.univar "${name}" > master."${name}"
#done
#
#csv_names=( supply.csv use.csv )
#for name in "${csv_names[@]}"
#do
#  echo "${name}"
#  rm -rf "${name}".master
#  cp "${name}" .master."${name}"
#done

g.region  raster=area_of_interest

r.reclass --overwrite input="local_administrative_units_AT" output="regions" rules="lau_to_regions_for_test.rules"

g.remove type=raster name=potential_corine -f

#r.estimap.recreation  land=land_suitability  infrastructure=distance_to_infrastructure  population=population_2015  base=local_administrative_units  landcover=corine_land_cover_2006  aggregation=regions  land_classes=corine_accounting_to_maes_land_classes.rules  potential=potential_corine supply=supply --o --verbose

r.estimap.recreation \
  --verbose \
  --overwrite \
  mask=area_of_interest \
  land=land_suitability \
  water=water_resources,bathing_water_quality \
  natural=protected_areas \
  infrastructure=distance_to_infrastructure \
  potential=potential \
  opportunity=opportunity \
  spectrum=spectrum \
  demand=demand \
  unmet=unmet_demand \
  flow=flow \
  population=population_2015 \
  base=local_administrative_units \
  landcover=corine_land_cover_2006 \
  aggregation=regions \
  land_classes=corine_accounting_to_maes_land_classes.rules \
  supply=supply \
  use=use \

rm -rf flow_corine_land_cover_2006.current maes_ecosystem_types.current maes_ecosystem_types_flow.current

for name in "${map_names[@]}"
do
  rm -rf current."${name}"
  r.univar "${name}" > current."${name}"
  echo "${name}"
  diff master."${name}" current."${name}"
done

