#!/bin/bash


# *****************************************
# Executables
# *****************************************


# *****************************************
# DATA ENV VARIABLES
# *****************************************
# Where the Original Brain Stem Binary Masks are located (From Imperial)
DATA_HOME="/dichter/AutoSeg_Rerun_CONTE1and2/Data" # Make sure you have the correct file folder 

# *****************************************
# RUN INPUT FOLDERS
# *****************************************
# Text File of Subject IDs To Run 
txtFILE="/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/ListsForBrent/Healthy_SubjectsWith_1Yr_2Yr_4Yr_WMData/Conte1Yrs.txt"
# ******************************************

#while IFS= read -r subject; do

# Project ID
#ID=$subject
ID='neo-0113-2-1year'
PROJ="CONTE"
echo Starting BrainStemExtraction: subject $ID

# INPUT
OriginalSeg="${DATA_HOME}/${ID}/AutoSegTissue_1year_v2-MultiAtlas/WarpROI/${ID}-T1_SkullStripped_scaled_corrected_EMS--Imperial_Parc_SubCort_Extended-WarpReg_label_1.nrrd"
echo $OriginalSeg 
#echo $ID
#echo $DATA_HOME

###############################################
#OUTPUT
###############################################
OutFolder="${DATA_HOME}/${ID}/AutoSegTissue_1year_v2-MultiAtlas/SALT"

cmd="mkdir $OutFolder"
eval $cmd

BrainStemAll="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem.nrrd"
echo $BrainStemAll


# Intermediate Files as we need to extract 3 brainstem regions to get good seg (19, 74 and 75)-removed
BrainStemA="${OutFolder}/${ID}-T1-SkullStripped_scaled_label_BrainstemA.nrrd"
BrainStemB="${OutFolder}/${ID}-T1-SkullStripped_scaled_label_BrainstemB.nrrd"

#After cleaning via SegPostProcess 
BrainStemPostProcess="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_pp.nrrd"

# SPHARM surfaces

BrainStemPara="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_pp_para.vtk"
BrainStemInitialSurf="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_pp_surf.vtk"

#Note the SPHARM pipeline will add on the appropriate endings to deliniate the output .vtks
# the primary output of interest is ${BrainStemSPHARM}_SPHARM.vtk the final SPHARM mesh. 
BrainStemSPHARM="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_pp_surf"

#################################################
# START
# Extract the brainstem labels (Extract 19, 74, and 75)
cmd="ImageMath $OriginalSeg -extractLabel 19 -outfile $BrainStemAll"
#eval $cmd

cmd="ImageMath $OriginalSeg -extractLabel 74 -outfile $BrainStemA"
#eval $cmd

cmd="ImageMath $OriginalSeg -extractLabel 75 -outfile $BrainStemB"
#eval $cmd

# Combine brain stem into one .nrrd 
cmd="ImageMath $BrainStemAll -combine $BrainStemA -outfile $BrainStemAll"
#eval $cmd

cmd="ImageMath $BrainStemAll -combine $BrainStemB -outfile $BrainStemAll"
#eval $cmd

# remove intermediate files
rm $BrainStemA
rm $BrainStemB



# Binary Volume Segmentation Cleaning/Smoothing
cmd="SegPostProcessCLP $BrainStemAll $BrainStemPostProcess --space 0.75,0.75,0.75 --rescale --verb --Gauss"
#eval $cmd

# Surface Generation using SPHARM
# Parameterization
cmd="GenParaMeshCLP $BrainStemPostProcess $BrainStemPara $BrainStemInitialSurf"
#eval $cmd
# Make Final SPHARMMesh
cmd="ParaToSPHARMMeshCLP $BrainStemPara $BrainStemInitialSurf $BrainStemSPHARM --subdivLevel 10 --spharmDegree 15"
eval $cmd
#done < "${txtFILE}"
exit

