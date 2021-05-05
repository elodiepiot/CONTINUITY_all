#!/bin/bash

# for the twin 4yrs we need to rerun every step 202001 as their was a problem with the 'fterm' in the CreateBrainStemSurfaces 
# (only twin 1 and 2 years seem to have the differential naming convention: NOT 4 and 6) 
bash ./CreateBrainStemSurfaces_ImperialParc_EBDS_finalTestBSSeg.sh $1 $2
#./RunSPHARM-PDM_Put_and_GP_EBDS_final.script $1 $2
#bash ./Label_Combine_WARPtoDWISpace_SALTSubcorts_EBDS_final.sh $1 $2 
