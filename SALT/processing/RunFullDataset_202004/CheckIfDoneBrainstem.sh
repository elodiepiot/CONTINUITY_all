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
countFail=0 # some of the brain stem will not have spherical topology - establish a counter. 
idfile=$1
echo $idfile
while read idx
do
# Project ID
#ID=$subject
	#idx=${idx//$'\n'/} 
	ID=$idx
#echo $ID
	
	#echo Starting BrainStemExtraction: subject $ID
	#echo $DATA_HOME


###############################################
#OUTPUT
###############################################
OutFolder="${DATA_HOME}/${ID}/AutoSegTissue_1year_v2-MultiAtlas/SALT" 
#OutFolder="/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/SubCortical_Processing/temp_BrainStemClosing/${ID}"

#if [ ! -f $OutFolder ]; then  
#cmd="mkdir $OutFolder"
#eval $cmd
#fi
BrainStemAll="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem.nrrd"
#echo $BrainStemAll

BrainStemPara="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_ppFinal_para.vtk"
BrainStemInitialSurf="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_ppFinal_surf.vtk"

#Note the SPHARM pipeline will add on the appropriate endings to deliniate the output .vtks
# the primary output of interest is ${BrainStemSPHARM}_SPHARM.vtk the final SPHARM mesh. 
BrainStemSPHARM="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_ppFinal_surf"

# Log Files 
BrainStemLogGenPPFinal="${OutFolder}/BrainStemFinal_genparamesh.log"

#################################################




# Test to see if .para file was made
# if it was not exit with error 
if [ -f $BrainStemPara ]; then   
# Make Final SPHARMMesh

 
echo "$BrainStemPara Found"
else
# count the failure 
let countFail++
echo $countFail
echo "$ID FAILED BRAINSTEM PARAMETERIZATION!"  
echo ""$ID"" >> "FailedBrainstems_${studyYear}.txt"
fi 


done < $idfile
echo Number Failed: $countFail
