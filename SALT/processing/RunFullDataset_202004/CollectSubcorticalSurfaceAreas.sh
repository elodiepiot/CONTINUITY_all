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


# call matlab surfaceAreaCalcs.m input will be the data ID and the folder with the .txt files. 
matlab2014 -nodisplay -r "addpath('/NIRAL/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/SubCortical_Processing/SALT/processing/RunFullDataset_202004'); SurfaceAreaCalcs('"$1"','"$DATA_HOME"','"$3"','"$4"');"


exit

