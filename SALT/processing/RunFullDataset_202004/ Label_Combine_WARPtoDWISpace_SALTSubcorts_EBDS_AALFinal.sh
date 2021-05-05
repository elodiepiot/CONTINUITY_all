#!/bin/bash

# I. This script will label individual subcortical  surface  .vtk files (subcorticals in T1 space) 
# II. Combine the labeled subcorticals into a single .vtk surface file (still in T1 space)
# III. Apply the T1 to DWI Space WARP (previously calculated) to the Subcortical Surfaces in T1 space. (Now in DWI Space) 
# IV Combine the .vtk Subcortical file in DWI space with the labeled cortical surface in DWI Space.  (DWI Space)
# V. Output the beginning of a .csv file to submit to tractographyScriptAppSumbitJob.sh NOTE: this part can be improved – I add some of the final formatting manually. I wasn’t as familiar with formatting a .csv from bash , it was quicker than looking it up.  The output give you the pathnames for the CIVILITY input files  in the appropriate order which is mainly what you need. 

# Input 1 : a .txt file with a list of IDs to wrap : again the file hierarchy is a bit specific to how my data are organized and may need to be changed. 

# Input 2 : Number 0,1,2,3 (specific to this project- quick and dirty signifying where the home data file is located- for my data it was scattered in a bunch of different directories)

# Input 3 : Name of output .csv file to submit to CIVILITY (this part can be improved – I add some of the final formatting manually just because I wasn’t as familiar with formatting a .csv from bash- this was just helpful to give you the data paths of the input). 

# Hard Coded Input: 
#	the surfSPHARM.vtk subcortical surface files 
#	the subcortical names (AmyL AmyR CaudL CaudR GPL GPR HippoL HippoR PutL PutR ThalL ThalR)
#	the T1 to DWI Space WARP .nrrd file 
#	the cortical .vtk labeled surface in DWISpace (for example either AAL or Destrieux) 

# Main Output: 
#	a .vtk surface file in DWISpace with the cortical and subcorticals labeled such that they match the .json parcellation file (to be input into CIVILITY) 


###################################################################################################################################
# Begin Code 

# *****************************************
# DATA ENV VARIABLES
# *****************************************
#
# This is all just specific to the Conte/Twin project 
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

# Set the parcellation (can make this input)
parc="AAL"

# *****************************************
# RUN 
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

# set where the labels are stored : Could be made input
KMWDir="/NIRAL/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/SubCortical_Processing/SALT/processing/RunFullDataset_202004/TxtLabels_${parc}"

# set which subcorticals to label : Could be made input
subcorticals=(AmyL AmyR CaudL CaudR GPL GPR HippoL HippoR PutL PutR ThalL ThalR)


# (NOTE labelName should be the same as the final parcellation name you wish to merge them with- if it is different you will lose all labels in the final merging.  You can check the scalar name of the original cortical .vtk in Slicer to obtain this information.
  
labelName="AAL" # the scalar label name 

###############################################
#OUTPUT
###############################################
OutFolder="${saltDIR}/Labels_${parc}"

echo $OutFolder


if [ -d "$OutFolder" ]; then 
        echo $OutFolder Found : OVERWRITING $ID
        cmd="rm $OutFolder -r"
        eval $cmd
fi 
	
        cmd="mkdir $OutFolder"
        eval $cmd
	
#################################################
# START
# For each region label the SALT file with the Atlas label value using MeshMath
for region in "${subcorticals[@]}"; do


KWMFile="${KMWDir}/${region}_1002_KWM.txt" 	

SPHARMSurf="${saltDIR}/${ID}-*_label_${region}_pp_surfSPHARM.vtk"

echo $SPHARMSurf

if [ ! -f $SPHARMSurf ]; then

SPHARMSurf="${saltDIR}/${ID}-*_label_${region}_ppManualFix_surfSPHARM.vtk"
echo $SPHARMSurf >> manualFixes.txt
#echo $SPHARMSurf


fi 
 

# Create SPHARM surface labeled with the new atlas label. 
SPHARMSurfL="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_${region}_pp_SPHARM_labeled.vtk"

#echo $SPHARMSurfL 

if [ -f $SPHARMSurfL ]; then
echo $SPHARMSurfL :Found Skipping Labeling
else
#echo $SPHARMSurf
#echo $region
	cmd="MeshMath $SPHARMSurf $SPHARMSurfL -KWMtoPolyData $KWMFile $labelName  -v"
	eval $cmd
	#echo $SPHARMSurfL
fi # if SPHARMSurfL exists 
done # for each region 
echo Labeling for ${ID} Finished


##################################
# COMBINE the labeled subcorticals 
##################################
# add the first 2 to create an initial output file. 
outputSurface="${OutFolder}/${ID}-${parc}_Labeled_Subcorticals_Combined_T1Space.vtk"
#if [ -f "$outputSurface" ]; then
#echo $outputSurface Found: Skipping Individual Labeling
#else 

