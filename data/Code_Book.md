Code Book
---------

**Under construction**

# About

Within the context of the `r.estimap.recreation` GRASS GIS add-on, this code
book describes:

- [Input] the raw data used to prepare the sample data set

- [Processing] the transformations applied to the raw data

- [Samples] the sample data set used to test the add-on

- [Output] the output maps derived after running the add-on

#

Of concern are the following "input" data sets:

## Input maps

### In overview

|------------------------------|-----------------------------------|--------|
| Map                          | Source                            |        |
|------------------------------|-----------------------------------|--------|
| `area_of_interest`           | Urban Audit 2011-2014             | Vector |
|------------------------------|-----------------------------------|--------|
| `corine_land_cover_2006`     | CORINE land cover                 | Raster |
|------------------------------|-----------------------------------|--------|
| `land_suitability`           | CORINE Land Cover 2006            | Raster |
|------------------------------|-----------------------------------|--------|
| `water_resources`            | ?                                 | ?      |
|------------------------------|-----------------------------------|--------|
| `bathing_water_quality`      | State of bathing water            | Vector |
|------------------------------|-----------------------------------|--------|
| `protected_areas`            | World Database on Protected Areas | Vector |
|------------------------------|-----------------------------------|--------|
| `distance_to_infrastructure` | ?                                 | ?      |
|------------------------------|-----------------------------------|--------|
| `population_2015`            | Global Human Settlement Layer     | Raster |
|------------------------------|-----------------------------------|--------|
| `local_administrative_units` | Local Administrative Units (LAU)  | Vector |
|------------------------------|-----------------------------------|--------|
| `regions`                    | Local Administrative Units (LAU)  | Vector |
|------------------------------|-----------------------------------|--------|

Other

*  `corine_accounting_to_maes_land_classes.rules


#### Urban Audit 2011-2014

Eurostat's Urban Audit Cities 2011-2014 (ESRI Shapefile) vector map contains
the boundaries of cities, greater cities and functional urban areas (EC-OECD).

Links:

  * https://ec.europa.eu/eurostat/cache/GISCO/geodatafiles/URAU-2011-2014-SH.zip
  * available at https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/urban-audit

#### CORINE land cover

#### State of bathing water

Links:

  * https://www.eea.europa.eu/themes/water/status-and-monitoring/state-of-bathing-water/state/state-of-bathing-water-3

#### Local Administrative Units (LAU)

Links:

  * https://ec.europa.eu/eurostat/web/nuts/local-administrative-units

#### WDPA

#### GHSL

## Processing

## Sample data set

* area_of_interest
* corine_land_cover_2006
* land_suitability
* water_resources
* bathing_water_quality
* protected_areas
* distance_to_infrastructure
* population_2015
* local_administrative_units
* regions
* corine_accounting_to_maes_land_classes.rules

## Output maps

* potential
* opportunity
* spectrum
* demand
* unmet_demand
* flow
