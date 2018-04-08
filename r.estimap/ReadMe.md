# About

Implementation of ESTIMAP as a GRASS GIS add-on.

## Open questions

* Which are the minimum required input maps to run the module?

* Which are the minimum required output maps to run the module?

* In the function that sets small values (<.0001 or <.0003) to zero, why not
overwrite the input raster map itself?
  * This will possibly retouch irreversibly the given input raster map. Which
  is not correct.

* Functions `normalise_component` and `zerofy_and_normalise_component` differ
only in one step. The latter function does, in addition to what the former
does, the following: `zerofy_small_values(tmp_intermediate, threshhold,
tmp_output)`. Is the duplication worth?

* Why not use `r.cross` in `recreation_spectrum_expression`.

## Answered questions

*  Why not use r.null for the "suitability" map?
 *  Answer: No reason not to use r.null.

*  What is the following (found in the "original" python script that derived
recreation potential?
> # ---------------------------------------------------------------------
> # mask RA with recode industry ?
> # ---------------------------------------------------------------------

 * Answer: some remaining from older attempts. Now irrelevant.
