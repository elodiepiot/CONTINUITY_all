#!/usr/bin/env python3
import json
import os 
import sys 
import shutil
import subprocess 
from termcolor import colored
import time
import datetime
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QCheckBox, QGridLayout, QLabel, QTableWidgetItem
from PyQt5.QtCore import Qt

from main_CONTINUITY import * 
from CONTINUITY_functions import *


class Ui(QtWidgets.QTabWidget):

    # *****************************************
    # Init interface
    # *****************************************

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('interface_tab.ui', self)

        # write default values on interface:  
        Ui.setup_default_values(self)

        self.show()



    # *****************************************
    # Write in user json file
    # *****************************************  
    
    def update_user_json_file():
        with open(user_json_filename, "w+") as user_Qt_file:
            user_Qt_file.write(json.dumps(json_user_object, indent=4)) 



    # *****************************************
    # Function to run a specific command
    # *****************************************
    def run_command(text_printed, command):
        # Display command 
        print(colored("\n"+" ".join(command)+"\n", 'blue'))
        # Run command and display output and error
        run = subprocess.Popen(command, stdout=0, stderr=subprocess.PIPE)
        out, err = run.communicate()
        print(text_printed, "out: ", colored("\n" + str(out) + "\n", 'green')) 
        print(text_printed, "err: ", colored("\n" + str(err) + "\n", 'red'))



    # *****************************************
    # Setup default value (locating in args_setup.json) in the interface 
    # *****************************************

    def setup_default_values(self):
        # Arguments filename
        global user_json_filename
        user_json_filename = "./CONTINUITY_ARGS/args_main_CONTINUITY.json"
        default_json_filename = "./CONTINUITY_ARGS/args_main_CONTINUITY_completed_test.json" #./CONTINUITY_ARGS/args_setup.json"


        # Json file which contains values given by the user: 
        with open(user_json_filename, "r") as user_Qt_file:
            global json_user_object
            json_user_object = json.load(user_Qt_file)

        # Json file which contains defaults values
        with open(default_json_filename, "r") as default_Qt_file:
            global json_setup_object
            json_setup_object = json.load(default_Qt_file)

        # Initilize json user file with default value in json default file
        for categories, infos in json_setup_object.items():
            for key in infos: 
                json_user_object[categories][key]["value"] = json_setup_object[categories][key]["default"]
                Ui.update_user_json_file() 

        # Registration
        self.registration_tab1_groupBox.setChecked(True)
        self.registration_tab2_groupBox.setChecked(False)
        Ui.no_registration_surface_data_clicked(self)
        Ui.no_registration_surface_data_clicked2(self)

        if (json_setup_object['Parameters']["DO_REGISTRATION"]["default"]).lower() == "false": 
            self.registration_tab1_groupBox.setChecked(False)
            self.registration_tab2_groupBox.setChecked(True)
            Ui.no_registration_surface_data_clicked(self)
            Ui.no_registration_surface_data_clicked2(self)


        # ID: text and help 
        self.job_name_lineEdit.setText( json_setup_object['Parameters']["ID"]["default"] )
        self.question_job_name_textEdit.setStyleSheet("color: transparent;"  "background-color: transparent")

        # Parcellation table for registration and non registration:
        self.PARCELLATION_TABLE_textEdit.setText(json_setup_object['Parameters']["PARCELLATION_TABLE"]["default"])
        self.no_registration_parcellation_table_textEdit.setText(json_setup_object['Parameters']["PARCELLATION_TABLE"]["default"])

        # Labelset name: text and help: 
        self.labelset_lineEdit.setText( json_setup_object['Parameters']["labelSetName"]["default"] ) 
        self.question_labelset_name_textEdit.setStyleSheet("color: transparent;"  "background-color: transparent")

        # Label cortical surfaces for registration and not registration:
        self.question_cortical_labeled_textEdit.setStyleSheet("color: transparent;"  "background-color: transparent")
        self.NO_registration_question_cortical_labeled_textEdit.setStyleSheet("color: transparent;"  "background-color: transparent")

        # Surface_already_labeled:
        self.surface_already_labeled_groupBox.setChecked(True)
        if json_setup_object['Parameters']["surface_already_labeled"]["default"].lower() == "true":
            self.surface_already_labeled_groupBox.setChecked(False)

        # NO_registration_surface_already_labeled:
        self.NO_registration_surface_already_labeled_groupBox.setChecked(True)
        if json_setup_object['Parameters']["surface_already_labeled"]["default"].lower() == "true":
            self.NO_registration_surface_already_labeled_groupBox.setChecked(False)

        # Cortical_label left and right: do and do not registration:
        self.cortical_label_left_textEdit.setText(json_setup_object['Parameters']["cortical_label_left"]["default"])
        self.cortical_label_right_textEdit.setText(json_setup_object['Parameters']["cortical_label_right"]["default"])
        self.NO_registration_cortical_label_left_textEdit.setText(json_setup_object['Parameters']["cortical_label_left"]["default"])
        self.NO_registration_cortical_label_right_textEdit.setText(json_setup_object['Parameters']["cortical_label_right"]["default"])

        # Subcortical tab: color code explanation
        self.SALTDir_textEdit.setText(json_setup_object['Parameters']["SALTDir"]["default"])
        self.KWMDir_textEdit.setText(json_setup_object['Parameters']["KWMDir"]["default"])
        self.color_sc_textEdit.setStyleSheet("background-color: transparent")
        self.question_SALT_textEdit.setStyleSheet("color: transparent;"  "background-color: transparent")        
        self.question_KWM_textEdit.setStyleSheet("color: transparent;"  "background-color: transparent")

        # Subcortical tab: helps buttons and help texts
        self.integrate_sc_data_groupBox.setChecked(False)
        color = "background-color: white"
        if (json_setup_object['Parameters']["INTEGRATE_SC_DATA"]["default"]).lower() == "true":
            self.integrate_sc_data_groupBox.setChecked(True)
            color = "background-color: blue"
        self.question_SALT_pushButton.setStyleSheet(color)
        self.question_KWM_pushButton.setStyleSheet(color)

        # Registration tab: upsampling
        self.upsampling_checkBox.setChecked(False)
        if (json_setup_object['Parameters']["UPSAMPLING_DWI"]["default"]).lower() == "true":
            self.upsampling_checkBox.setChecked(True)
   
        # Initialization ANTS param: images for cross correlation
        list_param_setCurrentText = ["first_fixed_img", "first_moving_img", "second_fixed_img", "second_moving_img" ]
        for item in list_param_setCurrentText:
            eval("self." + item + "_comboBox.setCurrentText( str(Ui.convert_metric_parameter_json_to_QT( str(json_setup_object['Parameters'][item]['default']) )))")

        # Initialization of spinBox:
        list_param_setValue_spinBox = ["first_metric_weight", "first_radius", "second_metric_weight", "second_radius", 
                                       "iteration1", "iteration2", "iteration3", 
                                       "nb_fibers", "nb_fiber_per_seed", "nb_threads"]
        for item in list_param_setValue_spinBox:
            eval("self." + item + "_spinBox.setValue(int(json_setup_object['Parameters'][item]['default']))")

        # Initialization of doubleSpinBox:
        list_param_setValue_doubleSpinBox = ["gradient_field_sigma", "deformation_field_sigma", "SyN_param", "steplength", "sampvox"]
        for item in list_param_setValue_doubleSpinBox:
            eval("self." + item + "_doubleSpinBox.setValue(float(json_setup_object['Parameters'][item]['default']))")
  
        # Search path of executables: write them in user json file
        executable_path(default_json_filename, user_json_filename)

        # Display path of executables in GUI:
        with open(user_json_filename, "r") as user_Qt_file:
            json_user_object = json.load(user_Qt_file)
        for categories, infos in json_user_object.items():
            if categories == "Executables":
                for key in infos: 
                    eval("self." + key + "_textEdit.setText(json_user_object[categories][key]['value'])")

        # Ignore label:
        self.ignore_label_checkBox.setChecked(False)
        self.value_ignore_label_label.setStyleSheet("color: lightGray")
        self.ignore_label_lineEdit.setStyleSheet("background-color: transparent")
        if (json_setup_object['Parameters']["ignoreLabel"]["default"]).lower() == "true":
            self.ignore_label_checkBox.setChecked(True)

        # Overlapping:
        self.overlapping_checkBox.setChecked(False)
        if (json_setup_object['Parameters']["overlapping"]["default"]).lower() == "true":
            self.overlapping_checkBox.setChecked(True)

        # Loopcheck:
        self.loopcheck_checkBox.setChecked(False)
        if (json_setup_object['Parameters']["loopcheck"]["default"]).lower() == "true":
            self.loopcheck_checkBox.setChecked(True)  

        # Filtering_with_tcksift:
        self.filtering_with_tcksift_checkBox.setChecked(False)
        if (json_setup_object['Parameters']["filtering_with_tcksift"]["default"]).lower() == "true":
            self.filtering_with_tcksift_checkBox.setChecked(True)  

        # Optimisation_with_tcksift2:
        self.optimisation_with_tcksift2_checkBox.setChecked(False)
        if (json_setup_object['Parameters']["optimisation_with_tcksift2"]["default"]).lower() == "true":
            self.optimisation_with_tcksift2_checkBox.setChecked(True)  

        # Inner surface:
        self.inner_surface_checkBox.setChecked(False)
        if (json_setup_object['Parameters']["EXTRA_SURFACE_COLOR"]["default"]).lower() == "true":
            self.inner_surface_checkBox.setChecked(True) 
              
        # Combined or non combined surfaces:
        self.left_right_not_combined_groupBox.setChecked(True)
        self.left_right_combined_groupBox.setChecked(False)
        color ="color: lightGray"
        self.WML_surface_diffusion_label.setText('White Matter Left surface data in diffusion space (.vtk):')
        self.WMR_surface_diffusion_label.setText('White Matter Right surface data in diffusion space (.vtk):')
        self.no_registration_surface_diffusion_label.setText('Surface data labeled in diffusion space (.vtk):')          
        self.no_registration_surface_diffusion_label.setStyleSheet(color)
        if (json_setup_object['Parameters']["DO_REGISTRATION"]["default"]).lower() == "false":
            color = "color: black"
            self.WML_surface_diffusion_label.setText('White Matter Left surface data <font color="red">in diffusion space</font> (.vtk):')
            self.WMR_surface_diffusion_label.setText('White Matter Right surface data <font color="red">in diffusion space</font> (.vtk):')
        self.WML_surface_diffusion_label.setStyleSheet(color)
        self.WMR_surface_diffusion_label.setStyleSheet(color)

        # Submit job tab:
        self.json_config_file_textEdit.setText(json_setup_object['Parameters']["json_config_file"]["default"])

        # Local and remote run:
        self.local_run_groupBox.setChecked(True)
        self.remote_run_groupBox.setChecked(False)
        self.commande_line_cluster_plainTextEdit.setPlainText(json_setup_object['Parameters']["cluster_command_line"]["default"])

        # Out_PATH:
        self.OUT_PATH_textEdit.setText(json_setup_object['Parameters']["OUT_PATH"]["default"])

        

    # *****************************************
    # Initialization of metric parameters : default values (in json) write in Qt interface 
    # *****************************************

    def convert_metric_parameter_json_to_QT(json_param):
        dict_param = {"FA_NRRD":"FA in nrrd space",
                      "T1_DATA":"T1",
                      "T2_DATA":"T2",
                      "B0_BiasCorrect_NRRD":"BO bias correct in nrrd space"}
        return dict_param[json_param]



    # *****************************************
    # Parameters: update path choose by user
    # *****************************************  

    def update_param_path(self, button_name):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()" , "", "ALL Files (*)", options=QFileDialog.Options())
        if fileName:
            eval("self." + button_name + "_textEdit.setText(fileName)")
            json_user_object['Parameters'][button_name]["value"] = fileName
            Ui.update_user_json_file()



    # *****************************************
    # Functions activate if a "classic" button is clicked
    # *****************************************  

    def button_param_path_clicked(self):
        button_name = self.sender().objectName()[:-11]
        Ui.update_param_path(self, button_name)



















    # *************************************************************************************
    # Interface data tab
    # *************************************************************************************

    # *****************************************
    # User choose if this tool do the registration or not
    # *****************************************

    def registration_tab1_groupBox_valueChanged(self): 
        self.registration_tab2_groupBox.setChecked(True)
        json_user_object['Parameters']["DO_REGISTRATION"]["value"] = "False"

        if self.registration_tab1_groupBox.isChecked():
            self.registration_tab2_groupBox.setChecked(False)
            json_user_object['Parameters']["DO_REGISTRATION"]["value"] = "True" 
        Ui.update_user_json_file()



    # *****************************************
    # Write the job name in user information json file
    # *****************************************

    def job_name_textChanged(self):
        json_user_object['Parameters']["ID"]["value"] = self.job_name_lineEdit.text()
        Ui.update_user_json_file()



    # *****************************************
    # Button help which display explanations
    # *****************************************

    def question_job_name_pushButton_clicked(self):
        if self.question_job_name_pushButton.text() == "Help":
            self.question_job_name_pushButton.setText("close help")
            self.question_job_name_textEdit.setStyleSheet("color: blue;"  "background-color: transparent")
        else: # self.question_job_name_pushButton.text() == "X":
            self.question_job_name_pushButton.setText("Help")
            self.question_job_name_textEdit.setStyleSheet("color: transparent;"  "background-color: transparent")



    # *****************************************
    # Open file system and write the T2 data path in user information json file + change interface 
    # *****************************************

    def T2_button_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()" , "", "ALL Files (*)", options=QFileDialog.Options())
        color = "color: black"
        if fileName:
            self.T2_textEdit.setText(fileName)
            json_user_object['Parameters']["T2_DATA"]["value"] = fileName
            Ui.update_user_json_file() 
        else:   
            if self.modify_ANTs_groupBox.isChecked() == "False":    
                color = "color: lightGray"

        self.second_metric_groupBox.setStyleSheet(color)
        self.second_fixed_img_comboBox.setStyleSheet(color)
        self.second_fixed_img_label.setStyleSheet(color)
        
        self.second_moving_img_comboBox.setStyleSheet(color)
        self.second_moving_img_label.setStyleSheet(color)

        self.second_metric_weight_label.setStyleSheet(color)
        self.second_metric_weight_spinBox.setStyleSheet(color)

        self.second_radius_label.setStyleSheet(color)
        self.second_radius_spinBox.setStyleSheet(color)



    # *****************************************
    # Remove the selected path and change value of T2 data parameter in json user file
    # *****************************************

    def T2_remove_pushButton_clicked(self):
        self.T2_DATA_textEdit.setText("No file selected.")
        json_user_object['Parameters']["T2_DATA"]["value"] = " "
        Ui.update_user_json_file()




    # *****************************************
    # Button help which display explanations
    # *****************************************

    def question_cortical_labeled_pushButton_clicked(self):
        if self.question_cortical_labeled_pushButton.text() == "Help":
            self.question_cortical_labeled_pushButton.setText("close help")
            self.question_cortical_labeled_textEdit.setStyleSheet("color: blue;"  "background-color: transparent")
        else: # self.question_cortical_labeled_pushButton.text() == "X":
            self.question_cortical_labeled_pushButton.setText("Help")
            self.question_cortical_labeled_textEdit.setStyleSheet("color: transparent;"  "background-color: transparent")




    # *****************************************
    # Button help which display explanations
    # *****************************************

    def NO_registration_question_cortical_labeled_pushButton_clicked(self):
        if self.NO_registration_question_cortical_labeled_pushButton.text() == "Help":
            self.NO_registration_question_cortical_labeled_pushButton.setText("close help")
            self.NO_registration_question_cortical_labeled_textEdit.setStyleSheet("color: blue;"  "background-color: transparent")
        else: # self.NO_registration_question_cortical_labeled_pushButton.text() == "X":
            self.NO_registration_question_cortical_labeled_pushButton.setText("Help")
            self.NO_registration_question_cortical_labeled_textEdit.setStyleSheet("color: transparent;"  "background-color: transparent")




    # *****************************************
    # Open file system and write the white matter right surface path in user information json file
    # *****************************************

    def labelsetname_valuechanged(self):
        json_user_object['Parameters']["labelSetName"]["value"] = self.labelset_lineEdit.text()
        Ui.update_user_json_file()



    # *****************************************
    # Button help which display explanations
    # *****************************************       

    def question_labelset_name_pushButton_clicked(self):
        if self.question_labelset_name_pushButton.text() == "Help":
            self.question_labelset_name_pushButton.setText("close help")
            self.question_labelset_name_textEdit.setStyleSheet("color: blue;"  "background-color: transparent")
            
        else: # self.question_job_name_pushButton.text() == "X":
            self.question_labelset_name_pushButton.setText("Help")
            self.question_labelset_name_textEdit.setStyleSheet("color: transparent;"  "background-color: transparent")    

    

    # *****************************************
    # GroupBox to known if surface is already labeled or not
    # *****************************************  
    def surface_already_labeled_groupBox_clicked(self):
        json_user_object['Parameters']["surface_already_labeled"]["value"] = "true"
        if self.surface_already_labeled_groupBox.isChecked():
            json_user_object['Parameters']["surface_already_labeled"]["value"] = "false"
           
 




    # *****************************************
    # NO registration: GroupBox to known if surface is already labeled or not
    # *****************************************  
    def NO_registration_surface_already_labeled_groupBox_clicked(self):
        json_user_object['Parameters']["surface_already_labeled"]["value"] = "true"
        if self.NO_registration_surface_already_labeled_groupBox.isChecked():
            json_user_object['Parameters']["surface_already_labeled"]["value"] = "false"


    # *****************************************
    # Functions activate if a NO registration cortical left button is clicked
    # *****************************************  

    def NO_registration_cortical_labeled_left_Button_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()" , "", "ALL Files (*)", options=QFileDialog.Options())
        if fileName:
            self.NO_registration_cortical_label_left_textEdit.setText(fileName)
            json_user_object['Parameters']["cortical_label_left"]["value"] = fileName
            Ui.update_user_json_file() 
       


    # *****************************************
    # Functions activate if a NO registration cortical right button is clicked
    # *****************************************  

    def NO_registration_cortical_labeled_right_Button_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()" , "", "ALL Files (*)", options=QFileDialog.Options())
        if fileName:
            self.NO_registration_cortical_label_right_textEdit.setText(fileName)
            json_user_object['Parameters']["cortical_label_right"]["value"] = fileName
            Ui.update_user_json_file() 




















    # *************************************************************************************
    # Interface subcortical tab
    # *************************************************************************************

    # *****************************************
    # Integrate subcortical data or not: write bool in json user file and change interface 
    # *****************************************

    def integrate_sc_data_groupBox_valueChanged(self):
        json_user_object['Parameters']["INTEGRATE_SC_DATA"]["value"] = "False"
        self.question_SALT_pushButton.setStyleSheet( "background-color: white")
        self.question_KWM_pushButton.setStyleSheet( "background-color: white")

        if self.integrate_sc_data_groupBox.isChecked():
            json_user_object['Parameters']["INTEGRATE_SC_DATA"]["value"] = "True"
            self.question_SALT_pushButton.setStyleSheet( "background-color: blue")
            self.question_KWM_pushButton.setStyleSheet( "background-color: blue")
        Ui.update_user_json_file()



    # *****************************************
    # Integrate subcortical data by providing SALT and KWM folders: write bool in json user file and change interface 
    # *****************************************

    def own_sc_groupBox_clicked(self):
        self.question_SALT_pushButton.setStyleSheet( "background-color: white")
        self.question_KWM_pushButton.setStyleSheet( "background-color: white")

        if self.own_sc_groupBox.isChecked():
            json_user_object['Parameters']["INTEGRATE_SC_DATA_by_generated_sc_surf"]["value"] = "False"
            Ui.update_user_json_file()
            self.question_SALT_pushButton.setStyleSheet( "background-color: blue")
            self.question_KWM_pushButton.setStyleSheet( "background-color: blue")
            self.INTEGRATE_SC_DATA_by_generated_sc_surf_groupBox.setChecked(False)

        else: 
            self.INTEGRATE_SC_DATA_by_generated_sc_surf_groupBox.setChecked(True)


        



    # *****************************************
    # Integrate subcortical data but without SALT dir: write bool in json user file and change interface 
    # *****************************************

    def INTEGRATE_SC_DATA_by_generated_sc_surf_groupBox_clicked(self):
        if self.INTEGRATE_SC_DATA_by_generated_sc_surf_groupBox.isChecked():
            self.own_sc_groupBox.setChecked(False)

            json_user_object['Parameters']["INTEGRATE_SC_DATA_by_generated_sc_surf"]["value"] = "True"
            Ui.update_user_json_file()


            self.question_SALT_pushButton.setStyleSheet( "background-color: white")
            self.question_KWM_pushButton.setStyleSheet( "background-color: white")

        else: 
            self.own_sc_groupBox.setChecked(True)
            self.question_SALT_pushButton.setStyleSheet( "background-color: blue")
            self.question_KWM_pushButton.setStyleSheet( "background-color: blue")





    # *****************************************
    # Open file system and write the KWM path in user information json file + handle the choice of subcortical regions : 
    # *****************************************

    def SALT_button_clicked(self):
        DirName= QtWidgets.QFileDialog.getExistingDirectory(self)
        if DirName:
            self.SALTDir_textEdit.setText(DirName) 
            json_user_object['Parameters']["SALTDir"]["value"] = DirName
            Ui.update_user_json_file() 



    # *****************************************
    # Open file system and write the KWM path in user information json file + handle the choice of subcortical regions: 
    # *****************************************

    def KWM_button_clicked(self):
        DirName= QtWidgets.QFileDialog.getExistingDirectory(self)
        if DirName:
            # Modify Qt interface
            self.KWMDir_textEdit.setText(DirName) 

            # Modify .json
            json_user_object['Parameters']["KWMDir"]["value"] = DirName
            Ui.update_user_json_file() 



    # *****************************************
    # Display subcortical regions names:
    # *****************************************

    def tab_name_sc_region_clicked(self):
        if self.SALTDir_textEdit.toPlainText() != "No file selected." and self.KWMDir_textEdit.toPlainText() != "No file selected.":

            # Initiate subcorticalsList parameter                        
            json_user_object['Parameters']["subcorticalsList"]["value"] = ""
            Ui.update_user_json_file()

            # Create new dir:
            if not os.path.exists(json_user_object['Parameters']["OUT_PATH"]["value"]):
                os.mkdir(json_user_object['Parameters']["OUT_PATH"]["value"])

            if not os.path.exists(os.path.join(json_user_object['Parameters']["OUT_PATH"]["value"], json_user_object['Parameters']["ID"]["value"])):
                os.mkdir(os.path.join(json_user_object['Parameters']["OUT_PATH"]["value"], json_user_object['Parameters']["ID"]["value"]))

            if not os.path.exists(os.path.join(json_user_object['Parameters']["OUT_PATH"]["value"], json_user_object['Parameters']["ID"]["value"], "Salt")):
                os.mkdir(os.path.join(json_user_object['Parameters']["OUT_PATH"]["value"], json_user_object['Parameters']["ID"]["value"], "Salt"))

            # Path to new folder: 
            SALTDir_new = os.path.join(json_user_object['Parameters']["OUT_PATH"]["value"], json_user_object['Parameters']["ID"]["value"], "Salt","Salt_new" )
            KWMDir_new = os.path.join(json_user_object['Parameters']["OUT_PATH"]["value"], json_user_object['Parameters']["ID"]["value"], "Salt","KWM_new")

            list_sc_region_SALT_original = organize_SALT_dir(json_user_object['Parameters']["ID"]["value"], 
                                                            json_user_object['Parameters']["SALTDir"]["value"],
                                                            SALTDir_new,
                                                            json_user_object['Parameters']["PARCELLATION_TABLE"]["value"])
            list_sc_region_KWM_original = organize_KWM_dir(json_user_object['Parameters']["ID"]["value"], 
                                                            json_user_object['Parameters']["KWMDir"]["value"],
                                                            KWMDir_new,
                                                            json_user_object['Parameters']["PARCELLATION_TABLE"]["value"]) 
            '''
            # Extract regions in both folder
            list_sc_region_SALT = sorted(Ui.extract_name_sc_region(self, SALTDir_new))
            #print("SALT:",list_sc_region_SALT)
            list_sc_region_KWM = sorted(Ui.extract_name_sc_region(self,KWMDir_new))
            #print("KWM: ",list_sc_region_KWM)
            '''

            region_only_SALTDir = []
            region_only_KWMDir = []
        
            # Compare lists to extract common regions: 
            for region_SALT in list_sc_region_SALT_original :
                if not(region_SALT in list_sc_region_KWM_original): #a of list_sc_region_SALT isn't in list_sc_region_KWM
                    region_only_SALTDir.append(region_SALT)
         
            for region_KWM in list_sc_region_KWM_original :
                if not(region_KWM in list_sc_region_SALT_original): #b of list_sc_region_KWM isn't in list_sc_region_SALT
                    region_only_KWMDir.append(region_KWM)

            # Concatenate all regions without copie
            global all_sc_region
            all_sc_region = sorted(list_sc_region_SALT_original + region_only_KWMDir)

            # Create layout inside a groupBox
            self.sc_gridLayouttest = QGridLayout()
            self.list_sc_groupBox.setLayout(self.sc_gridLayouttest)

            # Add color code explanation
            self.color_sc_textEdit.setText('<font color="green">Checkbox in green</font>: file for this region in the SALT and KWM directory \n' + 
                                           '<font color="red">Checkbox in red</font>: file for this region only in the KWM directory \n' + '\n'
                                           '<font color="purple">Checkbox in purple</font>: file for this region only in the SALT directory') 

            # Create checkBox for each region and change their color
            positions = [(i, j) for i in range(6) for j in range( int(len(all_sc_region)/6)+1)]
            for position, name in zip(positions, all_sc_region):
                # create checkbox: 
                my_name = "CheckBox" + name
                self.my_name = QCheckBox(name, self)
                self.sc_gridLayouttest.addWidget(self.my_name, *position )

                if name not in region_only_SALTDir and name not in region_only_KWMDir: #both directory 
                    self.my_name.setStyleSheet("color: green")
                    self.my_name.setChecked(True)

                    # Modify .json
                    json_user_object['Parameters']["subcorticalsList"]["value"] = json_user_object['Parameters']["subcorticalsList"]["value"] + self.my_name.text()  + " "
                    Ui.update_user_json_file()

                elif name in region_only_SALTDir: 
                    self.my_name.setStyleSheet("color: purple") 

                else: #if name in region_only_KWMDir:
                    self.my_name.setStyleSheet("color: red")

                


    # *****************************************
    # Extract name of subcortical region 
    # *****************************************

    def extract_name_sc_region(self,fileDir):
        list_sc_region = []
        for entry in os.listdir(fileDir):
            if os.path.isdir(os.path.join(fileDir, entry)):  #is directory  
                if entry.startswith("sub") or entry.startswith( "brain"):  # error if you remove one of this 'if' with an 'and'
                        list_sc_region.append(str(entry))
        return list_sc_region


    # *****************************************
    # Button help which display explanations
    # *****************************************       

    def question_SALT_pushButton_clicked(self):
        if self.question_SALT_pushButton.text() == "Help":
            self.question_SALT_pushButton.setText("close help")
            self.question_SALT_textEdit.setText('SALT directory : directory with one subfolder per subcortical <font color="red">region</font>. '+
                                                'In each subfolder, you need to provide a file with a name like that: "job_name-T1_SkullStripped_scaled_label_'+
                                                '<font color="red">region</font>_..."  \n where "job_name" is the same name that specify in the first tab')
            self.question_SALT_textEdit.setStyleSheet("color: blue;"  "background-color: transparent")
        else: # self.question_job_name_pushButton.text() == "X":
            self.question_SALT_pushButton.setText("Help")
            self.question_SALT_textEdit.setText("")
            self.question_SALT_textEdit.setStyleSheet("color: transparent;"  "background-color: transparent")



    # *****************************************
    # Button help which display explanations
    # *****************************************             

    def question_KWM_pushButton_clicked(self):
        if self.question_KWM_pushButton.text() == "Help":
            self.question_KWM_pushButton.setText("close help")
            self.question_KWM_textEdit.setText('KWM directory : directory with a txt file per subcortical region. For each subcortical region, you need to provide a file' +
                                               ' which contains the name of the subcortical region in his name.')
            self.question_KWM_textEdit.setStyleSheet("color: blue;"  "background-color: transparent")
        else: # self.question_job_name_pushButton.text() == "X":
            self.question_KWM_pushButton.setText("Help")
            self.question_KWM_textEdit.setText("")
            self.question_KWM_textEdit.setStyleSheet("color: transparent;"  "background-color: transparent")



    # *****************************************
    # Complete table with labels and names
    # *****************************************  

    def complete_table_label_name_sc_region(self): 
        global table_created
        table_created = 'false'

        '''
        list_subcortical_regions_lower, list_subcortical_regions_right, list_subcortical_regions_left  = ([],[],[])
   
        for i in range(len(list_subcortical_regions)):
                     
            if list_subcortical_regions[i] != "Brainstem":
                list_subcortical_regions_lower.append(list_subcortical_regions[i].lower())
                new_i_r = "sub_rh_" + list_subcortical_regions[i].lower()
                new_i_l = "sub_lh_" + list_subcortical_regions[i].lower()

                list_subcortical_regions_right.append(new_i_r)
                list_subcortical_regions_left.append(new_i_l)
                
            else: 
                list_subcortical_regions_lower.append(list_subcortical_regions[i])
                new_i_r = list_subcortical_regions[i]

                list_subcortical_regions_right.append(new_i_r)
           
        #print('list_subcortical_regions_lower', list_subcortical_regions_lower)
        #print('list_subcortical_regions_right', list_subcortical_regions_right)
        #print('list_subcortical_regions_left', list_subcortical_regions_left)


        with open(json_user_object['Parameters']["PARCELLATION_TABLE"]["value"], "r") as table_sc_json_file:
            table_sc_json_object = json.load(table_sc_json_file)

        list_name_label_left, list_name_label_right = ([],[])

        for key in table_sc_json_object:        
            if key["name"] in list_subcortical_regions_right: 
                for part_name in key["name"].split('_'): 
                    if part_name in list_subcortical_regions_lower:
                        list_name_label_right.append(key["name"] + " " + part_name + " " + key["labelValue"] ) #sub_rh_gp"

            elif key["name"] in list_subcortical_regions_left:
                for part_name in key["name"].split('_'): 
                    if part_name in list_subcortical_regions_lower:
                        list_name_label_left.append(key["name"] + " " + part_name + " " + key["labelValue"] ) 

        print("list_name_label_right:", list_name_label_right) #['amy 12176', 'caud 12177', 'hippo 12178', 'thal 12179', 'put 12180', 'gp 12181', 'Brainstem 12182']
        print("list_name_label_left:", list_name_label_left) #['amy 11176', 'caud 11177', 'hippo 11178', 'thal 11179', 'put 11180', 'gp 11181']

        #list_name_label_right: ['sub_rh_amy amy 12176', 'sub_rh_caud caud 12177', 'sub_rh_hippo hippo 12178', 'sub_rh_thal thal 12179', 
        #                        'sub_rh_put put 12180', 'sub_rh_gp gp 12181', 'Brainstem Brainstem 12182']
        #list_name_label_left: ['sub_lh_amy amy 11176', 'sub_lh_caud caud 11177', 'sub_lh_hippo hippo 11178', 'sub_lh_thal thal 11179', 
        #                       'sub_lh_put put 11180', 'sub_lh_gp gp 11181']

        for the_region in range(len(list_subcortical_regions_lower)): 

            for left_region_name_label in list_name_label_left:
                split = left_region_name_label.split(' ')
                if split[1] == list_subcortical_regions_lower[the_region]:
                    self.table_sc_regions_tableWidget.setItem(the_region, 0, QTableWidgetItem(split[0]))  #0: name/ID left 
                    self.table_sc_regions_tableWidget.setItem(the_region, 1, QTableWidgetItem(split[2]))  #1: label/number left

            for right_region_name_label in list_name_label_right:
                split = right_region_name_label.split(' ')
                if split[1] == list_subcortical_regions_lower[the_region]:
                    self.table_sc_regions_tableWidget.setItem(the_region, 2, QTableWidgetItem(split[0]))  #2: name/ID right 
                    self.table_sc_regions_tableWidget.setItem(the_region, 3, QTableWidgetItem(split[2]))  #3: label/number right
        '''
        
        global list_subcortical_regions
        list_subcortical_regions = [ 'Amy', 'Caud', 'Hippo', 'Thal', 'GP','Put']
    
        self.table_sc_regions_tableWidget.setVerticalHeaderLabels(list_subcortical_regions)
        self.table_sc_regions_tableWidget.setRowCount(len(list_subcortical_regions))
        self.table_sc_regions_tableWidget.setColumnCount(4)

        Labels = list(json_user_object['Parameters']["subcorticalsListNumber"]["value"].split(" "))
        
        cpt = 0
        for the_region in range(len(list_subcortical_regions)): 
            Label_names_left = list_subcortical_regions[the_region] + 'L'
            Label_names_right = list_subcortical_regions[the_region] + 'R'
            
            self.table_sc_regions_tableWidget.setItem(the_region, 0, QTableWidgetItem(str(Label_names_left)))  #0: name/ID left 
            self.table_sc_regions_tableWidget.setItem(the_region, 1, QTableWidgetItem(str(Labels[cpt])))  #1: label/number left

            self.table_sc_regions_tableWidget.setItem(the_region, 2, QTableWidgetItem(str(Label_names_right)))  #2: name/ID right 
            self.table_sc_regions_tableWidget.setItem(the_region, 3, QTableWidgetItem(str(Labels[cpt + 1])))  #3: label/number right

            cpt += 2

        table_created = 'true'



    # *****************************************
    # Select the labeled image
    # *****************************************

    def select_labeled_image(self): 
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()" , "", "ALL Files (*)", options=QFileDialog.Options())
        if fileName:
            self.labeled_image_textEdit.setText(fileName)
            json_user_object['Parameters']["labeled_image"]["value"] = fileName
            Ui.update_user_json_file()


    # *****************************************
    # Update labels
    # *****************************************

    def update_label_number(self): 
        if table_created == 'true': 
            new_label = []
            new_number = []
            error = 'False'
            for row in range(self.table_sc_regions_tableWidget.rowCount()):
              for column in range(self.table_sc_regions_tableWidget.columnCount()):

                item = self.table_sc_regions_tableWidget.item(row, column).text()
                
                #print(f'row: {row}, column: {column}, item={item}')
                #row: 0, column: 0, item=AmyL    row: 0, column: 1, item=1   row: 0, column: 2, item=AmyR   row: 0, column: 3, item=2   row: 1, column: 0, item=CaudL
                
                if column % 2 == 0: #column 0, 2 : label/name
                    new_label.append(item)
                else: 
                    if item.isdigit(): 
                        new_number.append(int(item))
                    else: 
                        error = 'True'
                        if column == 1: 
                            help = "LEFT"
                        else: 
                            help = 'RIGHT'
                        self.check_table.setText('<font color="red"> Row \'' + str(list_subcortical_regions[row]) 
                                                + '\' , column \'label/number ' + help + '\' ' 
                                                + ' : write an integrer please </font> ')

                     

            if error != 'True': 
                self.check_table.setText(" ")
            else: 
                json_user_object['Parameters']["subcorticalsList"]["value"] = " ".join(new_label)
                print( " ".join(new_label))
                Ui.update_user_json_file()

            print(new_label)
            print(new_number)

            















    # *************************************************************************************
    # Interface registration (ANTs) tab
    # *************************************************************************************
    # *****************************************
    # To change default value: Qt interface information write in json file with user information
    # *****************************************

    def convert_metric_parameter_Qt_to_json(Qt_param):
        dict_param = {"FA in nrrd space ":"FA_NRRD",
                      "T1":"T1_DATA",
                      "T2":"T2_DATA",
                      "BO bias correct in nrrd space":"B0_BiasCorrect_NRRD"}
        return dict_param[Qt_param]



    # *****************************************
    # If T2 data are missing: modify interface 
    # *****************************************

    def modify_ANTs_groupBox_checked(self): 
        color = "color: lightGray"
        if self.modify_ANTs_groupBox.isChecked() and (self.T2_DATA_textEdit.toPlainText() != "No file selected."): 
            color = "color: black"

        self.second_metric_groupBox.setStyleSheet(color)
        self.second_fixed_img_comboBox.setStyleSheet(color)
        self.second_fixed_img_label.setStyleSheet(color)
        self.second_moving_img_comboBox.setStyleSheet(color)
        self.second_moving_img_label.setStyleSheet(color)
        self.second_metric_weight_label.setStyleSheet(color)
        self.second_metric_weight_spinBox.setStyleSheet(color)
        self.second_radius_label.setStyleSheet(color)
        self.second_radius_spinBox.setStyleSheet(color)



    # *****************************************
    # Write the value for upsampling parameter (given by the user) in the user information json file
    # *****************************************         

    def upsampling_checkbox_stateChanged(self):
        json_user_object['Parameters']["UPSAMPLING_DWI"]["value"] = "false"
        if self.upsampling_checkBox.isChecked():
            json_user_object['Parameters']["UPSAMPLING_DWI"]["value"] = "true"        
        Ui.update_user_json_file()                  



    # *****************************************
    # ANTs: write the value for first/second fixed and moving image parameter (given by the user) in the user information json file
    # *****************************************  

    def first_fixed_img_currentTextChanged(self):
        json_user_object['Parameters']["first_fixed_img"]["value"] = Ui.convert_metric_parameter_Qt_to_json(self.first_fixed_img_comboBox.currentText() )
        Ui.update_user_json_file()

    def first_moving_img_currentTextChanged(self):
        json_user_object['Parameters']["first_moving_img"]["value"] = Ui.convert_metric_parameter_Qt_to_json(self.first_moving_img_comboBox.currentText() )
        Ui.update_user_json_file()

    def second_fixed_img_currentTextChanged(self):
        json_user_object['Parameters']["second_fixed_img"]["value"] = Ui.convert_metric_parameter_Qt_to_json(self.second_fixed_img_comboBox.currentText() )
        Ui.update_user_json_file()

    def second_moving_img_currentTextChanged(self):
        json_user_object['Parameters']["second_moving_img"]["value"] = Ui.convert_metric_parameter_Qt_to_json(self.second_moving_img_comboBox.currentText() )
        Ui.update_user_json_file()



    # *****************************************
    # ANTs: write the value for first/second metric weight and radius parameters (given by the user) in the user information json file
    # ***************************************** 

    def first_metric_weight_valueChanged(self):
        json_user_object['Parameters']["first_metric_weight"]["value"] = self.first_metric_weight_spinBox.value()
        Ui.update_user_json_file()

    def first_radius_valueChanged(self):
        json_user_object['Parameters']["first_radius"]["value"] = self.first_radius_spinBox.value()
        Ui.update_user_json_file()

    def second_metric_weight_valueChanged(self):
        json_user_object['Parameters']["second_metric_weight"]["value"] = self.second_metric_weight_spinBox.value()
        Ui.update_user_json_file()

    def second_radius_valueChanged(self):
        json_user_object['Parameters']["second_radius"]["value"] = self.second_radius_spinBox.value()
        Ui.update_user_json_file()



    # *****************************************
    # ANTs: write the value for gradient field sigma and deformation field sigma parameters (given by the user) in the user information json file
    # ***************************************** 

    def gradient_field_sigma_valueChanged(self):
        json_user_object['Parameters']["gradient_field_sigma"]["value"] = self.gradient_field_sigma_doubleSpinBox.value()
        Ui.update_user_json_file()

    def deformation_field_sigma_valueChanged(self):
        json_user_object['Parameters']["deformation_field_sigma"]["value"] = self.deformation_field_sigma_doubleSpinBox.value()
        Ui.update_user_json_file()



    # *****************************************
    # ANTs: write the value for iteration 1, 2 and 3 parameters (given by the user) in the user information json file
    # ***************************************** 

    def iteration1_valueChanged(self):
        json_user_object['Parameters']["iteration1"]["value"] = self.iteration1_spinBox.value()
        Ui.update_user_json_file()

    def iteration2_valueChanged(self):
        json_user_object['Parameters']["iteration2"]["value"] = self.iteration2_spinBox.value()
        Ui.update_user_json_file()

    def iteration3_valueChanged(self):
        json_user_object['Parameters']["iteration3"]["value"] = self.iteration3_spinBox.value()
        Ui.update_user_json_file()



    # *****************************************
    # ANTs: write the value for Syn parameters (given by the user) in the user information json file
    # ***************************************** 

    def Syn_parameter_valueChanged(self):
        json_user_object['Parameters']["SyN_param"]["value"] = self.SyN_param_doubleSpinBox.value()
        Ui.update_user_json_file()


















    # *************************************************************************************
    # Interface NOT registration tab
    # *************************************************************************************

    # *****************************************
    # Do registration or not: write bool in json user file
    # *****************************************

    def registration_tab2_groupBox_valueChanged(self): 
        self.registration_tab1_groupBox.setChecked(True)
        Ui.no_registration_surface_data_clicked(self)
        Ui.no_registration_surface_data_clicked2(self)
        json_user_object['Parameters']["DO_REGISTRATION"]["value"] = "True" 

        if self.registration_tab2_groupBox.isChecked():
            self.registration_tab1_groupBox.setChecked(False)
            Ui.no_registration_surface_data_clicked(self)
            Ui.no_registration_surface_data_clicked2(self)
            json_user_object['Parameters']["DO_REGISTRATION"]["value"] = "False" 
        Ui.update_user_json_file()



    # *****************************************
    # No registration: provide NOT combined left/right surface 
    # *****************************************

    def no_registration_surface_data_clicked(self): 
        color = "color: lightGray"  
        self.WML_surface_diffusion_label.setText("White Matter Left surface data in diffusion space (.vtk):")
        self.WMR_surface_diffusion_label.setText("White Matter Right surface data in diffusion space (.vtk):")
        self.no_registration_surface_diffusion_label.setText('Surface data labeled in diffusion space (.vtk):')     
        self.no_registration_surface_diffusion_label.setStyleSheet(color) 

        if self.registration_tab2_groupBox.isChecked():
            if self.left_right_not_combined_groupBox.isChecked():

                self.left_right_combined_groupBox.setChecked(False)
                color = "color: black"
                self.WML_surface_diffusion_label.setText('White Matter Left surface data <font color="red">in diffusion space</font> (.vtk):')
                self.WMR_surface_diffusion_label.setText('White Matter Right surface data <font color="red">in diffusion space</font> (.vtk):')
   
                json_user_object['Parameters']["left_right_surface_need_to_be_combining"]["value"] = "True" 

            else:
                self.left_right_combined_groupBox.setChecked(True)
                color = "color: lightGray"
                self.no_registration_surface_diffusion_label.setStyleSheet("color: black")
                self.no_registration_surface_diffusion_label.setText('Surface data labeled <font color="red">in diffusion space</font> (.vtk):')

                json_user_object['Parameters']["left_right_surface_need_to_be_combining"]["value"] = "False"                    

        self.WML_surface_diffusion_label.setStyleSheet(color)
        self.WMR_surface_diffusion_label.setStyleSheet(color)         



    # *****************************************
    # No registration: provide combined left/right surface 
    # *****************************************

    def no_registration_surface_data_clicked2(self): 
        color = "color: lightGray"
        self.WML_surface_diffusion_label.setText("White Matter Left surface data in diffusion space (.vtk):")
        self.WMR_surface_diffusion_label.setText("White Matter Right surface data in diffusion space (.vtk):")
        self.no_registration_surface_diffusion_label.setText('Surface data labeled in diffusion space (.vtk):')
        self.no_registration_surface_diffusion_label.setStyleSheet(color)

        if self.registration_tab2_groupBox.isChecked():
            if self.left_right_combined_groupBox.isChecked():

                self.left_right_not_combined_groupBox.setChecked(False)
                color = "color: lightGray"
                self.no_registration_surface_diffusion_label.setStyleSheet("color: black")
                self.no_registration_surface_diffusion_label.setText('Surface data labeled <font color="red">in diffusion space</font> (.vtk):')

                json_user_object['Parameters']["left_right_surface_need_to_be_combining"]["value"] = "False" 
              
            else:
                self.left_right_not_combined_groupBox.setChecked(True)
                color = "color: black"
                self.WML_surface_diffusion_label.setText('White Matter Left surface data <font color="red">in diffusion space</font> (.vtk):')
                self.WMR_surface_diffusion_label.setText('White Matter Right surface data <font color="red">in diffusion space</font> (.vtk):')
                
                json_user_object['Parameters']["left_right_surface_need_to_be_combining"]["value"] = "True"    
        
        self.WML_surface_diffusion_label.setStyleSheet(color)
        self.WMR_surface_diffusion_label.setStyleSheet(color)        



    # *****************************************
    # NO registration: open file system and write the DWI path in user information json file
    # *****************************************

    def no_registration_DWI_button_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()" , "", "ALL Files (*)", options=QFileDialog.Options())
        if fileName:
            self.no_registration_DWI_textEdit.setText(fileName)
            json_user_object['Parameters']["DWI_DATA"]["value"] = fileName
            Ui.update_user_json_file()



    # *****************************************
    # NO registration: open file system and write the DWI bvecs path in user information json file
    # *****************************************

    def no_registration_DWI_bvecs_pushButton(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()" , "", "ALL Files (*)", options=QFileDialog.Options())
        if fileName:
            self.no_registration_DWI_DATA_bvecs_textEdit.setText(fileName)
            json_user_object['Parameters']["DWI_DATA_bvecs"]["value"] = fileName
            Ui.update_user_json_file()



    # *****************************************
    # NO registration: open file system and write the DWI bvals path in user information json file
    # *****************************************

    def no_registration_DWI_bvals_pushButton(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()" , "", "ALL Files (*)", options=QFileDialog.Options())
        if fileName:
            self.no_registration_DWI_DATA_bvals_textEdit.setText(fileName)
            json_user_object['Parameters']["DWI_DATA_bvals"]["value"] = fileName
            Ui.update_user_json_file()






    # *****************************************
    # NO registration: open file system and write the parcellation table path in user information json file
    # *****************************************

    def no_registration_parcellation_table_button_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()" , "", "ALL Files (*)", options=QFileDialog.Options())
        if fileName:
            self.no_registration_parcellation_table_textEdit.setText(fileName) 
            json_user_object['Parameters']["PARCELLATION_TABLE"]["value"] = fileName
            Ui.update_user_json_file()



    # *****************************************
    # Write the value of inner surface boolean in user information json file
    # *****************************************

    def inner_surface_checkBox_checked(self): 
        json_user_object['Parameters']["EXTRA_SURFACE_COLOR"]["value"] = "false"
        if self.inner_surface_checkBox.isChecked(): 
            json_user_object['Parameters']["EXTRA_SURFACE_COLOR"]["value"] = "true"
        Ui.update_user_json_file()



















    # *************************************************************************************
    # Interface diffusion and tractography model tab
    # *************************************************************************************

    # *****************************************
    # Write the number of fibers (bedpostx parameter) in user information json file  
    # *****************************************

    def nb_fibers_spinBox_valueChanged(self):
        json_user_object['Parameters']["nb_fibers"]["value"] = self.nb_fibers_spinBox.value()
        Ui.update_user_json_file()



    # *****************************************
    # Write the number of fibers per seed (probtrackx2 parameter) in user information json file  
    # *****************************************

    def nb_fibers_per_seed_spinBox_valueChanged(self):
        json_user_object['Parameters']["nb_fiber_per_seed"]["value"] = self.nb_fiber_per_seed_spinBox.value()
        Ui.update_user_json_file()



    # *****************************************
    # Write the steplength value (probtrackx2 parameter) in user information json file  
    # *****************************************

    def step_length_doubleSpinBox_valueChanged(self):
        json_user_object['Parameters']["steplength"]["value"] = self.steplength_doubleSpinBox.value()
        Ui.update_user_json_file()



    # *****************************************
    # Write the sampvox value (probtrackx2 parameter) in user information json file  
    # *****************************************

    def sample_doubleSpinBox_valueChanged(self):
        json_user_object['Parameters']["sampvox"]["value"] = self.sampvox_doubleSpinBox.value()
        Ui.update_user_json_file()



    # *****************************************
    # Write the boolean value of ignore label parameters (probtrackx2 parameter) in user information json file  + modify interface
    # *****************************************

    def ignore_label_checkBox_checked(self): 
        self.value_ignore_label_label.setStyleSheet("color: lightGray")
        self.ignore_label_lineEdit.setStyleSheet("background-color: transparent")
        json_user_object['Parameters']["ignoreLabel"]["value"] = "false"

        if self.ignore_label_checkBox.isChecked(): 
            self.value_ignore_label_label.setStyleSheet("color: black")
            self.ignore_label_lineEdit.setStyleSheet("background-color: white")
            json_user_object['Parameters']["ignoreLabel"]["value"] = "true"
        Ui.update_user_json_file()



    # *****************************************
    # Write the name of ignored label (probtrackx2 parameter) in user information json file  
    # *****************************************

    def ignore_label_lineEdit_valueChanged(self):
        if self.ignore_label_checkBox.isChecked():
            json_user_object['Parameters']["ignoreLabel"]["value"] = self.ignore_label_lineEdit.text()
        Ui.update_user_json_file()
     


    # *****************************************
    # Write the boolean value of overlapping parameters (probtrackx2 parameter) in user information json file  
    # *****************************************

    def overlapping_checkBox_checked(self): 
        json_user_object['Parameters']["overlapping"]["value"] = "false"
        if self.overlapping_checkBox.isChecked(): 
            json_user_object['Parameters']["overlapping"]["value"] = "true"
        Ui.update_user_json_file()
       


    # *****************************************
    # Write the boolean value of loopcheck parameters (probtrackx2 parameter) in user information json file 
    # *****************************************

    def loopcheck_checkBox_checked(self): 
        json_user_object['Parameters']["loopcheck"]["value"] = "false"
        if self.loopcheck_checkBox.isChecked(): 
            json_user_object['Parameters']["loopcheck"]["value"] = "true"            
        Ui.update_user_json_file()



    # *****************************************
    # Write the boolean value of filtering_with_tcksift parameters (MRtrix parameter) in user information json file 
    # *****************************************

    def filtering_with_tcksift_checkBox_checked(self): 
        json_user_object['Parameters']["filtering_with_tcksift"]["value"] = "false"
        if self.filtering_with_tcksift_checkBox.isChecked():

            json_user_object['Parameters']["filtering_with_tcksift"]["value"] = "true"  

            if self.optimisation_with_tcksift2_checkBox.isChecked():
                self.optimisation_with_tcksift2_checkBox.isChecked(False)
                json_user_object['Parameters']["optimisation_with_tcksift2"]["value"] = "false"

        Ui.update_user_json_file()


    # *****************************************
    # Write the boolean value of optimisation_with_tcksift2 parameters (MRtrix parameter) in user information json file 
    # *****************************************

    def optimisation_with_tcksift2_checkBox_checked(self): 
        json_user_object['Parameters']["optimisation_with_tcksift2"]["value"] = "false"
        if self.optimisation_with_tcksift2_checkBox.isChecked(): 
            json_user_object['Parameters']["optimisation_with_tcksift2"]["value"] = "true"    

            if self.filtering_with_tcksift_checkBox.isChecked():
                self.filtering_with_tcksift_checkBox.isChecked(False)
                json_user_object['Parameters']["filtering_with_tcksift"]["value"] = "false"


        Ui.update_user_json_file()


    # *****************************************
    # Checkbox to do the -act option
    # ***************************************** 

    def act_checkBox_checked(sefl): 
        json_user_object['Parameters']["act_option"]["value"] = "false"
        if act_checkBox.isChecked(): 
            json_user_object['Parameters']["act_option"]["value"] = "true"
        Ui_visu.update_user_json_file()




















    # *************************************************************************************
    # Interface submit job tab
    # *************************************************************************************

    # *****************************************
    # Open file system and write the output path in user information json file
    # *****************************************

    def OUT_PATH_button_clicked(self):
        DirName= QtWidgets.QFileDialog.getExistingDirectory(self)
        if DirName:
            self.OUT_PATH_textEdit.setText(DirName) 
        
            json_user_object['Parameters']["OUT_PATH"]["value"] = DirName
            Ui.update_user_json_file() 



    # *****************************************
    # Write the number of threads/core (given by the user) in the user information json file
    # *****************************************

    def number_threads_valueChanged(self):   
        json_user_object['Parameters']["nb_threads"]["value"] = self.nb_threads_spinBox.value()
        Ui.update_user_json_file()



    # *****************************************
    # Open file system and write the json configuration path in user information json file 
    # *****************************************

    def json_config_file_pushButton_clicked(self):
        DirName= QtWidgets.QFileDialog.getExistingDirectory(self)
        if DirName:
            self.json_config_file_textEdit.setText(DirName) 
            json_user_object['Parameters']["json_config_file"]["value"] = DirName
            Ui.update_user_json_file() 


    # *****************************************
    # Button to save the json configuration file
    # *****************************************

    def save_config_file_pushButton_clicked(self):
        shutil.copy(user_json_filename, json_user_object['Parameters']["json_config_file"]["value"]) 
        print("copy done")



    # *****************************************
    # Tractography model: FSL, MRtrxi or DIPY
    # *****************************************

    def tractography_model_comboBox_valueChanged(self):   
        json_user_object['Parameters']["tractography_model"]["value"] = self.tractography_model_comboBox.currentText()
        Ui.update_user_json_file()



    # *****************************************
    # Groupbox to run the script localy
    # *****************************************

    def local_run_checkBox_clicked(self):
        json_user_object['Parameters']["cluster"]["value"] = "True"            
        self.remote_run_groupBox.setChecked(True)

        if self.local_run_groupBox.isChecked():
            json_user_object['Parameters']["cluster"]["value"] = "False"            
            self.remote_run_groupBox.setChecked(False)
        
            

    # *****************************************
    # GroupBox to run the script remotely
    # *****************************************

    def remote_run_checkBox_clicked(self):
        json_user_object['Parameters']["cluster"]["value"] = "True"            
        self.local_run_groupBox.setChecked(True)

        if self.remote_run_groupBox.isChecked():
            json_user_object['Parameters']["cluster"]["value"] = "False"            
            self.local_run_groupBox.setChecked(False)          



    # *****************************************
    # Command line to run the script remotely
    # *****************************************

    def commande_line_cluster_plainTextEdit_textChanged(self):
        json_user_object['Parameters']["cluster_command_line"]["value"] = self.commande_line_cluster_plainTextEdit.toPlainText()



    # *****************************************
    # START TRACTOGRAPHY 
    # *****************************************

    def start_tractography_button_clicked(self):
        # Save subcortical region list in the user json file 
        for checkbox in self.list_sc_groupBox.findChildren(QCheckBox):
            #print('%s: %s' % (checkbox.text(), checkbox.isChecked()))
            if checkbox.isChecked() == True:
                if checkbox.text() not in json_user_object['Parameters']["subcorticalsList"]["value"]:
                   json_user_object['Parameters']["subcorticalsList"]["value"] = json_user_object['Parameters']["subcorticalsList"]["value"] + checkbox.text()  + " "
            else:
                json_user_object['Parameters']["subcorticalsList"]["value"] = json_user_object['Parameters']["subcorticalsList"]["value"].replace(checkbox.text() + " ","")
        Ui.update_user_json_file()

        # Display the begin time
        now = datetime.datetime.now()
        self.start_time_label.setText(now.strftime("Script running since: %Hh:%Mmin , %m-%d-%Y"))

        # Run 4 scripts to do the tractogrphy
        CONTINUITY(user_json_filename)



    # *****************************************
    # Start tractography on longleaf
    # *****************************************

    def start_tractography_remotely_pushButton_clicked(self):
        cluster("./slurm-job", json_user_object['Parameters']["cluster_command_line"]["value"])



    # *****************************************
    # Open log file
    # *****************************************

    def open_log_file_pushButton_clicked(self):
        log_file = os.path.join(json_user_object['Parameters']["OUT_PATH"]["value"], json_user_object['Parameters']["ID"]["value"],"log.txt") 
        Ui.run_command("Open log file", ['xdg-open', log_file]) 



    # *****************************************
    # Open visualisation interface 
    # *****************************************

    def open_visualisation_button_clicked(self):
        Ui.run_command("Open visualization interface", [sys.executable, "./CONTINUITY_QC/main_interface_visualization.py"])
     


    # *****************************************
    # Open Slicer
    # *****************************************

    def open_slicer_first_interface_button_clicked(self):
        Ui.run_command("Open slicer with the first interface", [sys.executable, "./CONTINUITY_QC/slicer_QC.py", user_json_filename])



    # *****************************************
    # Update path of executables
    # *****************************************  

    def update_exec_path(self, button_name):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()" , "", "ALL Files (*)", options=QFileDialog.Options())
        if fileName:
            eval("self." + button_name + "_textEdit.setText(fileName)")
            json_user_object['Executables'][button_name]["value"] = fileName
            Ui.update_user_json_file()



        # *****************************************
        # Activated if an executables buttons is clicked
        # *****************************************  

    def button_exec_path_clicked(self):
        button_name = self.sender().objectName()[:-11]
        Ui.update_exec_path(self, button_name)