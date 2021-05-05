#!/usr/bin/env python3
import argparse
import json
import os 
import sys 
import traceback
import shutil
import subprocess
import time
import datetime
from termcolor import colored
from vtk import *
import numpy as np

import dipy 
from dipy.core.gradients import gradient_table
from dipy.io.gradients import read_bvals_bvecs
from dipy.io.image import load_nifti, load_nifti_data

from dipy.reconst.csdeconv import (ConstrainedSphericalDeconvModel, auto_response_ssst)

from dipy.reconst.shm import CsaOdfModel
from dipy.data import (default_sphere, small_sphere )
from dipy.direction import peaks_from_model

from dipy.tracking.stopping_criterion import ThresholdStoppingCriterion

from dipy.direction import ProbabilisticDirectionGetter

from dipy.tracking.local_tracking import LocalTracking
from dipy.tracking.streamline import Streamlines

from dipy.io.stateful_tractogram import Space, StatefulTractogram
from dipy.io.streamline import save_trk


from CONTINUITY_functions import *

##########################################################################################################################################

    # CONTINUITY completed script for tractography

##########################################################################################################################################

# *****************************************
# Parameters
# *****************************************

parser = argparse.ArgumentParser(description='CONTINUITY script for tractography')
parser.add_argument("user_json_filename", help = "File with all parameters given by the user", type = str) 
args = parser.parse_args()

# Read json file
with open(args.user_json_filename, "r") as user_Qt_file:
    json_user_object = json.load(user_Qt_file)
'''
for categories, infos in json_user_object.items():
    for key in infos: 
        print(key, ": ", json_user_object[categories][key]["value"])
'''

# Parameters
noGUI                                   = str(json_user_object["Parameters"]["noGUI"]['value'])
cluster                                 = str(json_user_object["Parameters"]["cluster"]['value'])
cluster_command_line                    = str(json_user_object["Parameters"]["cluster_command_line"]['value'])
tractography_model                      = str(json_user_object["Parameters"]["tractography_model"]['value'])
filtering_with_tcksift					= str(json_user_object["Parameters"]["filtering_with_tcksift"]['value'])
optimisation_with_tcksift2				= str(json_user_object["Parameters"]["optimisation_with_tcksift2"]['value'])
act_option				                = str(json_user_object["Parameters"]["act_option"]['value'])
ID                                      = str(json_user_object["Parameters"]["ID"]['value'])
DWI_DATA                                = str(json_user_object["Parameters"]["DWI_DATA"]['value'])
T1_DATA                                 = str(json_user_object["Parameters"]["T1_DATA"]['value'])
T2_DATA                                 = str(json_user_object["Parameters"]["T2_DATA"]['value'])
BRAINMASK                               = str(json_user_object["Parameters"]["BRAINMASK"]['value'])
PARCELLATION_TABLE                      = str(json_user_object["Parameters"]["PARCELLATION_TABLE"]['value'])
UPSAMPLING_DWI                          = str(json_user_object["Parameters"]["UPSAMPLING_DWI"]['value'])
DO_REGISTRATION                         = str(json_user_object["Parameters"]["DO_REGISTRATION"]['value'])
INTEGRATE_SC_DATA                       = str(json_user_object["Parameters"]["INTEGRATE_SC_DATA"]['value'])
INTEGRATE_SC_DATA_by_generated_sc_surf  = str(json_user_object["Parameters"]["INTEGRATE_SC_DATA_by_generated_sc_surf"]['value'])
EXTRA_SURFACE_COLOR                     = str(json_user_object["Parameters"]["EXTRA_SURFACE_COLOR"]['value'])
labelSetName                            = str(json_user_object["Parameters"]["labelSetName"]['value'])
ignoreLabel                             = str(json_user_object["Parameters"]["ignoreLabel"]['value'])
WM_L_Surf                               = str(json_user_object["Parameters"]["WM_L_Surf"]['value'])
WM_R_Surf                               = str(json_user_object["Parameters"]["WM_R_Surf"]['value'])
left_right_surface_need_to_be_combining = str(json_user_object["Parameters"]["left_right_surface_need_to_be_combining"]['value'])
SURFACE_USER                            = str(json_user_object["Parameters"]["SURFACE_USER"]['value']),
WM_L_Surf_NON_REGISTRATION              = str(json_user_object["Parameters"]["WM_L_Surf_NON_REGISTRATION"]['value'])
WM_R_Surf_NON_REGISTRATION              = str(json_user_object["Parameters"]["WM_R_Surf_NON_REGISTRATION"]['value'])
SALTDir                                 = str(json_user_object["Parameters"]["SALTDir"]['value'])
subcorticalsList                        = str(json_user_object["Parameters"]["subcorticalsList"]['value'])
subcorticalsListNumber                  = str(json_user_object["Parameters"]["subcorticalsListNumber"]['value'])
labeled_image                           = str(json_user_object["Parameters"]["labeled_image"]['value'])
KWMDir                                  = str(json_user_object["Parameters"]["KWMDir"]['value'])
surface_already_labeled                 = str(json_user_object["Parameters"]["surface_already_labeled"]['value'])
cortical_label_left                     = str(json_user_object["Parameters"]["cortical_label_left"]['value'])
cortical_label_right                    = str(json_user_object["Parameters"]["cortical_label_right"]['value'])
first_fixed_img                         = str(json_user_object["Parameters"]["first_fixed_img"]['value'])
first_moving_img                        = str(json_user_object["Parameters"]["first_moving_img"]['value'])
second_fixed_img                        = str(json_user_object["Parameters"]["second_fixed_img"]['value'])
second_moving_img                       = str(json_user_object["Parameters"]["second_moving_img"]['value'])
first_metric_weight                     = str(json_user_object["Parameters"]["first_metric_weight"]['value'])
first_radius                            = str(json_user_object["Parameters"]["first_radius"]['value'])
second_metric_weight                    = str(json_user_object["Parameters"]["second_metric_weight"]['value'])
second_radius                           = str(json_user_object["Parameters"]["second_radius"]['value'])
deformation_field_sigma                 = str(json_user_object["Parameters"]["deformation_field_sigma"]['value'])
gradient_field_sigma                    = str(json_user_object["Parameters"]["gradient_field_sigma"]['value'])
SyN_param                               = str(json_user_object["Parameters"]["SyN_param"]['value'])
iteration1                              = str(json_user_object["Parameters"]["iteration1"]['value'])
iteration2                              = str(json_user_object["Parameters"]["iteration2"]['value'])
iteration3                              = str(json_user_object["Parameters"]["iteration3"]['value'])
nb_threads                              = str(json_user_object["Parameters"]["nb_threads"]['value'])
overlapping                             = str(json_user_object["Parameters"]["overlapping"]['value'])
nb_fibers                               = str(json_user_object["Parameters"]["nb_fibers"]['value'])
nb_fiber_per_seed                       = str(json_user_object["Parameters"]["nb_fiber_per_seed"]['value'])
steplength                              = str(json_user_object["Parameters"]["steplength"]['value'])
sampvox                                 = str(json_user_object["Parameters"]["sampvox"]['value'])
loopcheck                               = str(json_user_object["Parameters"]["loopcheck"]['value'])
OUT_PATH                                = str(json_user_object["Parameters"]["OUT_PATH"]['value'])

# Executables
pathUnu                   = str(json_user_object["Executables"]["unu"]['value'])
pathN4BiasFieldCorrection = str(json_user_object["Executables"]["N4BiasFieldCorrection"]['value'])
pathBRAINSFit_CMD         = str(json_user_object["Executables"]["BRAINSFit"]['value'])
pathdtiprocess            = str(json_user_object["Executables"]["dtiprocess"]['value'])
pathDtiestim              = str(json_user_object["Executables"]["dtiestim"]['value'])
pathANTS_CMD              = str(json_user_object["Executables"]["ANTS"]['value'])
pathITK_TRANSTOOL_EXE     = str(json_user_object["Executables"]["ITKTransformTools_v1"]['value'])
pathPOLY_TRANSTOOL_EXE    = str(json_user_object["Executables"]["polydatatransform_v1"]['value'])
pathWARP_TRANSFORM        = str(json_user_object["Executables"]["WarpImageMultiTransform"]['value'])
DWIConvertPath            = str(json_user_object["Executables"]["DWIConvert"]['value'])

FSLPath                   = str(json_user_object["Executables"]["fsl"]['value']) 
ExtractLabelSurfaces      = str(json_user_object["Executables"]["ExtractLabelSurfaces"]['value']) 

MRtrixPath                = str(json_user_object["Executables"]["MRtrix"]['value']) 

SegPostProcessCLPPath     = str(json_user_object["Executables"]["SegPostProcessCLP"]['value'])
GenParaMeshCLPPath        = str(json_user_object["Executables"]["GenParaMeshCLP"]['value']) 
ParaToSPHARMMeshCLPPath   = str(json_user_object["Executables"]["ParaToSPHARMMeshCLP"]['value']) 

writeSeedListScript       = "./writeSeedList.py" 


# data: /Human/twin-gilmore/AUTOSEG_4-6year_T1andMultiAtlas/Data/T0054-1-1-6yr/AutoSegTissue_1year_v2-MultiAtlas

# *****************************************
# Create folder and complete log file
# *****************************************

OUT_FOLDER = os.path.join(OUT_PATH,ID) #ID
if not os.path.exists( OUT_FOLDER ):
    os.mkdir(OUT_FOLDER)


# Log file:
log_file = os.path.join(OUT_FOLDER,"log.txt")

# Context manager that copies stdout and any exceptions to a log file
class Tee(object):
    def __init__(self, filename):
        self.file = open(filename, 'w')
        self.stdout = sys.stdout

    def __enter__(self):
        sys.stdout = self

    def __exit__(self, exc_type, exc_value, tb):
        sys.stdout = self.stdout
        if exc_type is not None:
            self.file.write(traceback.format_exc())
        self.file.close()

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    def flush(self):
        self.file.flush()
        self.stdout.flush()

