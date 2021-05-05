#!/bin/bash


# Text File of Subject IDs To Run 
idfile=$1

# Input Directory 
outDirForCivility=
# ******************************************

while read idx
do

# Project ID
ID=$idx


# --------------- save to csv file ($3)  ---------------------
name=${ID}-0yr_2020

dwi="${outDirForCivility}/Input_Civility_DWISpace/${ID}_42_DWI_QCed_VC_1mm.nrrd"

t1="${outDirForCivility}/T1ToDWISpace/00_QC_Visualization/${ID}_DWISpace.nrrd"

mask="${outDirForCivility}/Input_Civility_DWISpace/${ID}_Original_DWI_BrainMask_1mm.nrrd"

table="/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/jsonFilesForCivility/TABLE_AAL.json"

surfaceInner="${outDirForCivility}/

surfaceColour=

labelname="colour" 

overlapping="TRUE"

create_tar="FALSE"

if [ -f $dwi ] & [ -f $t1 ] & [ -f $mask ] & [ -f table ] & [ -f $surface ]; then 

#probtrackParam="\"\"\"-P 1000 --steplength=0.75 --sampvox=0.5\"\"\""


printf "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" $name $dwi $t1 $mask $table $surfaceInner $surfaceColour $labelname $overlapping $create_tar >> $3

 
else 

echo ERROR $ID : FILES MISSING

fi
done < $idfile
exit

