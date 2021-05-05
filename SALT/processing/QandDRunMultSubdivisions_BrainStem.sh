#!/bin/bash


# *****************************************
# RUN INPUT FOLDERS
# *****************************************
# Text File of Subject IDs To Run 
# **************************************

#idfile=$1

#while read idx
#do
# Project ID
#ID=$subject
	#idx=${idx//$'\n'/} 
	#ID=$idx
	ID="neo-0113-2-1year"
###############################################
#OUTPUT
###############################################
#OutFolder="${DATA_HOME}/${ID}/AutoSegTissue_1year_v2-MultiAtlas/SALT" 
OutFolder="/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/SubCortical_Processing/temp_BrainStemClosing/${ID}"

if [ ! -f $OutFolder ]; then  
cmd="mkdir $OutFolder"
eval $cmd
fi

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
levels=(31)
for i in "${levels[@]]}"; do 
#Note the SPHARM pipeline will add on the appropriate endings to deliniate the output .vtks
# the primary output of interest is ${BrainStemSPHARM}_SPHARM.vtk the final SPHARM mesh. 
BrainStemSPHARM="${OutFolder}/${ID}-T1_SkullStripped_scaled_label_Brainstem_ppFinal_surf_${i}"

# Make Final SPHARMMesh
cmd="ParaToSPHARMMeshCLP $BrainStemPara $BrainStemInitialSurf $BrainStemSPHARM --subdivLevel $i --spharmDegree 15"

eval $cmd
done

#done < $idfile