with Tee(log_file):

	OUT_INPUT_CONTINUITY_DWISPACE = os.path.join(OUT_FOLDER,"Input_CONTINUITY_DWISpace") #ID --> Input_CONTINUITY_DWISpace
	if not os.path.exists( OUT_INPUT_CONTINUITY_DWISPACE ): os.mkdir(OUT_INPUT_CONTINUITY_DWISPACE)
	
	OUT_SALT = os.path.join(OUT_FOLDER, "Salt") #ID --> SALT
	if not os.path.exists(OUT_SALT): os.mkdir(OUT_SALT)

	OUT_T1TODWISPACE = os.path.join(OUT_FOLDER,"T1ToDWISpace") #ID --> T1ToDWISpace
	if not os.path.exists( OUT_T1TODWISPACE ): os.mkdir(OUT_T1TODWISPACE)

	OUT_00_QC_VISUALIZATION = os.path.join(OUT_T1TODWISPACE,"00_QC_Visualization") #ID --> T1ToDWISpace --> 00_QC_Visualization
	if not os.path.exists( OUT_00_QC_VISUALIZATION ): os.mkdir(OUT_00_QC_VISUALIZATION)

	OUT_INTERMEDIATEFILES = os.path.join(OUT_T1TODWISPACE,"IntermediateFiles") #ID --> T1ToDWISpace --> IntermediateFiles
	if not os.path.exists( OUT_INTERMEDIATEFILES ): os.mkdir(OUT_INTERMEDIATEFILES)

	OUT_DTI = os.path.join(OUT_INTERMEDIATEFILES,"DTI") #ID --> T1ToDWISpace --> IntermediateFiles --> DTI
	if not os.path.exists( OUT_DTI ): os.mkdir(OUT_DTI)
	
	OUT_SURFACE = os.path.join(OUT_DTI, "Surface") #ID --> T1ToDWISpace --> IntermediateFiles --> DTI --> Surface
	if not os.path.exists( OUT_SURFACE ): os.mkdir(OUT_SURFACE)

	OUT_WARPS = os.path.join(OUT_T1TODWISPACE, "Warps") #ID --> T1ToDWISpace --> WARP
	if not os.path.exists( OUT_WARPS ): os.mkdir(OUT_WARPS)

	OUT_INPUTDATA = os.path.join(OUT_FOLDER, "InputDataForSlicer") #ID --> INPUTDATA: for visualization
	if not os.path.exists( OUT_INPUTDATA ): os.mkdir(OUT_INPUTDATA)

	OUT_TRACTOGRAPHY = os.path.join(OUT_FOLDER, "Tractography") #ID --> Tractography
	if not os.path.exists(OUT_TRACTOGRAPHY): os.mkdir(OUT_TRACTOGRAPHY)

	OUT_DIFFUSION = os.path.join(OUT_TRACTOGRAPHY, "Diffusion") #ID --> Tractography --> Diffusion
	if not os.path.exists( OUT_DIFFUSION ): os.mkdir(OUT_DIFFUSION)


	# *****************************************
	# Function to run a specific command
	# *****************************************

	def run_command(text_printed, command):
		# Display command:
	    print(colored("\n"+" ".join(command)+"\n", 'blue'))
	    # Run command and display output and error:
	    run = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	    out, err = run.communicate()
	    print(text_printed, "out: ", colored("\n" + str(out) + "\n", 'green')) 
	    print(text_printed, "err: ", colored("\n" + str(err) + "\n", 'red'))



	# *****************************************
	# Function to convert inputs in nifti format to nrrd format 
	# *****************************************

	# Convert nifti input to nrrd:  
	for file in [T1_DATA, T2_DATA, DWI_DATA, BRAINMASK]:
		[path, afile] =os.path.split(file)
		print(path) #./input_CONTINUITY
		print(afile) #T0054-1-1-6yr-T1_SkullStripped_scaled.nrrd

		if afile.endswith('nii.gz'): 
			print("*****************************************")
			print("Convert FSL2Nrrd")
			print("*****************************************")

			new_name = afile[:-7] + '.nrrd'
			print(new_name)
			
			# New folder: 
			OUT_FOLDER_nifti2nrrd = os.path.join(OUT_FOLDER, 'nifti2nrrd') 
			if not os.path.exists(OUT_FOLDER_nifti2nrrd):
				os.mkdir(OUT_FOLDER_nifti2nrrd)

			output_nrrd = os.path.join(OUT_FOLDER_nifti2nrrd, new_name)
			print("TO DO ")
			inputBValues = ''
			inputBVectors = ''

			run_command("DWIConvert: convert input image in nifti format to nrrd format", [DWIConvertPath, "--inputVolume", file, 
															                             "--conversionMode", "FSLToNrrd", 
															                             "--outputVolume", output_nrrd, 
															                             "--inputBValues",inputBValues, 
															                             "--inputBVectors",inputBVectors])
			# New path :
			file = output_nrrd
			


	########################################################################
	'''   
	    CONTINUITY script 1: Prepare files for T1 to DWISpace Registration

	 1- Pre-registration: (Up)sampled DWI, DWI BrainMask (upsample data is an option) using UNU
	 2- Preparing files for registration: 
	    - B0/DTI Image Generation: calculate the (up)sampled/masked DTI and the B0 directly from the (up)sampled DWI. Get the masked B0 and DTI image using dtiest. 
	    - B0 Bias Corrected Image generation: bias Correct the B0 Image to match the T2 Bias Corrected Image using N4BiasFieldCorrection
	    - FA generation using DTI process

	(from the script of Maria Bagonis (Nov 2019) 
	'''
	########################################################################

	print("**********************************************************************************")
	print("Script 1: prepare files for T1 to DWI space registration")
	print("**********************************************************************************")

	if DO_REGISTRATION.lower() == "true":
		print("Starting Pre-registration: (Up)sampled DWI, DWI BrainMask, T1 DWISpace, DWISpace T1 surfaces")

		# Create different names for DWI_NRRD and DWI_MASK according to the value of UPSAMPLING_DWI and find the position of the gradient 
		if UPSAMPLING_DWI:
		    DWI_NRRD = os.path.join(OUT_INPUT_CONTINUITY_DWISPACE, ID + "_DWI_resample.nrrd")
		    DWI_MASK = os.path.join(OUT_INPUT_CONTINUITY_DWISPACE, ID + "_Original_DWI_BrainMask_resample.nrrd")

		    # Check the header file (line “kinds”) to verify if gradient is the first dimension or the last dimension of data → change unu resample option
		    command = [pathUnu, "head", DWI_DATA]   # NOT use run_command function because I use 'out' after
		    print(colored("\n"+" ".join(command)+"\n", 'blue'))
		    run = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		    out, err = run.communicate()
		    print("Unu check header, out: ", colored("\n" + str(out) + "\n", 'green')) 
		    print("Unu check header, err: ", colored("\n" + str(err) + "\n", 'red'))
	
		    for i in out.splitlines():
		        section = i.split()
		        if "b'kinds:" in str(section):
		            grad_first = 'False'               # Case: [b'kinds:', b'domain', b'domain', b'domain', b'vector'] --> gradient in last position
		            if "b'vector" in str(section[1]):  # Case: [b'kinds:', b'vector', b'domain', b'domain', b'domain'] --> gradient in first position
		                grad_first = 'True'                
		else:
		    DWI_NRRD = os.path.join(OUT_INPUT_CONTINUITY_DWISPACE, ID + "_DWI_original.nrrd")
		    DWI_MASK = os.path.join(OUT_INPUT_CONTINUITY_DWISPACE, ID + "_Original_DWI_BrainMask_original.nrrd")



		# Interpolation / upsampling DWI
		if os.path.exists( DWI_NRRD ):
		    print("Files Found: Skipping Upsampling DWI")
		elif UPSAMPLING_DWI:
			print("*****************************************")
			print("Upsampling DWI")
			print("*****************************************")

			command = [pathUnu, "resample", "-i", DWI_DATA, "-s", "x2", "x2", "x2", "=", "-k", "cubic:0,0.5"]
			if grad_first: 
				command = [pathUnu, "resample", "-i", DWI_DATA, "-s", "=", "x2", "x2", "x2", "-k", "cubic:0,0.5"]       
			p1 = subprocess.Popen(command, stdout=subprocess.PIPE)

			command = [pathUnu,"3op", "clamp", "0",'-', "10000000"]
			p2 = subprocess.Popen(command, stdin=p1.stdout, stdout=subprocess.PIPE)

			command = [pathUnu,"save", "-e", "gzip", "-f", "nrrd", "-o", DWI_NRRD]
			p3 = subprocess.Popen(command,stdin=p2.stdout, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			print( colored("\n"+" ".join(command)+"\n", 'blue'))
			out, err = p3.communicate()
			print("Resample DWI out: ", colored("\n" + str(out) + "\n", 'green'))
			print("Resample DWI err: ", colored("\n" + str(err) + "\n", 'red')) 

		else: # no Upsampling DWI
			command = [pathUnu,"3op", "clamp", 0,'-', 10000000]
			p2 = subprocess.Popen(command, stdin= DWI_DATA, stdout=subprocess.PIPE)

			command = [pathUnu,"save", "-e", "gzip", "-f", "nrrd", "-o", DWI_NRRD]
			p3 = subprocess.Popen(command,stdin=p2.stdout, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			print( colored("\n"+" ".join(command)+"\n", 'blue'))
			out, err = p3.communicate()
			print("No resample DWI out: ", colored("\n" + str(out) + "\n", 'green'))
			print("No resample DWI err: ", colored("\n" + str(err) + "\n", 'red'))     
		   


		# Interpolation / upsampling DWI MASK
		if os.path.exists( DWI_MASK ):
		    print("Files Found: Skipping Upsampling DWIMask")
		elif UPSAMPLING_DWI:
			print("*****************************************")
			print("Upsampling DWI MASK")
			print("*****************************************")

			command = [pathUnu, "resample", "-i", BRAINMASK, "-s", "x2", "x2", "x2", "-k", "cheap"]
			p1 = subprocess.Popen(command, stdout=subprocess.PIPE)

			command = [pathUnu,"save", "-e", "gzip", "-f", "nrrd", "-o", DWI_MASK]
			p2 = subprocess.Popen(command,stdin=p1.stdout, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			print( colored("\n"+" ".join(command)+"\n", 'blue'))
			out, err = p2.communicate()
			print("Pipe resample DWI Mask out: ", colored("\n" + str(out) + "\n", 'green'))
			print("Pipe resample DWI Mask err: ", colored("\n" + str(err) + "\n", 'red')) 

		else: # no Upsampling DWI
		    command = [pathUnu,"save", "-e", "gzip", "-f", "nrrd", "-o", DWI_MASK]
		    p2 = subprocess.Popen(command,stdin= BRAINMASK, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		    print( colored("\n"+" ".join(command)+"\n", 'blue'))
		    out, err = p2.communicate()
		    print("Pipe no resample DWI_Mask out: ", colored("\n" + str(out) + "\n", 'green'))
		    print("Pipe no resample DWI_Mask err: ", colored("\n" + str(err) + "\n", 'red')) 


		print("*****************************************")
		print("Preparing files for registration")
		print("*****************************************")

		# Create different name according to upsampling parameter:
		if UPSAMPLING_DWI:
		    B0_NRRD             = os.path.join(OUT_00_QC_VISUALIZATION, ID + "_DTI_B0_resample.nrrd")
		    A0_NRRD             = os.path.join(OUT_00_QC_VISUALIZATION, ID + "_DTI_A0_resample.nrrd")
		    DTI_NRRD            = os.path.join(OUT_DTI, ID + "_DTI_DTI_resample.nrrd")
		    IDWI_NRRD           = os.path.join(OUT_DTI, ID + "_DTI_IDTI_resample.nrrd")
		    B0_BiasCorrect_NRRD = os.path.join(OUT_DTI, ID + "_DTI_B0_BiasCorrect_resample.nrrd")
		    FA_NRRD             = os.path.join(OUT_DTI, ID + "_DTI_FA_resample.nrrd")
		else:
		    B0_NRRD             = os.path.join(OUT_00_QC_VISUALIZATION, ID + "_DTI_B0_original.nrrd")
		    A0_NRRD             = os.path.join(OUT_00_QC_VISUALIZATION, ID + "_DTI_A0_original.nrrd")
		    DTI_NRRD            = os.path.join(OUT_DTI, ID + "_DTI_DTI_original.nrrd")
		    IDWI_NRRD           = os.path.join(OUT_DTI, ID + "_DTI_IDTI_original.nrrd")
		    B0_BiasCorrect_NRRD = os.path.join(OUT_DTI, ID + "_DTI_B0_BiasCorrect_original.nrrd")
		    FA_NRRD             = os.path.join(OUT_DTI, ID + "_DTI_FA_original.nrrd")


		# Calculate the (up)sampled/masked DTI and the B0 directly from the (up)sampled DWI. Get the masked B0 and DTI image using dtiest
		if os.path.exists( B0_NRRD ):
		    print("Files Found: Skipping B0/DTI Image Generation")
		else:
		    # Estimate tensor in a set of DWIs     
		    run_command("Dtiestim BO/DTI Image generation", [pathDtiestim, "--dwi_image", DWI_NRRD, 
		                                                                   "-M", DWI_MASK, 
		                                                                   "-t", '0', #threshold: -t 0 turns off the automatic masking performed in dtiestim
		                                                                   "--B0", B0_NRRD, #output: average baseline image (–B0) which is the average of all the B0s
		                                                                   "--tensor_output", DTI_NRRD, #output
												                           "-m", "wls",  #method: weighted least squares    
												                           "--idwi", IDWI_NRRD, #output:  geometric mean of the diffusion images.
												                           "--correction nearest"])
		    # Add BO_NRRD in INPUTDATA folder for visualization 
		    shutil.copy(B0_NRRD, OUT_INPUTDATA) 


		# Bias Correct the B0 Image to match the T2 Bias Corrected Image: bias correction algorithm    
		if os.path.exists( B0_BiasCorrect_NRRD ):
		    print("B0 Bias Corrected Image Found: Skipping Correction")
		else:
			print("*****************************************")
			print("Bias Correct the B0 Image to match the T2 Bias Corrected Image")
			print("*****************************************")

			run_command("N4BiasFieldCorrection: BO Bias corrected image", [pathN4BiasFieldCorrection, "-d", "3", "-i", B0_NRRD, "-o", B0_BiasCorrect_NRRD])

			# Add B0_BiasCorrect_NRRD in INPUTDATA folder for visualization 
			shutil.copy(B0_BiasCorrect_NRRD, OUT_INPUTDATA) 
		    

		# FA generation using DTI process
		if os.path.exists( FA_NRRD ):
		    print("FA Image Found: Skipping FA Generation from DTI")
		else:
			print("*****************************************")
			print("FA generation using DTI process")      
			print("*****************************************")#                                            ,    FA output , max eigenvalue output
			run_command("Dtiprocess: FA generation from DTI", [pathdtiprocess, "--inputDTIVolume", DTI_NRRD, "-f", FA_NRRD, "--lambda1_output", A0_NRRD])

			# Add FA_NRRD and A0_NRRD in INPUTDATA folder for visualization 
			shutil.copy(FA_NRRD, OUT_INPUTDATA) 
			shutil.copy(A0_NRRD, OUT_INPUTDATA) 



		########################################################################
		'''  
		    CONTINUITY script 2: Register T1 surfaces to DWI space: This script continues to prepare T1 surfaces registration to DWI space
	
		 1- T1 resample in DWI space: - Get a rigid transformation using BrainsFits for the initialization of the affine transform in ANTS
				                      - Perform the Deformable Registration using ANTS (35min)
		 		                      - Make invert matrix and T1 resample in DWI space using WARP_TRANSFORM and ITK_TRANSTOOL_EXE
		 2- Concatenate InvertWarp and InvertAffine transformations using ITK_TRANSTOOL_EXE
		 3- Transform surface (left and right) with InvWarp using POLY_TRANSTOOL_EXE

		(from the script of Maria Bagonis (Nov 2019) 
		'''
		########################################################################

		print("**********************************************************************************")
		print("Script 2: register T1 surfaces to DWI space")
		print("**********************************************************************************")

		#*****************************************
		# OUTPUT 
		#*****************************************

		outWarpPrefix = os.path.join(OUT_WARPS,ID + "_")
		outRigidReg   = os.path.join(OUT_WARPS,"RegRigid.txt")
		T1_OUT_NRRD   = os.path.join(OUT_00_QC_VISUALIZATION, ID + "_T1_SkullStripped_scaled_DWISpace.nrrd")
		INVAffine = os.path.join(OUT_WARPS, ID + "_InvAffine.txt") # output of ITK

		# Outputs of ANTs command:
		Affine    = os.path.join(OUT_WARPS, ID + "_Affine.txt")
		INVWarp   = os.path.join(OUT_WARPS, ID + "_InverseWarp.nii.gz")
		Warp      = os.path.join(OUT_WARPS, ID + "_Warp.nii.gz")


		if os.path.exists(Warp):
			print("ANTS File Found Skipping")
		else:
			moving_volume_ANTS = "T2_DATA"
			if T2_DATA == "": # just T1 data
			    moving_volume_ANTS = "T1_DATA"	

			print("*****************************************")
			print("Get a rigid transformation")
			print("*****************************************")

			# Get a rigid transformation using BrainsFits for the initialization of the affine transform in ANTS (register a 3D image to a reference volume)
			run_command("BRAINSFit", [pathBRAINSFit_CMD, "--fixedVolume", B0_BiasCorrect_NRRD, 
			                                             "--movingVolume", eval(moving_volume_ANTS), 
			                                             "--useRigid", "--initializeTransformMode", "useCenterOfHeadAlign", 
			                                             "--outputTransform", outRigidReg])


			print("*****************************************")
			print("Start ANTs command (~30 min with 1 core)")
			print("*****************************************")

			now = datetime.datetime.now()
			print(now.strftime("Script running ANTs command since: %H:%M %m-%d-%Y"))
			start = time.time()

			# Perform the Deformable Registration using ANTS
			# The T1 to DWI Space WARP(displacement field).nrrd is the output of the ANTS registration of the T1 Image to the DWI
			# Radius of the region = number of layers around a voxel/pixel
			command = [pathANTS_CMD, "3", "-m", "CC[", eval(first_fixed_img), ",", eval(first_moving_img), ",", first_metric_weight, ",", first_radius,"]",
			                              "-m", "CC[", eval(second_fixed_img),",", eval(second_moving_img),",", second_metric_weight,",", second_radius,"]",
			                              "-r", "Gauss[",gradient_field_sigma,",",deformation_field_sigma,"]", 
			                              "-i", iteration1, "x", iteration2, "x", iteration3, 
			                              "-t", "SyN[",SyN_param,"]",
			                              "-o", outWarpPrefix, 
			                              "--initial-affine", outRigidReg, 
			                              "--use-all-metrics-for-convergence",
			                              "num_threads", nb_threads, 
			                              "--verbose", "true"] 
			if T2_DATA == "": # just T1 data
				command = [pathANTS_CMD, "3", "-m", "CC[", eval(first_fixed_img),",",eval(first_moving_img),",",first_metric_weight,",",first_radius,"]",
				                              "-r", "Gauss[",gradient_field_sigma,",",deformation_field_sigma,"]", 
				                              "-i", iteration1, "x", iteration2, "x", iteration3, 
				                              "-t", "SyN[",SyN_param,"]",
				                              "-o", outWarpPrefix, 
				                              "--initial-affine", outRigidReg, 
				                              "--use-all-metrics-for-convergence",
				                              "num_threads", nb_threads, 
				                              "--verbose", "true"]
			run_command("ANTs command", command)
			print("ANTs command: ",time.strftime("%H h: %M min: %S s",time.gmtime( time.time() - start )))



			print("*****************************************")
			print("T1 resample in DWI space")
			print("*****************************************")

			# Warp an image (T1_DATA) from one space (B0_BiasCorrect_NRRD) to one other space (T1_OUT_NRRD)    3,moving img,output img,reference img           
			run_command("WARP_TRANSFORM: T1 resample in DWI space", [pathWARP_TRANSFORM, "3", T1_DATA, T1_OUT_NRRD, "-R", B0_BiasCorrect_NRRD, Warp, Affine])
			
			# Add T1_OUT_NRRD in INPUTDATA folder for visualization 
			shutil.copy(T1_OUT_NRRD, OUT_INPUTDATA)



			print("*****************************************")
			print("Make invert matrix")	   
			print("*****************************************")
			                                                # 		                                input  output
			run_command("ITK_TRANSTOOL_EXE: Make invert matrix", [pathITK_TRANSTOOL_EXE, "invert", Affine,INVAffine])


		print("*****************************************")
		print("Concatenate InvertWarp and InvertAffine")
		print("*****************************************")

		ConcatedWarp = os.path.join(OUT_WARPS, ID + "_ConcatenatedInvWarp.nrrd")
		if os.path.exists(ConcatedWarp):
			print("ConcatedWarp File Found Skipping")
		else:	                                                         #outputTransform ,Ref img       , input (INVWarp link with displacement)
			run_command("Concatenate", [pathITK_TRANSTOOL_EXE, "concatenate", ConcatedWarp, "-r", T1_DATA, INVAffine, INVWarp, "displacement"])


		print("*****************************************")
		print("Transform surface with InvWarp")
		print("*****************************************")

		# Output of the next functions: 
		RSL_WM_L_Surf = os.path.join(OUT_00_QC_VISUALIZATION, "stx_" + ID + 
		                                        "-T1_SkullStripped_scaled_BiasCorr_corrected_multi_atlas_white_surface_rsl_left_327680_native_DWIspace.vtk")
		RSL_WM_R_Surf = os.path.join(OUT_00_QC_VISUALIZATION, "stx_" + ID + 
		                                        "-T1_SkullStripped_scaled_BiasCorr_corrected_multi_atlas_white_surface_rsl_right_327680_native_DWIspace.vtk")
		if os.path.exists(RSL_WM_L_Surf):
			print("RSL_WM_L_Surf File Found Skipping")
		else:                               #, landmark file,input      , displacement file
			command = [pathPOLY_TRANSTOOL_EXE, "--fiber_file", WM_L_Surf, "-D", ConcatedWarp, "-o", RSL_WM_L_Surf, "--inverty", "--invertx"]
			run_command("POLY_TRANSTOOL_EXE: Transform WM left surface with InvWarp", command)
		
		if os.path.exists(RSL_WM_R_Surf):
			print("RSL_WM_R_Surf File Found Skipping")
		else:
			command = [pathPOLY_TRANSTOOL_EXE, "--fiber_file", WM_R_Surf, "-D", ConcatedWarp, "-o", RSL_WM_R_Surf, "--inverty", "--invertx"]
			run_command("POLY_TRANSTOOL_EXE: Transform WM right surface with InvWarp", command)		

		# Add T1_OUT_NRRD in INPUTDATA folder for visualization 
		shutil.copy(RSL_WM_L_Surf, OUT_INPUTDATA)	
		shutil.copy(RSL_WM_R_Surf, OUT_INPUTDATA)	
       








	########################################################################
	'''
		CONTINUITY script 3:
	
	A-If the user want to integrate subcortical data:
	 	0- Validation of subcortical region list
		1- Apply label: for each sc region label the SALT file with the Atlas label value (Create SPHARM surface labeled with the new atlas label)
		2- Combine the labeled subcorticals using polydatamerge
		3- Create Subcortical.vtk: move combining subcortical surface into DWISpace using POLY_TRANSTOOL_EXE- 
    B- labelization of cortical surfaces		 
	C- Create Cortical.vtk: combine left and right surface (in structural space if Not Registration, in DWI space if Registration) using polydatamerge
	D- If the user want to integrate subcortical data: Combine Subcortical.vtk with Cortical.vtk using polydatamerge

	(from the script of Maria Bagonis (Nov 2019)
	'''
	########################################################################

	print("**********************************************************************************")
	print("Script 3: Label_Combine_WARPtoDWISpace_SALTSubcort")
	print("**********************************************************************************")

	NAME_PARCELLATION_TABLE = labelSetName

	# *****************************************
	# OUTPUT
	# *****************************************

	OUT_LABELS = os.path.join(OUT_SALT, "Labels_" + NAME_PARCELLATION_TABLE)
	if not os.path.exists(OUT_LABELS):
		os.mkdir(OUT_LABELS)


	if INTEGRATE_SC_DATA.lower() == "true":  
		print("*****************************************")
		print("Integration of subcortical data ")
		print("*****************************************")


		if INTEGRATE_SC_DATA_by_generated_sc_surf.lower() == 'true':

			print("*****************************************")
			print("Generation of subcortical surfaces (~30 min )")
			print("*****************************************")
			
			now = datetime.datetime.now()
			print (now.strftime("Generation of subcortical surfaces: %H:%M %m-%d-%Y"))
			start = time.time()

			Labels     = list(subcorticalsListNumber.split(" ")) # [1, 2, 3, 4, 5, 6, 40, 41, 7, 8, 9, 10]
			LabelNames = list(subcorticalsList.split(" ")) # ['AmyL', 'AmyR', 'CaudL', 'CaudR', 'HippoL', 'HippoR', 'ThalL', 'ThalR', 'GPL', 'GPR', 'PutL', 'PutR']

			# Generate subcortical surfaces: 
			generating_subcortical_surfaces(OUT_FOLDER, ID, labeled_image, Labels, LabelNames, SegPostProcessCLPPath, GenParaMeshCLPPath, ParaToSPHARMMeshCLPPath)
			print("Generation of subcortical surfaces: ",time.strftime("%H h: %M min: %S s",time.gmtime(time.time() - start)))

			# Update the localization of subcortical surfaces: 
			SALTDir = os.path.join(OUT_FOLDER, 'my_SALT') 



		subcorticals = subcorticalsList.split() 

		# Copy to have only regions with good KWM and SALT files
		subcorticals_list_checked = subcorticalsList

		# Copy the original parcellation table to be able to build an other specific with only good subcortical regions ( = with good KWM and SALT files)
		new_parcellation_table = os.path.join(OUT_TRACTOGRAPHY, 'new_parcellation_table' )
		shutil.copy(PARCELLATION_TABLE, new_parcellation_table)

		# Check if all elements in subcorticalsList are referenced in the parcellation table with subcortical data:
		for region in subcorticals:  # "AmyL AmyR CaudL CaudR GPL GPR HippoL HippoR PutL PutR ThalL ThalR Brainstem"  
			#Open parcellation table file with subcortical regions:
			with open(new_parcellation_table) as data_file:    
				data = json.load(data_file)

			data_region_find = 'False' 
			for seed in data:
				for name in str(seed['name']).split("_"): # ctx _ rh _ S _ temporal _ sup    OR    sub_rh_thal	
	
					if region[-1].lower() == "l" or region[-1].lower() == 'r':
						if name.lower() == region[:-1].lower():
							data_region_find = 'True'
					else: #brainstem
						if name.lower() == region.lower():
								data_region_find = 'True'

			# After check all the json file: 
			if data_region_find == 'False':
				print(" NO information about ", region, "in your parcellation table with subcortical data")
				subcorticals_list_checked = subcorticals_list_checked.remove(region)
				


		print("*****************************************")
		print("Apply label after validation of subcortical region")
		print("*****************************************")

		# Only region with info in parcellation table
		subcorticals_list_checked = subcorticals_list_checked.split() 
		subcorticals_list_checked_with_surfaces = []

		# For each region label the SALT file with the Atlas label value. Create SPHARM surface labeled with the new atlas label. 
		for region in subcorticals_list_checked:
			#​The KWM files are intermediate .txt files for labeling the vertices on the respective subcortical SPHARM surfaces with a parcellation specific label number.
			KWMFile = os.path.join(KWMDir,region + "_1002_KWM.txt")
			SPHARMSurf = os.path.join(SALTDir, ID + "-T1_SkullStripped_scaled_label_" + region + "_pp_surfSPHARM.vtk")

			if not os.path.exists(SPHARMSurf) or not os.path.exists(KWMFile) : 
				SPHARMSurf = os.path.join(SALTDir, ID + "-T1_SkullStripped_scaled_label_" + region +"_ppManualFix_surfSPHARM.vtk")
				print(SPHARMSurf,file=open( os.path.join(OUT_LABELS,"manualFixes.txt"),"a"))

				# Delete info of this region in the new-parcellation-table:
				with open(new_parcellation_table, 'r') as data_file:
				    data = json.load(data_file)

				for i in range(len(data)):
					if data[i]['name'] == region: 
						data.pop(i)
						break

				with open(new_parcellation_table, 'w') as data_file:
					data = json.dump(data, data_file, indent = 2)

			else: 
				subcorticals_list_checked_with_surfaces.append(region)


			# Create SPHARM surface labeled: 
			SPHARMSurfL = os.path.join(OUT_LABELS, ID + "-T1_SkullStripped_scaled_label_" + region +"_pp_SPHARM_labeled.vtk")

			if os.path.exists(SPHARMSurfL):
				print("For", region, "region: SPHARM surface labeled file: Found Skipping Labeling")
			else: 
				print("For", region, "region: creation SPHARM surface labeled file")
			    # Applies the label in the KWM file to the SPHARM surface: 
				KWMtoPolyData(SPHARMSurf, SPHARMSurfL, KWMFile, NAME_PARCELLATION_TABLE)



		print("*****************************************")
		print("Combine the labeled subcorticals")
		print("*****************************************")

		outputSurface = os.path.join(OUT_LABELS, ID + "-" + NAME_PARCELLATION_TABLE + "_Labeled_Subcorticals_Combined_T1Space.vtk")

		
		if NAME_PARCELLATION_TABLE == 'Destrieux': 
			print("*****************************************")
			print("Compute one point per region")
			print("*****************************************")

			compute_point_destrieux(new_parcellation_table, subcorticals_list_checked_with_surfaces, KWMDir, SALTDir, ID )
		


		if os.path.exists( outputSurface ):
			print("OutputSurface file found: Skipping combine the labeled subcorticals ")
		else:
			# Add the first 2 subcortical regions to create an initial output file
			s1=os.path.join(OUT_LABELS, ID + "-T1_SkullStripped_scaled_label_" + subcorticals_list_checked[0] + "_pp_SPHARM_labeled.vtk")
			s2=os.path.join(OUT_LABELS, ID + "-T1_SkullStripped_scaled_label_" + subcorticals_list_checked[1] + "_pp_SPHARM_labeled.vtk") 

            # Combine the labeled subcorticals 
			print("For ", subcorticals_list_checked[0], "region: ") 
			polydatamerge(s1, s2, outputSurface)

			# Add other regions 
			for i in range(2,len(subcorticals_list_checked)):
				toAdd = os.path.join(OUT_LABELS, ID + "-T1_SkullStripped_scaled_label_" + subcorticals_list_checked[i] + "_pp_SPHARM_labeled.vtk")

				# Combine the labeled subcorticals 
				print("For ", subcorticals_list_checked[i], "region: ")
				polydatamerge(outputSurface, toAdd, outputSurface)


		print("Move combining subcortical surfaces in DWISpace")
		subsAllDWISpace = os.path.join(OUT_SURFACE, "stx_" + ID + "_" + NAME_PARCELLATION_TABLE + "_Labeled_Subcorticals_Combined_DWISpace.vtk" ) 

		if os.path.exists(subsAllDWISpace):
			print("Labeled subcorticals combined DWISpace file: Found Skipping Transformation into DWISpace")
		else: 
			# Transform a PolyData with a displacement field: apply T1 to DWI WARP (ie displacement field)
			#                              , landmark file ,input        , displacement file       , output in DWI space
			command=[pathPOLY_TRANSTOOL_EXE, "--fiber_file",outputSurface, "-D", ConcatedWarp, "-o", subsAllDWISpace, "--inverty", "--invertx"]
			run_command("POLY_TRANSTOOL_EXE: combining sc data transform into DWISpace", command)



	print("*****************************************")
	print("Labelization of the cortical surfaces ")
	print("*****************************************")

	if surface_already_labeled.lower() == "false":

		if DO_REGISTRATION.lower() == "false":
			# Outputs:
			RSL_WM_L_Surf_NON_REGISTRATION_labeled = os.path.join(OUT_00_QC_VISUALIZATION, "stx_" + ID + 
			            "-T1_SkullStripped_scaled_BiasCorr_corrected_multi_atlas_white_surface_rsl_left_327680_native_DWIspace_labeled_" + NAME_PARCELLATION_TABLE + ".vtk")
			RSL_WM_R_Surf_NON_REGISTRATION_labeled = os.path.join(OUT_00_QC_VISUALIZATION, "stx_" + ID + 
			            "-T1_SkullStripped_scaled_BiasCorr_corrected_multi_atlas_white_surface_rsl_right_327680_native_DWIspace_labeled_" + NAME_PARCELLATION_TABLE + ".vtk")
		
			print("NON_REGISTRATION: Label the left cortical surface")
			if os.path.exists( RSL_WM_L_Surf_NON_REGISTRATION_labeled ):
				print("NON_REGISTRATION: WM left labeled file found: Skipping Labelization of the left cortical surfaces")
			else:
				KWMtoPolyData(RSL_WM_L_Surf_NON_REGISTRATION, RSL_WM_L_Surf_NON_REGISTRATION_labeled, cortical_label_left, NAME_PARCELLATION_TABLE)  
				 

			print("NON_REGISTRATION: Label the right cortical surface")
			if os.path.exists( RSL_WM_R_Surf_NON_REGISTRATION_labeled ):
				print("NON_REGISTRATION: WM right labeled file found: Skipping Labelization of the right cortical surfaces")
			else:
				KWMtoPolyData(RSL_WM_R_Surf_NON_REGISTRATION, RSL_WM_R_Surf_NON_REGISTRATION_labeled, cortical_label_right, NAME_PARCELLATION_TABLE)  		


		else: #DO_REGISTRATION.lower() == "true":
			# Outputs:
			RSL_WM_L_Surf_labeled = os.path.join(OUT_00_QC_VISUALIZATION, "stx_" + ID + 
			           "-T1_SkullStripped_scaled_BiasCorr_corrected_multi_atlas_white_surface_rsl_left_327680_native_DWIspace_labeled_" + NAME_PARCELLATION_TABLE + ".vtk")
			RSL_WM_R_Surf_labeled = os.path.join(OUT_00_QC_VISUALIZATION, "stx_" + ID + 
			           "-T1_SkullStripped_scaled_BiasCorr_corrected_multi_atlas_white_surface_rsl_right_327680_native_DWIspace_labeled_" + NAME_PARCELLATION_TABLE + ".vtk")
			
			print("Label the left cortical surface")
			if os.path.exists( RSL_WM_L_Surf_labeled ):
				print("WM left labeled file found: Skipping Labelization of the left cortical surfaces")
			else:
				KWMtoPolyData(RSL_WM_L_Surf, RSL_WM_L_Surf_labeled, cortical_label_left, NAME_PARCELLATION_TABLE)  
				 
			print("Label the right cortical surface")
			if os.path.exists( RSL_WM_R_Surf_labeled ):
				print("WM right labeled file found: Skipping Labelization of the right cortical surfaces")
			else:
				KWMtoPolyData(RSL_WM_R_Surf, RSL_WM_R_Surf_labeled, cortical_label_right, NAME_PARCELLATION_TABLE)  

			# Add SURFACE in INPUTDATA folder for visualization 
			shutil.copy(RSL_WM_L_Surf_labeled, OUT_INPUTDATA)
			shutil.copy(RSL_WM_R_Surf_labeled, OUT_INPUTDATA)


	else: #surfaces already labeled
		if DO_REGISTRATION.lower() == "false":
			RSL_WM_L_Surf_NON_REGISTRATION_labeled = RSL_WM_L_Surf_NON_REGISTRATION
			RSL_WM_R_Surf_NON_REGISTRATION_labeled = RSL_WM_R_Surf_NON_REGISTRATION

		else: 
			RSL_WM_L_Surf_labeled = RSL_WM_L_Surf
			RSL_WM_R_Surf_labeled = RSL_WM_R_Surf

			# Add SURFACE in INPUTDATA folder for visualization 
			shutil.copy(RSL_WM_L_Surf_labeled, OUT_INPUTDATA)
			shutil.copy(RSL_WM_R_Surf_labeled, OUT_INPUTDATA)



	print("*****************************************")
	print("Start: Combine left and right surface in structural and DWI space (do or not do registration) ")
	print("*****************************************")

	# Create cortical.vtk: 
	SURFACE = os.path.join(OUT_SURFACE, "stx_" + ID + "_T1_CombinedSurface_white_" + NAME_PARCELLATION_TABLE + ".vtk")

	if DO_REGISTRATION.lower() == "false":
		if os.path.exists(SURFACE):
			print("NOT REGISTRATION: Combine cortical file: Found Skipping combining cortical left and right surface ")
		else: 
			if left_right_surface_need_to_be_combining.lower() == "true":
				# NOT REGISTRATION: combine left and right surface 
				polydatamerge(WM_L_Surf_NON_REGISTRATION_labeled, WM_R_Surf_NON_REGISTRATION_labeled, SURFACE)
			else:
				shutil.copy(SURFACE_USER, SURFACE)
				SURFACE = SURFACE_USER
	else: 
		if os.path.exists(SURFACE):
			print("Combine cortical file: Found Skipping combining cortical left and right surface ")
		else: 
			# Combine left+right surface 
			polydatamerge(RSL_WM_L_Surf_labeled, RSL_WM_R_Surf_labeled, SURFACE)

	# Add SURFACE in INPUTDATA folder for visualization 
	shutil.copy(SURFACE, OUT_INPUTDATA)



	if INTEGRATE_SC_DATA.lower() == "true": 
		print("*****************************************")
		print("Start the integration of subcortical data: Combine subcortical with cortical vtk file in DWI Space of choice (Destrieux, AAL, etc)")
		print("*****************************************")

		# Output of the next command: 
		outputSurfaceFullMerge = os.path.join(OUT_INPUT_CONTINUITY_DWISPACE, "stx_" + ID + "_T1_CombinedSurface_white_" + NAME_PARCELLATION_TABLE + 
			                                                                                                                       "_WithSubcorticals.vtk") 
		if os.path.exists(outputSurfaceFullMerge):
			print("Combine cortical and subcortical file: Found Skipping combining cortical and sc")
		else: 
			# Integration of subcortical data
			polydatamerge(subsAllDWISpace, SURFACE, outputSurfaceFullMerge)

			# Add outputSurfaceFullMerge in INPUTDATA folder for visualization 
			shutil.copy(outputSurfaceFullMerge, OUT_INPUTDATA)

		SURFACE = outputSurfaceFullMerge

   
    

	########################################################################
	'''   
	    Run tractography

	 1- Create Diffusion data for bedpostx: conversion of BRAINMASK and DWI data: .nrrd file format to FSL format (.nii.gz) with DWIConvert
	 2- Bedpostx: fit probabilistic diffusion model      - 
	 3- ExtractLabelSurfaces: creation label surface from a VTK surface containing label information
	 4- Creation of seed list: text file listing all path of label surfaces created by ExtractLabelSurfaces using writeSeedList.py
	 5- Probtrackx2: compute tractography according to the seed list created
	 6- Convert T1 image to nifti format using DWIConvert
	 7- Normalize the matrix and save plot as PDF file using plotMatrix.py

	(from the script: "tractographyScriptAppv2.0.sh" in /CIVILITY/src/civility-tractography/scripts) 
	'''
	########################################################################

	print("**********************************************************************************")
	print("Script 4: tractography")
	print("**********************************************************************************")

	# *****************************************
	# Set parameters
	# *****************************************

	if EXTRA_SURFACE_COLOR.lower() == "true":
		EXTRA_SURFACE_COLOR = SURFACE

	overlapFlag, overlapName, loopcheckFlag, loopcheckName = ("", "", "", "")
	if overlapping: 
		overlapFlag = "--overlapping" ; overlapName = "_overlapping" 
	if loopcheck: 
		loopcheckFlag = "--loopcheck" ; loopcheckName = "_loopcheck"
	

	# *****************************************
	# Ouput folder
	# *****************************************

	OutSurfaceName = os.path.join(OUT_TRACTOGRAPHY, "OutputSurfaces" + overlapName)
	if not os.path.exists(OutSurfaceName):
	    os.mkdir(OutSurfaceName)

		
	print("*****************************************")
	print("DWIConvert BRAINMASK and DWI: nrrd to nii")
	print("*****************************************")

	# Outputs:
	DiffusionData      = os.path.join(OUT_DIFFUSION, "data.nii.gz") 
	DiffusionBrainMask = os.path.join(OUT_DIFFUSION, "nodif_brain_mask.nii.gz")

	# DWIConvert BRAINMASK: NrrdToFSL: .nrrd file format to FSL format (.nii.gz)     # Err: "No gradient vectors found " --> it is normal 
	if os.path.exists(DiffusionBrainMask):
	    print("Brain mask FSL file: Found Skipping convertion")
	else: 
	    run_command("DWIConvert BRAINMASK to FSL format(err ok)", [DWIConvertPath, "--inputVolume", BRAINMASK, 
								                                                   "--conversionMode", "NrrdToFSL", 
								                                                   "--outputVolume", DiffusionBrainMask, 
								                                                   "--outputBVectors", os.path.join(OUT_DIFFUSION, "bvecs.nodif"), 
								                                                   "--outputBValues", os.path.join(OUT_DIFFUSION, "bvals.temp")])
	# DWIConvert DWI: Nrrd to FSL format
	if os.path.exists(DiffusionData):
	    print("DWI FSL file: Found Skipping convertion")
	else:
	    run_command("DWIConvert DWI to FSL format", [DWIConvertPath, "--inputVolume", DWI_NRRD, # original: DWI_DATA
							                                         "--conversionMode", "NrrdToFSL", 
							                                         "--outputVolume", DiffusionData, 
							                                         "--outputBVectors", os.path.join(OUT_DIFFUSION, "bvecs"), 
							                                         "--outputBValues", os.path.join(OUT_DIFFUSION, "bvals")])


	print("*****************************************")
	print("Create labelSurfaces (~2h30 or 4h with subcortical regions)")
	print("*****************************************")				

	# Outputs:
	labelListNamePath   = os.path.join(OutSurfaceName, "labelListName.txt")
	labelListNumberPath = os.path.join(OutSurfaceName, "labelListNumber.txt")

	if os.path.exists( labelListNamePath):
	    print("labelListName.txt file: Found Skipping create labelSurfaces")
	else:
		now = datetime.datetime.now()
		print (now.strftime("Script running ExtractLabelSurfaces command since: %H:%M %m-%d-%Y"))
		start = time.time()
	
		# Extract Point Data from the vtk file containing labels
		command = [ExtractLabelSurfaces, "--extractPointData", "--translateToLabelNumber",   # /tools/bin_linux64/ExtractLabelSurfaces 
								  	    	 "--labelNameInfo", labelListNamePath, 
								  	    	 "--labelNumberInfo", labelListNumberPath, 
								  	    	 "--useTranslationTable", "--labelTranslationTable", new_parcellation_table, 
								  	    	 "-a", labelSetName, 
								  	    	 "--vtkLabelFile", EXTRA_SURFACE_COLOR, 
								  	    	 "--createSurfaceLabelFiles", 
								  	    	 "--vtkFile", SURFACE,
								  	    	 overlapFlag]

		if ignoreLabel != '' or ignoreLabel.lower() != 'false':
			command.append("--ignoreLabel")
			command.append(str(ignoreLabel))
			run_command("ExtractLabelSurfaces if 'ignoreLabel' != ''", command)
		else:
	  		run_command("ExtractLabelSurfaces", command)

		# Move created files (.asc) in the tractography folder 
		shutil.move('./labelSurfaces',OutSurfaceName)

		print("ExtractLabelSurfaces command: ",time.strftime("%H h: %M min: %S s",time.gmtime(time.time() - start)))



	print("*****************************************")
	print("Write seed list") 
	print("*****************************************")

	# No overwritting:
	if os.path.exists(os.path.join(OutSurfaceName,"seeds.txt")):
		os.remove(os.path.join(OutSurfaceName,"seeds.txt"))

	# Create a text file listing all path of label surfaces created by ExtractLabelSurfaces
	run_command("Write seed list", [sys.executable, writeSeedListScript, OutSurfaceName, overlapName, new_parcellation_table])


	
	print("*****************************************")
	print("Convert T1 image to nifti format")
	print("*****************************************")
	
	NETWORK_DIR = os.path.join(OUT_TRACTOGRAPHY, "Network" + overlapName + loopcheckName)
	if not os.path.exists( NETWORK_DIR ):
	    os.mkdir(NETWORK_DIR)

	T1_nifti = os.path.join(NETWORK_DIR, ID + "-T1_SkullStripped_scaled.nii.gz")
	if os.path.exists(T1_nifti):
	    print("T1_nifti file: Found Skipping Convert T1 image to nifti format ")
	else:
	    print("Convert T1 image to nifti format ")
	    run_command("DWIConvert: convert T1 image to nifti format", [DWIConvertPath, "--inputVolume", T1_DATA, 
														                             "--conversionMode", "NrrdToFSL", 
														                             "--outputVolume", T1_nifti, 
														                             "--outputBValues", os.path.join(OUT_DIFFUSION, "bvals.temp"), 
														                             "--outputBVectors", os.path.join(OUT_DIFFUSION, "bvecs.temp")])



	if tractography_model == "FSL": 

		print("*****************************************")
		print("Run tractography with FSL")
		print("*****************************************")

		# Bedpostx: fit probabilistic diffusion model: automatically determines the number of crossing fibres per voxel
		if os.path.exists( os.path.join(OUT_TRACTOGRAPHY, "Diffusion.bedpostX")):
			print("Bedpostx folder: Found Skipping bedpostx function")
		else:
			print("*****************************************")
			print("Start bedpostx (~ 11 hours)")
			print("*****************************************")

			now = datetime.datetime.now()
			print (now.strftime("Script running bedpostx command since: %H:%M %m-%d-%Y"))
			start = time.time() #                , INPUT directory           
			run_command("bedpostx", [FSLPath + '/bedpostx', OUT_DIFFUSION, "-n", nb_fibers])
			print("bedpostx command: ",time.strftime("%H h: %M min: %S s",time.gmtime(time.time() - start)))

		# Name define by probtrackx2 tool:
		matrix = "fdt_network_matrix"
		matrixFile = os.path.join(NETWORK_DIR, matrix)

		# Probtrackx2:
		if os.path.exists(matrixFile): 
		    print("fdt_network_matrix found: Found Skipping probtrackx function")
		else:
			print("*****************************************")
			print("Start tractography with probtrackx2 (~1h )")
			print("*****************************************")

			now = datetime.datetime.now()
			print (now.strftime("Script running probtrackx2 command since: %H:%M %m-%d-%Y"))
			start = time.time()
			run_command("probtrackx2", [FSLPath + '/probtrackx2', "-s", os.path.join(OUT_TRACTOGRAPHY, "Diffusion.bedpostX", "merged"), #-s,--samples	
							                             "-m", os.path.join(OUT_TRACTOGRAPHY, "Diffusion.bedpostX", "nodif_brain_mask"), #-m,--mask
							                             "-x", os.path.join(OUT_TRACTOGRAPHY, "seeds.txt"), #-x,--seed
							                             "--forcedir", "--network", "--omatrix1", "-V", "0",
							                             "--dir="+NETWORK_DIR, 
							                             "--stop="+os.path.join(OUT_TRACTOGRAPHY, "seeds.txt"), 
							                             "-P", nb_fiber_per_seed, #-P,--nsamples	Number of samples - default=5000
							                             "--steplength="+steplength, 
							                             "--sampvox="+sampvox, loopcheckFlag ])
			print("probtrackx2 command: ", time.strftime("%H h: %M min: %S s",time.gmtime(time.time() - start)))


		print("*****************************************")
		print("Normalize connectivity matrix and save plot as PDF file")
		print("*****************************************")
		
		save_connectivity_matrix('no_normalization', no_normalization(matrixFile), NETWORK_DIR, ID, overlapName, loopcheck)
		save_connectivity_matrix('whole', whole_normalization(matrixFile), NETWORK_DIR, ID, overlapName, loopcheck)
		save_connectivity_matrix('row_region', row_region_normalization(matrixFile), NETWORK_DIR, ID, overlapName, loopcheck)
		save_connectivity_matrix('row_column', row_column_normalization(matrixFile), NETWORK_DIR, ID, overlapName, loopcheck)




	# *****************************************
	# Tractography with MRtrix 
	# *****************************************

	if tractography_model == "MRtrix (default: IFOD2) " or tractography_model == "MRtrix (Tensor-Prob)" or tractography_model == "MRtrix (iFOD1)": 
		
		print("*****************************************")
		print("Run tractography with " + tractography_model )
		print("*****************************************")

	 	# *****************************************
		# Output folder for MRtrix and DIPY 
		# *****************************************

		add = ""
		if filtering_with_tcksift.lower() == 'true':
			add = '_tcksif'

		if optimisation_with_tcksift2.lower() == "true": 
			add = '_tcksif2'


		OUT_MRTRIX = os.path.join(OUT_TRACTOGRAPHY, tractography_model + add) 
		if not os.path.exists(OUT_MRTRIX):
			os.mkdir(OUT_MRTRIX)


		# *****************************************
		# Response function estimation: Estimate response function(s) for spherical deconvolution
		# *****************************************

		Response_function_estimation_txt = os.path.join(OUT_MRTRIX,'Response_function_estimation.txt')
		if os.path.exists(Response_function_estimation_txt):
		    print("Response function estimation already compute ")
		else: 
			print("Compute Response function estimation")
			command = [MRtrixPath + "/dwi2response",'tournier', DiffusionData, # input
												   				Response_function_estimation_txt, #output
												                '-fslgrad', os.path.join(OUT_DIFFUSION, "bvecs"),os.path.join(OUT_DIFFUSION, "bvals"),# input
												                '-nthreads', nb_threads]
			run_command("Response function estimation", command)

		# *****************************************
		# Fibre Orientation Distribution estimation: Estimate fibre orientation distributions from diffusion data using spherical deconvolution
		# *****************************************

		FOD_nii = os.path.join(OUT_MRTRIX, "FOD.nii.gz")
		if os.path.exists(FOD_nii):
		    print("Fibre Orientation Distribution estimation already compute")
		else: 
			print("Compute Fibre Orientation Distribution estimation")
			run_command("FOD estimation", [MRtrixPath + "/dwi2fod", 'csd',
								    						        DiffusionData, # input
								    								Response_function_estimation_txt, # input
								    								FOD_nii, # ouput
								   									'-mask', DiffusionBrainMask, # input
								    								'-fslgrad', os.path.join(OUT_DIFFUSION, "bvecs"),os.path.join(OUT_DIFFUSION, "bvals"),# input
								    								'-nthreads', nb_threads ])

		# *****************************************
		# Convert nrrd T1 in DWI space file in nifti
		# *****************************************

		T1_DWI_SPACE_nifti = os.path.join(OUT_MRTRIX, "T1_DWI_SPACE.nii.gz")
		if os.path.exists(T1_DWI_SPACE_nifti):
		    print("T1_nifti file in DWI space: Found Skipping Convert T1 image to nifti format ")
		else:
			# Load nrrd:
			reader = vtk.vtkNrrdReader()
			reader.SetFileName(T1_OUT_NRRD)
			reader.Update()

			# Save nifti:
			writer = vtk.vtkNIFTIImageWriter()
			writer.SetInputData(reader.GetOutput())
			writer.SetFileName(T1_DWI_SPACE_nifti)
			writer.SetInformation(reader.GetInformation())
			writer.Write()


		# *****************************************
		# Create 5tt   
		# *****************************************	    
		
		# First choice: use T1_OUT_NRRD (after convertion in nifti): T1 in DWI space (second choice: use T1_nifti: T1 in structural space + add the transformation: affine )
		fivett_img = os.path.join(OUT_MRTRIX,"5tt.nii.gz")
		if os.path.exists(fivett_img):
		    print("5tt image already compute")
		else: 
			print("Create 5tt image (~20min )")      
			now = datetime.datetime.now()
			print (now.strftime("Script to create 5tt image running since: %H:%M %m-%d-%Y"))
			start = time.time()
			run_command("create 5tt", [sys.executable, MRtrixPath + "/5ttgen", 'fsl', 
																			   T1_DWI_SPACE_nifti, # input
																			   fivett_img, # output
																			   '-nthreads', nb_threads ])
			print("Create 5tt image: ", time.strftime("%H h: %M min: %S s",time.gmtime(time.time() - start)))
		

		# *****************************************
		# Output folder
		# *****************************************

		# Create Whole-brain streamlines tractography folder: 
		output_track_tckgen = os.path.join(OUT_MRTRIX, "output_track_tckgen") 
		if not os.path.exists(output_track_tckgen): os.mkdir(output_track_tckgen)

		OUT_MRTRIX_tck = os.path.join(output_track_tckgen, "output_track_tckgen_tck") 
		if not os.path.exists(OUT_MRTRIX_tck): os.mkdir(OUT_MRTRIX_tck)

		OUT_MRTRIX_vtk = os.path.join(output_track_tckgen, "output_track_tckgen_vtk") 
		if not os.path.exists(OUT_MRTRIX_vtk): os.mkdir(OUT_MRTRIX_vtk)
		
		# Output tcksift:
		if filtering_with_tcksift.lower() == 'true':
			tcksift_folder = os.path.join(OUT_MRTRIX, "output_tcksift") 
			if not os.path.exists(tcksift_folder): os.mkdir(tcksift_folder)

			tcksift_tck = os.path.join(tcksift_folder, "output_tcksift_tck") 
			if not os.path.exists(tcksift_tck): os.mkdir(tcksift_tck)

			tcksift_vtk = os.path.join(tcksift_folder, "output_tcksift_vtk") 
			if not os.path.exists(tcksift_vtk): os.mkdir(tcksift_vtk)			

		# Output tcksift2:
		if optimisation_with_tcksift2.lower() == 'true': 
			tcksift2_txt = os.path.join(OUT_MRTRIX, "output_tcksift2_streamlines_weights_txt") 
			if not os.path.exists(tcksift2_txt): os.mkdir(tcksift2_txt)

		# Output tckEdit:
		weights_folder = os.path.join(OUT_MRTRIX, "output_tckEdit_tracks_and_streamlines_weight") 
		if not os.path.exists(weights_folder): os.mkdir(weights_folder)

		if optimisation_with_tcksift2.lower() == 'false': 
			weight_txt = os.path.join(weights_folder, "output_tckEdit_streamlines_weights_txt") 
			if not os.path.exists(weight_txt): os.mkdir(weight_txt)

		weight_tck = os.path.join(weights_folder, "output_tckEdit_tracks_tck ") 
		if not os.path.exists(weight_tck): os.mkdir(weight_tck)


		# *****************************************
		# Open seed.txt file to have the number of regions
		# *****************************************

		number_region_all = 0
		seed_data = open(os.path.join(OutSurfaceName,"seeds.txt"), "r")
		for line in seed_data:  
			number_region_all +=1


		# *****************************************
		# Open seed.txt file to compute all radius
		# *****************************************

		all_seed_with_radius,number_point_per_region, region_name_per_region = ([], [], [])
		seed_data = open(os.path.join(OutSurfaceName,"seeds.txt"), "r")
		for line in seed_data: #for each .asc file: for each region 
			# Extract region name information: 
			line = line.strip('\n')
			number_region = line[-9:-4] #remove '.asc' 

			# Compute radius of each seed of this specific region:
			list_coord_seeds, number_point = compute_radius_of_each_seed(str(line)) 
			print('Compute radius for region:', number_region, " ,number of points:", number_point)
	
			all_seed_with_radius.append(list_coord_seeds) # a list of list:  a sublist with all seed and radius per region
			number_point_per_region.append(number_point)
			region_name_per_region.append(number_region)


		# *****************************************
		# Initialize connectome and tractography
		# *****************************************

		# Create connectome and open seed.txt file to compute tractography:
		connectome = np.zeros( (number_region_all, number_region_all) )
		seed_data = open(os.path.join(OutSurfaceName,"seeds.txt"), "r")

		region = 0 
		while region < number_region_all: 
			# Get seeds and radius of the considering region: 
			list_coord_seeds = all_seed_with_radius[region]
			number_point     = number_point_per_region[region]
			number_region    = region_name_per_region[region]

			# Output: tck file generated by tckgen for this region: 
			output_track_tckgen_tck = os.path.join(OUT_MRTRIX_tck, "output_track_tckgen_tck_" + number_region + ".tck")


			# *****************************************
			# Compute tractography with different option and algorithm
			# *****************************************
			
			if os.path.exists(output_track_tckgen_tck):
			    print("Whole-brain streamlines tractography already compute for region " + number_region)
			else:
				print("Compute tractography with for region " + number_region )	

				# Type of algorithm and their specification:
				if tractography_model == "MRtrix (default: IFOD2) ":
					command = [MRtrixPath + "/tckgen", '-algorithm', 'iFOD2', FOD_nii, output_track_tckgen_tck]	

				elif tractography_model == "MRtrix (Tensor-Prob)":
					command = [MRtrixPath + "/tckgen", '-algorithm', 'Tensor_Prob', DiffusionData, output_track_tckgen_tck]

				elif tractography_model == "MRtrix (iFOD1)": 
					command = [MRtrixPath + "/tckgen", '-algorithm', 'iFOD1', FOD_nii, output_track_tckgen_tck]	

			    # Add seed coordinates for this region:
				for element in  list_coord_seeds[0 : number_point-1]:  
					command.append('-seed_sphere')
					command.append(str(element[0]) + ',' + str(element[1]) + ',' + str(element[2]) + ',' + str(element[3]) ) # X Y Z and radius
									   

				# act option: (not a seed option)
				if act_option.lower() == 'true': 
					command.append('-act')
					command.append(fivett_img)
					

				# Add common parameters: 
				command.append('-select')
				command.append(nb_fibers)
				
				command.append('-fslgrad')
				command.append(os.path.join(OUT_DIFFUSION, "bvecs"))
				command.append(os.path.join(OUT_DIFFUSION, "bvals"))
				command.append('-mask')
				command.append(DiffusionBrainMask)
				command.append('-nthreads')
				command.append( nb_threads)

			    # Run command:
				run = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				out, err = run.communicate()
				print("MRtrix tractography", "out: ", colored("\n" + str(out) + "\n", 'green')) 
				print("MRtrix tractography", "err: ", colored("\n" + str(err) + "\n", 'red'))	   
					

				# *****************************************
				# Convert tractography tck file to vtk format    FOR VISUALIZATION
				# *****************************************
				'''
				output_track_tckgen_vtk = os.path.join(OUT_MRTRIX_vtk, "output_track_tckgen_tck_" + number_region  + ".vtk")
				if os.path.exists(output_track_tckgen_vtk):
				    print("Convertion to vtk already done")
				else:
					print("Convert tck to vtk")									
					run_command("Convert to vtk", [MRtrixPath + "/tckconvert", output_track_tckgen_tck, output_track_tckgen_vtk])
				'''
				

			# Run tcksift: 
			if filtering_with_tcksift.lower() == 'true': # Filtering with SIFT 

				# *****************************************
				# tcksift: Filter a whole-brain fibre-tracking data
				# *****************************************

				output_tcksift_tck = os.path.join(tcksift_tck, "output_tcksift_" + number_region  + ".tck")
				if os.path.exists(output_tcksift_tck):
				    print("Tractography already filtered with tcksift")
				else:
					print("Filtering Tractography with tcksift")  
					run_command("tcksift ", [MRtrixPath + "/tcksift", output_track_tckgen_tck, FOD_nii, output_tcksift_tck, '-nthreads', nb_threads])	

				  
				# *****************************************
				# Convert tcksif tck file to vtk format       FOR VISUALIZATION
				# *****************************************
				'''
				output_tcksift_vtk = os.path.join(tcksift_vtk,"output_tcksift_" + number_region  + ".vtk")
				if os.path.exists(output_tcksift_vtk):
				    print("Convertion to vtk already done")
				else:
					print("Convert tck to vtk")									
					run_command("Convert to vtk", [MRtrixPath + "/tckconvert", output_tcksift_tck, output_tcksift_vtk]) 
				'''
				
			
			# *****************************************
			# Complete connectome: 
			# *****************************************

			region_target = 0
			while region_target < number_region_all: 
				# Get seeds and radius of the target region: 
				list_coord_seeds_target = all_seed_with_radius[region_target]
				number_point_target     = number_point_per_region[region_target]
				number_region_target    = region_name_per_region[region_target]
				print('region',region,'(name', number_region,') ,region target', region_target,'(name', number_region_target,')')

				# Outputs:
				output_tckEdit_tracks_tck = os.path.join(weight_tck, "output_tckEdit_tracks_" + number_region + '_with_' + number_region_target + ".tck" )
				
				if optimisation_with_tcksift2.lower() == "false": 
					weight_txt_file = os.path.join(weight_txt, "output_tckEdit_streamlines_weight_" + number_region + '_with_' + number_region_target + ".txt" )
				else: 
					output_tcksift2_txt = os.path.join(tcksift2_txt, "output_tcksift2_streamlines_weights_" + number_region + '_with_' + number_region_target + ".txt")

				# tckEdit:
				if os.path.exists(output_tckEdit_tracks_tck):
					print('tckEdit already done')
				else:

					# *****************************************
					# tckEdit: Perform various editing operations on track files
					# *****************************************

					# Add input track file for tckEdit: file with all streamlines between the considering region and the target region
					if filtering_with_tcksift.lower() == 'false': # NO filtering with SIFT before tckEdit
						command = [MRtrixPath + "/tckedit", output_track_tckgen_tck] 
																	   
					else: # Filtering with SIFT before tckEdit
						command = [MRtrixPath + "/tckedit", output_tcksift_tck] #input track file

					# Add output track file:								
					command.append(output_tckEdit_tracks_tck) 
					command.append('-force')

					# Option '-tck_weights_out': specify the path for an output text scalar file containing streamline weights
					if optimisation_with_tcksift2.lower() == "false": 
						command.append('-tck_weights_out')
						command.append(weight_txt_file)

					# Add seed coordinates for target region:
					for element in list_coord_seeds_target[0 : number_point_target-1]:  
						command.append('-include')
						command.append(	str(element[0]) + ',' + str(element[1]) + ',' + str(element[2]) + ',' + str(element[3]) ) # X Y Z and radius

					# Run command (command line too big to be displayed)
					run = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					out, err = run.communicate()
					print("tckedit ", "out: ", colored("\n" + str(out) + "\n", 'green')) 
					print("tckedit ", "err: ", colored("\n" + str(err) + "\n", 'red'))	 
					

				# tcksift2:
				if optimisation_with_tcksift2.lower() == "true": 
					# Extract the number of streamlines:
					run = subprocess.Popen([MRtrixPath + "/tckinfo", '-count', output_tckEdit_tracks_tck], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					out, err = run.communicate()
				
					for i in out.splitlines():
						section = i.split()
						if "count:" in str(section):  
							number_stream_in_output_tckEdit_tracks_tck = int(section[-1])
							break # to avoid 'total_count' section: [b'total_count:', b'4895']
					print('number of stream in the output file ot tckEdit:',number_stream_in_output_tckEdit_tracks_tck )

					# Do tcksift2: 
					if number_stream_in_output_tckEdit_tracks_tck != 0:
						if os.path.exists(output_tcksift2_txt):
						    print("tcksift2 already done")
						else:

							# *****************************************
							# tcksift2: Optimise per-streamline cross-section multipliers to match a whole-brain tractogram to fixel-wise fibre densities
							# *****************************************

							print("Do optimization algorithm tcksift2: ")		
							run_command("tcksift2", [MRtrixPath + "/tcksift2", output_tckEdit_tracks_tck, FOD_nii, output_tcksift2_txt, '-nthreads', nb_threads])	

						# Open output file: 
						weight_file = open(output_tcksift2_txt, 'r')
						first = weight_file.readline() #first line: command line so skip

					# Not execute tcksift2 because of 0 streamline between this 2 regions:
					else: 
						weight_file = 'nan'
						value = 0 #value in the connectivity matrix
				else: 
					# Open output file: 
					weight_file = open(weight_txt_file, 'r')


				# Compute value: Value in connectome matrix between this two region: sum of weight of each streamlines 
				if weight_file != 'nan':
					# Sum each weight of each streamline: (just one line file)
					value = 0
					line = weight_file.readline().strip('\n')
					line_list = line.split(" ")
					line_list = line_list[:-1]

					for i in range(len(line_list)):
						value += float(line_list[i])
		
				# Write connectome: 
				connectome[region,region_target] = value
				print('value for the connectivity matrix:', connectome[region,region_target])
				
				region_target += 1
				print("************************")

			print("*********************************************************************")
			region += 1


		# *****************************************
		# Save the MRtrix connectome
		# *****************************************

		connectome_mrtrix = os.path.join(OUT_MRTRIX,'fdt_network_matrix')
		
		# No overwritting:
		if os.path.exists(connectome_mrtrix):
			os.remove(connectome_mrtrix)

		np.savetxt(connectome_mrtrix, connectome.astype(float),  fmt='%f', delimiter='  ')

		








	elif tractography_model == "DIPY":
		
		print("*****************************************")
		print("Run tractography with DIPY")
		print("*****************************************")
		# https://dipy.org/documentation/1.4.0./examples_built/tracking_probabilistic/#example-tracking-probabilistic

		# *****************************************
		# Output folder for MRtrix and DIPY 
		# *****************************************

		OUT_MRTRIX = os.path.join(OUT_TRACTOGRAPHY, tractography_model) 
		if not os.path.exists(OUT_MRTRIX):
			os.mkdir(OUT_MRTRIX)
			

		#*****************************************
		# Data and gradient
		#*****************************************
		
		data, affine, img = load_nifti(T1_nifti, return_img=True) 
	
		# https://dipy.org/documentation/1.1.1./reference/dipy.data/#dipy.data.gradient_table
		gtab = gradient_table(os.path.join(OUT_DIFFUSION, "bvals"), os.path.join(OUT_DIFFUSION, "bvecs"))

		# White matter mask to restrict tracking to the white matter
		white_matter = DiffusionBrainMask # DiffusionBrainMask = nifti of brainmask


        #*****************************************
		# Method for getting directions from a diffusion data set
		#*****************************************

		# https://dipy.org/documentation/1.2.0./examples_built/reconst_csd/
		response, ratio = auto_response_ssst(gtab, data, roi_radii=10, fa_thr=0.7)   #single shell    0.7: adult brain 

		# Multi-Shell Multi-Tissue: used auto_response_msmt
		#https://dipy.org/documentation/1.2.0./examples_built/reconst_mcsd/       csd: single shell



		# Fit a Constrained Spherical Deconvolution (CSD) model.
		csd_model = ConstrainedSphericalDeconvModel(gtab, response, sh_order=6) 
		csd_fit = csd_model.fit(data, mask=white_matter) 


        #*****************************************
		# Stopping criterion: a method for identifying when the tracking must stop: restricting the fiber tracking to areas with good directionality information
		#*****************************************

		# We use the GFA of the CSA model to build a stopping criterion.
		# Fit the data to a Constant Solid Angle ODF Model: estimate the Orientation Distribution Function (ODF) at each voxel
		csa_model = CsaOdfModel(gtab, sh_order=6) 
		gfa = csa_model.fit(data, mask=white_matter).gfa 

		# Restrict fiber tracking to white matter mask where the ODF shows significant restricted diffusion by thresholding on the generalized fractional anisotropy (GFA)
		stopping_criterion = ThresholdStoppingCriterion(gfa, .25) 


        #*****************************************
		# A set of seeds from which to begin tracking: the seeds chosen will depend on the pathways one is interested in modeling
		#*****************************************

		seed_mask = DiffusionBrainMask
		seeds = utils.seeds_from_mask(seed_mask, affine, density=1) 

		# The peaks of an ODF are good estimates for the orientation of tract segments at a point in the image
		# peaks_from_model: fit the data and calculated the fiber directions in all voxels of the white matter
		peaks = peaks_from_model(csd_model, data, default_sphere, .5, 25, mask=white_matter, return_sh=True, parallel=True) 
		fod_coeff = peaks.shm_coeff

		# Discrete FOD used by the ProbabilisticDirectionGetter as a PMF for sampling tracking directions.
		prob_dg = ProbabilisticDirectionGetter.from_shcoeff(fod_coeff, max_angle=30., sphere=default_sphere) 


        #*****************************************
	    # Generate streamlines
	    #*****************************************

		# Initialization of LocalTracking: 
		streamline_generator = LocalTracking(prob_dg, stopping_criterion, seeds, affine, step_size=.5)

		# Generate streamlines object: 
		streamlines = Streamlines(streamlines_generator)


        #*****************************************
		# Save the streamlines as a Trackvis file
		#*****************************************
		sft = StatefulTractogram(streamlines, img, Space.RASMM)
		save_trk(sft, "tractogram.trk", streamlines)