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

parc="AAL"
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
#echo Starting BrainStemExtraction: subject $ID

# INPUT # Folder with all SALT files 
saltDIR="${DATA_HOME}/${ID}/AutoSegTissue_1year_v2-MultiAtlas/SALT"


subcorticals=(AmyL AmyR CaudL CaudR GPL GPR HippoL HippoR PutL PutR ThalL ThalR)


#################################################
# START
# For each region label the SALT file with the Atlas label value using MeshMath
for region in "${subcorticals[@]}"; do

SPHARMSurf="${saltDIR}/${ID}-*_label_${region}_pp_surfSPHARM.vtk"

if [ ! -f $SPHARMSurf ]; then

SPHARMSurf="${saltDIR}/${ID}-*_label_${region}_ppManualFix_surfSPHARM.vtk"
echo $SPHARMSurf >> manualFixes.txt
#echo $SPHARMSurf

fi 
 
out="${saltDIR}/SurfaceAreas"
echo $out
if [ ! -d $out ]; then 
 mkdir $out
fi 

# get the SA of the subcorticals 

/tools/bin_linux64/Calculate_SurfaceArea $SPHARMSurf $out/${region}

done # for each region 

# calculate the surface area for the cortex 
# get the filename for the given ID : For better or worse data are sorted by scanner and T2 quality : need to search for the full name. 

ConcatedWarp="/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/PreCIVILITY/${PROJ}/*/*/*/${ID}/T1ToDWISpace/Warps/${ID}_ConcatenatedInvWarp.nrrd"

toReplace="/Warps/${ID}_ConcatenatedInvWarp.nrrd"
outDirSurfDWISpace=${ConcatedWarp/$toReplace/}
test="$(dirname $ConcatedWarp)"
test="$(dirname $test)"
	
	
surfCort="${test}/00_QC_Visualization/stx_${ID}_T1_CombinedSurface_white_AAL.vtk"

# get the SA of the subcorticals 

/tools/bin_linux64/Calculate_SurfaceArea $surfCort $out/cortex

done < $idfile
exit

