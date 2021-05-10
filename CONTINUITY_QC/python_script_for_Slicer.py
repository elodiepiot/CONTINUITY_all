#!/usr/bin/env python3
import argparse
import json
import os 

#macro: 
#import slicer
#import ApplicationsSlicerAppData as data

##########################################################################################################################################
'''  
     CONTINUITY python script running by Slicer: Python script to load specific files and parameters
'''  
##########################################################################################################################################

# *****************************************
# Parameters
# *****************************************

parser = argparse.ArgumentParser(description='python script for Slicer')
parser.add_argument("user_json_filename", help = "json file with arguments like ID, OUTPATH and parameters for view controllers", type = str)
args = parser.parse_args()

user_json_filename = args.user_json_filename
with open(user_json_filename, "r") as user_Qt_file:
    json_user_object = json.load(user_Qt_file)

print("Execution of python script for Slicer")

'''
#run macro in Slicer
testUtility= slicer.app.testingUtility()
success = testUtility.playTests("./CONTINUITY_QC/test_macro4.xml")
'''


# *****************************************
# Extraction name of parcellation 
# *****************************************

parc_inv = ''
for i in json_user_object['Parameters']['PARCELLATION_TABLE']['value'][::-1]:
    if i == "_":
        break
    parc_inv = parc_inv +i
NAME_PARCELLATION_TABLE_json = parc_inv[::-1]
NAME_PARCELLATION_TABLE = NAME_PARCELLATION_TABLE_json[:-5]



# *****************************************
# DATA
# *****************************************

ID = json_user_object['Parameters']['ID']['value']
input_path = os.path.join( json_user_object['Parameters']['OUT_PATH']['value'], ID, "InputDataForSlicer")


#find datas for B0_BiasCorrect
B0 = os.path.join( input_path, ID +"_DTI_B0_BiasCorrect_resample.nrrd")
if not os.path.exists(B0):
	B0 = os.path.join( input_path, ID +"_DTI_B0_BiasCorrect_original.nrrd")

#find datas for B0
B0_with_biais = os.path.join( input_path, ID +"_DTI_B0_resample.nrrd")
if not os.path.exists(B0_with_biais):
	B0_with_biais = os.path.join( input_path, ID +"_DTI_B0_original.nrrd")


# Find data for T1 and T1_registered
T1_registered = os.path.join( input_path, ID + "_T1_SkullStripped_scaled_DWISpace.nrrd")


# Find data for AD: (A0_NRRD variable in the script)
AD = os.path.join( input_path, ID +"_DTI_A0_resample.nrrd")
if not os.path.exists(AD):
	AD = os.path.join( input_path,  ID +"_DTI_A0_original.nrrd")


# Find data for FA: 
FA = os.path.join( input_path, ID +"_DTI_FA_resample.nrrd")
if not os.path.exists(FA):
	FA = os.path.join( input_path, ID +"_DTI_FA_original.nrrd")


# Find data for DWI: 


# Find data for surface: 
registered_combine_surface         = os.path.join( input_path, ID + "stx_" + ID + "_T1_CombinedSurface_" + NAME_PARCELLATION_TABLE + ".vtk")
registered_combine_surface_with_sc = os.path.join( input_path, ID + "stx_" + ID + "_T1_CombinedSurface_" + NAME_PARCELLATION_TABLE + "._WithSubcorticals.vtk")

surface_left          = os.path.join( input_path, ID + "stx_" + ID 
							+ "_SkullStripped_scaled_BiasCorr_corrected_multi_atlas_white_surface_rsl_left_327680_native_DWIspace" + NAME_PARCELLATION_TABLE + ".vtk")

surface_left_labeled  = os.path.join( input_path, ID + "stx_" + ID 
							+ "_SkullStripped_scaled_BiasCorr_corrected_multi_atlas_white_surface_rsl_left_327680_native_DWIspace_labeled" + NAME_PARCELLATION_TABLE + ".vtk")

surface_right         = os.path.join( input_path, ID + "stx_" + ID 
							+ "_SkullStripped_scaled_BiasCorr_corrected_multi_atlas_white_surface_rsl_right_327680_native_DWIspace" + NAME_PARCELLATION_TABLE + ".vtk")

surface_right_labeled = os.path.join( input_path, ID + "stx_" + ID 
							+ "_SkullStripped_scaled_BiasCorr_corrected_multi_atlas_white_surface_rsl_right_327680_native_DWIspace_labeled" + NAME_PARCELLATION_TABLE + ".vtk")




# *****************************************
# Load data in Slicer (no show)
# *****************************************
if os.path.exists(B0):
	loadedVolumeNode_B0                                 = slicer.util.loadVolume(B0,            properties={'name': 'B0', 'show': False})

if os.path.exists(B0_with_biais):
	loadedVolumeNode_B0_with_biais                      = slicer.util.loadVolume(B0_with_biais, properties={'name': 'B0_with_biais', 'show': False})

if os.path.exists(T1_registered):
	loadedVolumeNode_T1_registered                      = slicer.util.loadVolume(T1_registered, properties={'name': 'T1_registered', 'show': False})

if os.path.exists(AD):
	loadedVolumeNode_AD                                 = slicer.util.loadVolume(AD, properties={'name': 'AD' , 'show': False} )

if os.path.exists(FA):
	loadedVolumeNode_FA                                 = slicer.util.loadVolume(FA, properties={'name': 'FA' , 'show': False} )

if os.path.exists(registered_combine_surface):
	loadedVolumeNode_registered_combine_surface         = slicer.util.loadVolume(registered_combine_surface,         properties={'name': 'registered_combine_surface' , 'show': False} )

if os.path.exists(registered_combine_surface_with_sc):
	loadedVolumeNode_registered_combine_surface_with_sc = slicer.util.loadVolume(registered_combine_surface_with_sc, properties={'name': 'registered_combine_surface_with_sc' , 'show': False} )

if os.path.exists(surface_left):
	loadedVolumeNode_surface_left                       = slicer.util.loadVolume(surface_left,          properties={'name': 'surface_left' , 'show': False} )

if os.path.exists(surface_left_labeled):
	loadedVolumeNode_surface_left_labeled               = slicer.util.loadVolume(surface_left_labeled,  properties={'name': 'surface_left_labeled' , 'show': False} )

if os.path.exists(surface_right):
	loadedVolumeNode_surface_right                      = slicer.util.loadVolume(surface_right,         properties={'name': 'surface_right' , 'show': False} )

if os.path.exists(surface_right_labeled):
	loadedVolumeNode_surface_right_labeled              = slicer.util.loadVolume(surface_right_labeled, properties={'name': 'surface_right_labeled' , 'show': False} )




# *****************************************
# Get not and display data in the good place
# *****************************************

#Set the view: https://apidocs.slicer.org/v4.8/classvtkMRMLLayoutNode.html#a8273252526dff35749ddeefd80c5226a
slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutThreeByThreeSliceView)

for place in ['Red', 'Yellow', 'Green', 'Slice4', 'Slice5', 'Slice6','Slice7', 'Slice8', 'Slice9']:
	node = slicer.util.getNode(str(json_user_object['View_Controllers'][place]['value'])

	# Display
	slicer.app.layoutManager().sliceWidget(place).sliceLogic().GetSliceCompositeNode().SetForegroundVolumeID( node.GetID() ) 