s1='${OutFolder}/${ID}-T1_SkullStripped_scaled_label_${subcorticals[0]}_pp_SPHARM_labeled.vtk'
s2='${OutFolder}/${ID}-T1_SkullStripped_scaled_label_${subcorticals[1]}_pp_SPHARM_labeled.vtk'
#echo $s1

cmd="polydatamerge -f ${s1} -g ${s2} -o ${outputSurface}"
eval $cmd			

#add the rest: for now this number is hard-coded, could make dynamic
for i in $(seq 2 11); do
	toAdd="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_${subcorticals[$i]}_pp_SPHARM_labeled.vtk"
	echo $toAdd

	cmd="polydatamerge -f $outputSurface -g $toAdd -o $outputSurface"
	eval $cmd
done
#fi  # if exist outputSurface
echo Combining Subcorticals for ${ID} finished



#########################
# Transform into DWISpace
#########################
# Set the T1 to DWI WARP : this can eventually be made input 
ConcatedWarp="/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/PreCIVILITY/${PROJ}/*/*/*/${ID}/T1ToDWISpace/Warps/${ID}_ConcatenatedInvWarp.nrrd"

# this is just a quick and dirty way for me to get some of the paths given my hierarchy : specific to my data structure
toReplace="/Warps/${ID}_ConcatenatedInvWarp.nrrd"
outDirSurfDWISpace=${ConcatedWarp/$toReplace/}
test="$(dirname $ConcatedWarp)"
test="$(dirname $test)"


subsAllDWISpace="${test}/IntermediateFiles/Surfaces/stx_${ID}_${parc}_Labeled_Subcorticals_Combined_DWISpace.vtk"

#if [ -f $subAllDWISpace ]; then
	#echo $subAllDWISpace Found: Skipping Transformation into DWISpace
#else
	cmd="polydatatransform_v1.2.1 --fiber_file $outputSurface -D $ConcatedWarp -o $subsAllDWISpace --inverty --invertx"
	eval $cmd
copysubsALL="/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/SubCortical_Processing/Collected_SubcorticalsDWISpace/stx_${ID}_${parc}_Labeled_Subcorticals_Combined_DWISpace.vtk"



cmd="cp $subsAllDWISpace $copysubsALL"
echo $cmd
eval $cmd

#fi

outDirForCivility="$(dirname $test)"

outputSurfaceFullMerge="${outDirForCivility}/Input_Civility_DWISpace/stx_${ID}_T1_CombinedSurface_white_${parc}_WithSubcorticals.vtk"

#############################
# Combine Subs With Destrieux (or Atlas of choice) 
#############################
#if [ -f $outputSurfaceFullMerge ]; then 
	#echo $outputSurfaceFullMerge Found: Skipping 
#else
	inputMerge="${test}/00_QC_Visualization/stx_${ID}_T1_CombinedSurface_white_${parc}.vtk"

if [ -f $inputMerge ]; then
	polydatamerge -f $subsAllDWISpace -g $inputMerge -o $outputSurfaceFullMerge

	copyMerge="/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/SubCortical_Processing/Collected_FinalSurfaces/stx_${ID}_T1_CombinedSurface_white_${parc}_WithSubcorticals.vtk"

	cmd="cp $outputSurfaceFullMerge $copyMerge"
	eval $cmd
#fi
#echo $outputSurfaceFullMerge

##########################
# Start making the .csv for Civility (input via the command line): this is also somewhat specific for my path names and data structure
##########################

#if [ "$#" -ne 3 ]; 
#then 

#else 
# --------------- save to csv file ($3)  ---------------------
name=${ID}_AALSubCorts
dwi="${outDirForCivility}/Input_Civility_DWISpace/${ID}_42_DWI_QCed_VC_1mm.nrrd"
t1="${outDirForCivility}/T1ToDWISpace/00_QC_Visualization/${ID}_${fterm}_DWISpace.nrrd"
mask="${outDirForCivility}/Input_Civility_DWISpace/${ID}_Original_DWI_BrainMask_1mm.nrrd"
table="/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/jsonFilesForCivility/TABLE_${parc}_SubCorticals.json"
surface=${outputSurfaceFullMerge}
labelname=$labelName
overlapping="TRUE"
create_tar="FALSE"
#probtrackParam="\"\"\"-P 1000 --steplength=0.75 --sampvox=0.5\"\"\""

#printf "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" $name $dwi $t1 $mask $table $surface $labelname $overlapping $create_tar $probtrackParam >> $3
printf "%s,%s,%s,%s,%s,%s,%s,%s,%s\n" $name $dwi $t1 $mask $table $surface $labelname $overlapping $create_tar >> $3
#fi
 
echo $ID Complete
else 
echo ERROR $ID No AAL vtk Found 
fi


done < $idfile
exit

