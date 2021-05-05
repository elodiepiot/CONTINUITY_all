#!/bin/bash


# *****************************************
# Executables
# *****************************************


# *****************************************
# DATA ENV VARIABLES
# *****************************************
# Where the Original Brain Stem Binary Masks are located (From Imperial)
#DATA_HOME="/dichter/AutoSeg_Rerun_CONTE1and2/Data" # Make sure you have the correct file folder 

fterm="T1_SkullStripped_scaled_corrected_EMS--Imperial_Parc_SubCort_Extended-WarpReg_label_1.nrrd"
fterm2="T1_SkullStripped_scaled"
studyYear="Conte1_and_2Yr"
if [ $2 -eq 0 ] 
then
	# Conte 1 and 2 (option 0)
	DATA_HOME="/dichter/AutoSeg_Rerun_CONTE1and2/Data"
elif [ $2 -eq 1 ] 
then
	# Conte 4 and 6 (option 1)
	DATA_HOME="/Human/conte_projects/CONTE_NEO/AUTOSEG_4-6year_T1andMultiAtlas/Data"
studyYear="Conte4_and_6Yr"
elif [ $2 -eq 2 ] 
then
	# Twin 1 and 2 (option 2)
	DATA_HOME="/Human2/CONTE2/TWINS-SubCort/Data"
	fterm="T1_regAtlas-SkullStripped_corrected_EMS--Imperial_Parc_SubCort_Extended-WarpReg_label_1.nrrd"
	studyYear="Twin1_and_2Yr"
	fterm2="T1_regAtlas-SkullStripped"
else
	# Twin 4 and 6 (option 3 )
	DATA_HOME="/Human/twin-gilmore/AUTOSEG_4-6year_T1andMultiAtlas/Data"
	studyYear="Twin4_and_6Yr"
	
fi

#echo $DATA_HOME

# *****************************************
# RUN INPUT FOLDERS
# *****************************************
# Text File of Subject IDs To Run 
# **************************************

idfile=$1

while read idx
do
# Project ID
#ID=$subject
	#idx=${idx//$'\n'/} 
	ID=$idx
echo $ID
	countFail=0 # some of the brain stem will not have spherical topology - establish a counter. 
	#echo Starting BrainStemExtraction: subject $ID
	#echo $DATA_HOME

	# INPUT
	OriginalSeg="${DATA_HOME}/${ID}/AutoSegTissue_1year_v2-MultiAtlas/WarpROI/${ID}-${fterm}"
	#echo $OriginalSeg 
#echo $ID
#echo $DATA_HOME

touch "FailedBrainstems_Close2Gauss_${studyYear}.txt"
###############################################
#OUTPUT
###############################################
#OutFolder="${DATA_HOME}/${ID}/AutoSegTissue_1year_v2-MultiAtlas/SALT" 
OutFolder="/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/SubCortical_Processing/temp_BrainStemClosing/${ID}"

if [ ! -f $OutFolder ]; then  
cmd="mkdir $OutFolder"
eval $cmd
fi
BrainStemAll="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem.nrrd"
#echo $BrainStemAll


# Intermediate Files as we need to extract 3 brainstem regions to get good seg (19, 74 and 75)-removed
BrainStemA="${OutFolder}/${ID}-T1-SkullStripped_scaled_label_BrainstemA.nrrd"
BrainStemB="${OutFolder}/${ID}-T1-SkullStripped_scaled_label_BrainstemB.nrrd"

#After cleaning via SegPostProcess 
BrainStemPostProcess1="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_ppClose2.nrrd"
BrainStemPostProcessFinal="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_ppFinal.nrrd"

# SPHARM surfaces

BrainStemPara="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_ppFinal_para.vtk"
BrainStemInitialSurf="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_ppFinal_surf.vtk"

#Note the SPHARM pipeline will add on the appropriate endings to deliniate the output .vtks
# the primary output of interest is ${BrainStemSPHARM}_SPHARM.vtk the final SPHARM mesh. 
BrainStemSPHARM="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_ppFinal_surf"

# Log Files 
BrainStemLogGenPPFinal="${OutFolder}/BrainStemFinal_genparamesh.log"

#################################################
# START
if [ ! -f $BrainStemAll ]; then  
# Extract the brainstem labels (Extract 19, 74, and 75)
cmd="ImageMath $OriginalSeg -extractLabel 19 -outfile $BrainStemAll"
eval $cmd

cmd="ImageMath $OriginalSeg -extractLabel 74 -outfile $BrainStemA"
eval $cmd

cmd="ImageMath $OriginalSeg -extractLabel 75 -outfile $BrainStemB"
eval $cmd

# Combine brain stem into one .nrrd 
cmd="ImageMath $BrainStemAll -combine $BrainStemA -outfile $BrainStemAll"
eval $cmd

cmd="ImageMath $BrainStemAll -combine $BrainStemB -outfile $BrainStemAll"
eval $cmd
echo $BrainStemB


# remove intermediate files
rm $BrainStemA
rm $BrainStemB

# move any previous files made to a new folder 
#tempDirOldProcessing="${OutFolder}/BrainStem_SingleGaussPre2020"
#cmd="mkdir $tempDirOldProcessing"
#eval $cmd

fi #if BrainStemAll doesn't exist 


# Binary Volume Segmentation Cleaning/Smoothing
# There is typically a hole in the brainstem. first perform a morphological closing of size 2 
cmd="ImageMath $BrainStemAll -outfile $BrainStemPostProcess1 -smooth -grayClose -size 2"
eval $cmd
# Run through the default SegPostProcessCLP with Gauss smoothing.  
cmd="SegPostProcessCLP $BrainStemPostProcess1 $BrainStemPostProcessFinal --space 0.75,0.75,0.75 --rescale --Gauss --verb"  
eval $cmd
 
# Surface Generation using SPHARM
# Parameterization
cmd="GenParaMeshCLP $BrainStemPostProcessFinal $BrainStemPara $BrainStemInitialSurf --verb"
eval $cmd

# Test to see if .para file was made
# if it was not exit with error 
if [ -f $BrainStemPara ]; then   
# Make Final SPHARMMesh
cmd="ParaToSPHARMMeshCLP $BrainStemPara $BrainStemInitialSurf $BrainStemSPHARM --subdivLevel 10 --spharmDegree 15"
eval $cmd

cmd="cp ${BrainStemSPHARM}SPHARM.vtk /NIRAL/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/SubCortical_Processing/CollectedBrainSPHARMBrainStems/${ID}_surfSPHARM.vtk"
eval $cmd
cmd="cp ${DATA_HOME}/${ID}/${ID}-${fterm2}.nrrd ${OutFolder}/${ID}-T1_SkullStripped_scaled.nrrd" 
eval $cmd 
echo "$BrainStemPara Found"
else
# count the failure 
let countFail++
echo "$ID FAILED BRAINSTEM PARAMETERIZATION!"  
echo ""$ID"" >> "FailedBrainstems_Close2Gauss__${studyYear}.txt"
fi 


done < $idfile
echo Number Failed: $countFail
