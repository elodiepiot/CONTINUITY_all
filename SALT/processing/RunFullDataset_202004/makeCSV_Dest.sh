#!/bin/bash


# *****************************************
# Executables
# *****************************************


# *****************************************
# DATA ENV VARIABLES
# *****************************************
# Where the Original Brain Stem Binary Masks are located (From Imperial)
#DATA_HOME="/dichter/AutoSeg_Rerun_CONTE1and2/Data" # MAKE SURE THIS IS THE RIGHT LOCATION FOR YOUR DATA ! 

fterm="T1_SkullStripped_scaled"
PROJ="Conte"

if [ $2 -eq 0 ] 
then
	# Conte 1 and 2 (option 0)
	DATA_HOME="/dichter/AutoSeg_Rerun_CONTE1and2/Data"
elif [ $2 -eq 1 ] 
then
	# Conte 4 and 6 (option 1)
	DATA_HOME="/Human/conte_projects/CONTE_NEO/AUTOSEG_4-6year_T1andMultiAtlas/Data"
elif [ $2 -eq 2 ] 
then
	# Twin 1 and 2 (option 2)
	DATA_HOME="/Human2/CONTE2/TWINS-SubCort/Data"
	PROJ="Twin"
	fterm="T1_regAtlas-SkullStripped"
else
	# Twin 4 and 6 (option 3 )
	DATA_HOME="/Human/twin-gilmore/AUTOSEG_4-6year_T1andMultiAtlas/Data"
	PROJ="Twin"
	#fterm="T1_regAtlas-SkullStripped"
fi

#echo $DATA_HOME

# *****************************************
# RUN INPUT FOLDERS
# *****************************************
# Text File of Subject IDs To Run 
idfile=$1
# ******************************************

while read idx
do

# Project ID
ID=$idx

# INPUT # Folder with all SALT files 
saltDIR="${DATA_HOME}/${ID}/AutoSegTissue_1year_v2-MultiAtlas/SALT"

ConcatedWarp="/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/PreCIVILITY/${PROJ}/*/*/*/${ID}/T1ToDWISpace/Warps/${ID}_ConcatenatedInvWarp.nrrd"

toReplace="/Warps/${ID}_ConcatenatedInvWarp.nrrd"
outDirSurfDWISpace=${ConcatedWarp/$toReplace/}
test="$(dirname $ConcatedWarp)"
test="$(dirname $test)"

outDirForCivility="$(dirname $test)"

outputSurfaceFullMerge="${outDirForCivility}/Input_Civility_DWISpace/stx_${ID}_T1_CombinedSurface_white_Destrieux_WithSubcorticals.vtk"


 
# --------------- save to csv file ($3)  ---------------------
name=${ID}
dwi="${outDirForCivility}/Input_Civility_DWISpace/${ID}_42_DWI_QCed_VC_1mm.nrrd"
t1="${outDirForCivility}/T1ToDWISpace/00_QC_Visualization/${ID}_${fterm}_DWISpace.nrrd"
mask="${outDirForCivility}/Input_Civility_DWISpace/${ID}_Original_DWI_BrainMask_1mm.nrrd"
table="/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/jsonFilesForCivility/TABLE_Destrieux_SubCorticals_BrainStem.json"
surface=${outputSurfaceFullMerge}
labelname="Destrieux"
overlapping="TRUE"
create_tar="FALSE"
#probtrackParam="\"\"\"-P 1000 --steplength=0.75 --sampvox=0.5\"\"\""

#printf "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" $name $dwi $t1 $mask $table $surface $labelname $overlapping $create_tar $probtrackParam >> $3
printf "%s,%s,%s,%s,%s,%s,%s,%s,%s\n" $name $dwi $t1 $mask $table $surface $labelname $overlapping $create_tar >> $3
#fi
 


done < $idfile
exit

