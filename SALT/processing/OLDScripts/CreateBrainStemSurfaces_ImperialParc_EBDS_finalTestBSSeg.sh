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
studyYear="Conte1_and_2Yr"
if [ $2 -eq 0 ] 
then
	# Conte 1 and 2 (option 0)
	DATA_HOME="/dichter/AutoSeg_Rerun_CONTE1and2/Data"
elif [ $2 -eq 1 ] 
then
	# Conte 4 and 6 (option 1)
	DATA_HOME="/Human/conte_
projects/CONTE_NEO/AUTOSEG_4-6year_T1andMultiAtlas/Data"
studyYear="Conte4_and_6Yr"
elif [ $2 -eq 2 ] 
then
	# Twin 1 and 2 (option 2)
	DATA_HOME="/Human2/CONTE2/TWINS-SubCort/Data"
	fterm="T1_regAtlas-SkullStripped_corrected_EMS--Imperial_Parc_SubCort_Extended-WarpReg_label_1.nrrd"
	studyYear="Twin1_and_2Yr"
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
	countFail=0 # some of the brain stem will not have spherical topology - establish a counter. 
	#echo Starting BrainStemExtraction: subject $ID
	#echo $DATA_HOME

	# INPUT
	OriginalSeg="${DATA_HOME}/${ID}/AutoSegTissue_1year_v2-MultiAtlas/WarpROI/${ID}-${fterm}"
	#echo $OriginalSeg 
#echo $ID
#echo $DATA_HOME

touch "FailedBrainstems_2GaussOperations_${studyYear}.txt"
###############################################
#OUTPUT
###############################################
OutFolder="${DATA_HOME}/${ID}/AutoSegTissue_1year_v2-MultiAtlas/SALT" 
#OutFolder="/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/SubCortical_Processing/temp/${ID}"

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
BrainStemPostProcess1="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_ppGauss1.nrrd"
BrainStemPostProcessFinal="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_ppGauss2.nrrd"

# SPHARM surfaces

BrainStemPara="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_ppGauss2_para.vtk"
BrainStemInitialSurf="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_ppGauss2_surf.vtk"

#Note the SPHARM pipeline will add on the appropriate endings to deliniate the output .vtks
# the primary output of interest is ${BrainStemSPHARM}_SPHARM.vtk the final SPHARM mesh. 
BrainStemSPHARM="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_ppGauss2_surf"

# Log Files 
BrainStemLogGenPPFinal="${OutFolder}/BrainStemGauss2_genparamesh.log"

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
cmd="SegPostProcessCLP $BrainStemAll $BrainStemPostProcess1 --space 0.75,0.75,0.75 --rescale --verb --Gauss"
eval $cmd
# peform again: as was having some problems morph operations were insufficient to ensure correct spherical topology 
cmd="SegPostProcessCLP $BrainStemPostProcess1 $BrainStemPostProcessFinal --space 0.75,0.75,0.75 --rescale --Gauss --verb"  
eval $cmd
 
# Surface Generation using SPHARM
# Parameterization
cmd="GenParaMeshCLP $BrainStemPostProcessFinal $BrainStemPara $BrainStemInitialSurf --verb >! $BrainStemLogGenPPFinal"
eval $cmd

# Test to see if .para file was made
# if it was not exit with error 
if [ -f $BrainStemPara ]; then   
# Make Final SPHARMMesh
cmd="ParaToSPHARMMeshCLP $BrainStemPara $BrainStemInitialSurf $BrainStemSPHARM --subdivLevel 10 --spharmDegree 15"
eval $cmd
echo "$BrainStemPara Found"
else
# count the failure 
let countFail++
echo "$ID FAILED BRAINSTEM PARAMETERIZATION!"  
echo ""$ID"" >> "FailedBrainstems_2GaussOperations_${studyYear}.txt"
fi 


done < $idfile
echo Number Failed: $countFail
