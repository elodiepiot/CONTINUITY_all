#!/bin/bash


# *****************************************
# Executables
# *****************************************


# *****************************************
# DATA ENV VARIABLES
# *****************************************
# Where the Original Brain Stem Binary Masks are located (From Imperial)
#DATA_HOME="/dichter/AutoSeg_Rerun_CONTE1and2/Data" # MAKE SURE THIS IS THE RIGHT LOCATION FOR YOUR DATA ! 

fterm="T1_SkullStripped_scaled_corrected_EMS--Imperial_Parc_SubCort_Extended-WarpReg_label_1.nrrd"
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
	fterm="T1_regAtlas-SkullStripped_corrected_EMS--Imperial_Parc_SubCort_Extended-WarpReg_label_1.nrrd"
else
	# Twin 4 and 6 (option 3 )
	DATA_HOME="/Human/twin-gilmore/AUTOSEG_4-6year_T1andMultiAtlas/Data"
	PROJ="Twin"
	fterm="T1_regAtlas-SkullStripped_corrected_EMS--Imperial_Parc_SubCort_Extended-WarpReg_label_1.nrrd"
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
#echo Starting BrainStemExtraction: subject $ID

# INPUT # Folder with all SALT files 
saltDIR="${DATA_HOME}/${ID}/AutoSegTissue_1year_v2-MultiAtlas/SALT"

KMWDir="/work/maria5/EBDS_CIVILITY/Maria_Playground/processing/subCorticalProcessingFiles/TxtLabels_Destrieux" 

subcorticals=(AmyL AmyR Brainstem CaudL CaudR GPL GPR HippoL HippoR PutL PutR ThalL ThalR)

labelName="Destrieux" # the scalar label name 
# (note this name should be the same as the final parcellation name you wish to merge them with- if it is different you will lose all labels in the final merging) 
###############################################
#OUTPUT
###############################################
OutFolder="${saltDIR}/Labels_Destrieux"

cmd="mkdir $OutFolder"
eval $cmd


#################################################
# START
# For each region label the SALT file with the Atlas label value using MeshMath
for region in "${subcorticals[@]}"; do
# 
KWMFile="${KMWDir}/${region}_1002_KWM.txt" 	
SPHARMSurf="${saltDIR}/${ID}-T1_SkullStripped_scaled_label_${region}_pp_surfSPHARM.vtk"

SPHARMSurfL="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_${region}_pp_SPHARM_labeled.vtk"
#echo $SPHARMSurf
#echo $region
cmd="MeshMath $SPHARMSurf $SPHARMSurfL -KWMtoPolyData $KWMFile $labelName  -v"
eval $cmd

done

# combine them 

# add the first 2 to create an initial output file. 
outputSurface="${OutFolder}/${ID}-Destrieux_Labeled_Subcorticals_Combined_T1Space.vtk"
s1="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_${subcorticals[0]}_pp_SPHARM_labeled.vtk"
s2="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_${subcorticals[1]}_pp_SPHARM_labeled.vtk"

cmd="polydatamerge -f ${s1} -g ${s2} -o ${outputSurface}"
eval $cmd			

#add the rest
for i in $(seq 2 12); do
	toAdd="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_${subcorticals[$i]}_pp_SPHARM_labeled.vtk"
	cmd="polydatamerge -f $outputSurface -g $toAdd -o $outputSurface"
	#eval $cmd
done

# transform into DWISpace
ConcatedWarp="/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/PreCIVILITY/${PROJ}/*/*/*/${ID}/T1ToDWISpace/Warps/${ID}_ConcatenatedInvWarp.nrrd"

toReplace="/Warps/${ID}_ConcatenatedInvWarp.nrrd"
outDirSurfDWISpace=${ConcatedWarp/$toReplace/}
test="$(dirname $ConcatedWarp)"
test="$(dirname $test)"
subsAllDWISpace="${test}/IntermediateFiles/Surfaces/stx_${ID}_Destrieux_Labeled_Subcorticals_Combined_DWISpace.vtk"


cmd="polydatatransform_v1.2.1 --fiber_file $outputSurface -D $ConcatedWarp -o $subsAllDWISpace --inverty --invertx"
eval $cmd
outDirForCivility="$(dirname $test)"

outputSurfaceFullMerge="${outDirForCivility}/Input_Civility_DWISpace/stx_${ID}_T1_CombinedSurface_white_Destrieux_WithSubcorticals.vtk"

inputMerge="${test}/IntermediateFiles/Surfaces/stx_${ID}_T1_CombinedSurface_white_Destrieux.vtk"

polydatamerge -f $subsAllDWISpace -g $inputMerge -o $outputSurfaceFullMerge

# --------------- save to csv file ($3)  ---------------------
name=${ID}
dwi="${outDirForCivility}/Input_Civility_DWISpace/${ID}_42_DWI_QCed_VC_1mm.nrrd"
t1="${outDirForCivility}/T1ToDWISpace/00_QC_Visualization/${ID}_T1_SkullStripped_scaled_DWISpace.nrrd"
mask="${outDirForCivility}/Input_Civility_DWISpace/${ID}_Original_DWI_BrainMask_1mm.nrrd"
table="/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/jsonFilesForCivility/TABLE_DEST.json"
surface=${outputSurfaceFullMerge}
labelname="Destrieux"
overlapping="TRUE"
create_tar="FALSE"
probtrackParam="\"\"\"-P 1000 --steplength=0.75 --sampvox=0.5\"\"\""

printf "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" $name $dwi $t1 $mask $table $surface $labelname $overlapping $create_tar $probtrackParam >> $3


done < $idfile
exit

