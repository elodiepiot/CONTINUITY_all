#!/usr/bin/env python3
import json
import os 
import sys 
import subprocess
from termcolor import colored
import time
import datetime
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QCheckBox, QGridLayout, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib as mpl
import mne
from mne.viz import circular_layout, plot_connectivity_circle
import nrrd

sys.path.insert(1, os.path.split(os.getcwd())[0])  # if you want to open the second interface alone
sys.path.insert(1, os.getcwd())                    # if you want to open the second interface with the first interface

# sys.path.insert(1, '/proj/NIRAL/tools/CONTINUITY/')

from CONTINUITY_functions import *


##########################################################################################################################################
'''  
     CONTINUITY QC interface: functions file
'''  
##########################################################################################################################################

class Ui_visu(QtWidgets.QTabWidget):

    # *****************************************
    # Initialisation
    # *****************************************

    def __init__(self):
        super(Ui_visu, self).__init__()
    
        if os.path.exists('./CONTINUITY_QC/interface_visualization.ui'):      # if you open the second interface with the first interface
            uic.loadUi('./CONTINUITY_QC/interface_visualization.ui', self)
        else:                                                                   # if you open the second interface alone
            uic.loadUi('./interface_visualization.ui', self)

        # Write default values on interface    
        self.setup_default_values()

        self.show()



    # *****************************************
    # Setup default value
    # *****************************************

    def setup_default_values(self):
        # Open json files: 
        global user_json_filename
        if os.path.exists("./CONTINUITY_ARGS/args_main_CONTINUITY.json"): # if you open the second interface with the first interface
            user_json_filename = "./CONTINUITY_ARGS/args_main_CONTINUITY.json"
        else: 
            user_json_filename = "../CONTINUITY_ARGS/args_main_CONTINUITY.json"

        global default_json_filename
        if os.path.exists("./CONTINUITY_ARGS/args_main_CONTINUITY_completed_test.json"):  # if you open the second interface with the first interface
            default_json_filename = "./CONTINUITY_ARGS/args_main_CONTINUITY_completed_test.json" #./CONTINUITY_ARGS/args_setup.json"
        else:
            default_json_filename = "../CONTINUITY_ARGS/args_main_CONTINUITY_completed_test.json" #./CONTINUITY_ARGS/args_setup.json"
 
        
        # Json file which contains values given by the user: 
        with open(user_json_filename, "r") as user_Qt_file:
            global json_user_object
            json_user_object = json.load(user_Qt_file)

        # Json file which contains defaults values
        with open(default_json_filename, "r") as default_Qt_file:
            global json_setup_object
            json_setup_object = json.load(default_Qt_file)

        # Setup default path to access of created files for Slicer:
        self.OUTPUT_path_textEdit.setText(json_user_object['Parameters']["OUT_PATH"]["value"])

        # Setup default path to access to Slicer:
        self.slicer_textEdit.setText(json_user_object['Executables']["slicer"]["value"])


        # Setup default path to visualize connectivity matrix and brain/circle connectome:
        path = os.path.join(json_user_object['Parameters']["OUT_PATH"]["value"], json_user_object['Parameters']["ID"]["value"], "Tractography", 'new_parcellation_table')#, "new_parcellation_table")
        #path = "./input_CONTINUITY/TABLE_AAL_SubCorticals.json"
        self.parcellation_table_textEdit.setText(path)

        overlapName = ""
        if json_user_object['Parameters']["overlapping"]["value"]: 
            overlapName = "_overlapping" 

        # Setup default path to save the connectivity matrix with a specific name:
        loopcheckName = ""
        if json_user_object['Parameters']["loopcheck"]["value"]: 
            loopcheckName = "_loopcheck"
            
        path = os.path.join(json_user_object['Parameters']["OUT_PATH"]["value"], json_user_object['Parameters']["ID"]["value"], "Tractography" )#, "Network" + overlapName + loopcheckName)
        #path = "./input_CONTINUITY"
        self.connectivity_matrix_textEdit.setText(path)

        # Colormap circle connectome: strength of each node
        self.layout_colormap = QGridLayout()
        self.colormap_circle_groupBox.setLayout(self.layout_colormap)

        # Circle connectome
        self.Layoutcircle = QGridLayout()
        self.circle_connectome_groupBox.setLayout(self.Layoutcircle)

        self.fig_file_textEdit.setText(json_user_object['Parameters']["OUT_PATH"]["value"])   

        # Normalize matrix
        self.Layout_normalize_matrix = QGridLayout()
        self.normalize_matrix_groupBox.setLayout(self.Layout_normalize_matrix)

        self.path_normalize_matrix_textEdit.setText(json_user_object['Parameters']["OUT_PATH"]["value"])

        # 2D brain connectome
        self.Layout_brain_connectome = QGridLayout()
        self.brain_connectome_groupBox.setLayout(self.Layout_brain_connectome) 
        self.Layout_brain_connectome.setContentsMargins(0, 0, 0, 0) 

        self.num_slice_axial_label.setText("Slice " + str(self.num_slice_axial_horizontalSlider.value()))
        self.num_slice_sagittal_label.setText("Slice " + str(self.num_slice_sagittal_horizontalSlider.value()))
        self.num_slice_coronal_label.setText("Slice " + str(self.num_slice_coronal_horizontalSlider.value()))

        # 3D brain connectome
        self.Layout_brain_connectome_3D = QGridLayout()
        self.brain_connectome_3D_groupBox.setLayout(self.Layout_brain_connectome_3D)   

        # VTK fiber
        self.Layout_vtk_fiber = QGridLayout()
        self.Layout_vtk_fiber_groupBox.setLayout(self.Layout_vtk_fiber)




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
        run = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = run.communicate()
        print(text_printed, "out: ", colored("\n" + str(out) + "\n", 'green')) 
        print(text_printed, "err: ", colored("\n" + str(err) + "\n", 'red'))



    # *****************************************
    # Executables: write the path for Slicer (given by the user) in the user information json file
    # *****************************************  

    def slicer_path_button_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()" , "", "ALL Files (*)", options=QFileDialog.Options())
        if fileName:
            self.slicer_textEdit.setText(fileName)
            json_user_object['Executables']["slicer"]["value"] = fileName
            Ui_visu.update_user_json_file()



    # *****************************************
    # Write the path of output folder (i.e output of tractography) in user json file
    # ****************************************

    def OUTPUT_path_button_clicked(self):
        DirName= QtWidgets.QFileDialog.getExistingDirectory(self)
        if DirName:
            self.OUTPUT_path_textEdit.setText(DirName)
            json_user_object['Parameters']["OUT_PATH"]["value"] = DirName
            Ui_visu.update_user_json_file()



    # *****************************************
    # Open a script to open Slicer with specific parameters
    # *****************************************

    def open_slicer_clicked(self): 
        if os.path.exists("./CONTINUITY_QC/slicer_QC.py"):
            Ui_visu.run_command("Open slicer with specific parameters", [sys.executable, "./CONTINUITY_QC/slicer_QC.py", user_json_filename])
        else: 
            Ui_visu.run_command("Open slicer with specific parameters", [sys.executable, "./slicer_QC.py", user_json_filename])


    # *****************************************
    # Open a script to open Slicer without specific parameters
    # *****************************************

    def open_slicer_only(self):
        Ui_visu.run_command("Open Slicer without configuration", [json_user_object['Executables']["slicer"]["value"]])



    # *****************************************
    # Convert name of data in comboBox (QT) to name of param in script
    # *****************************************

    def convert_name_data(Qt_param):
        dict_param = {"B0":"B0",
                      "T1 registered":"T1_registered",
                      "T2 registered":"T2_registered",
                      "FA":"FA",
                      "DWI":"DWI",
                      "Registered combined surface":"Registered_combined_surface",
                      "AD":"AD"}
        return dict_param[Qt_param]



    # *****************************************
    # Save type of files which will displayed in Slicer (in the view controllers)
    # *****************************************  

    def update_param(self, comboBox_name):
        json_user_object['View_Controllers'][comboBox_name]["value"] = Ui_visu.convert_name_data( eval("self." + comboBox_name + "_comboBox.currentText()")) 
        Ui_visu.update_user_json_file()


        
    # *****************************************
    # Activated if an view controllers parameters is modify
    # ***************************************** 

    def view_controllers_params_clicked(self):
        comboBox_name = self.sender().objectName()[:-9] # 9 caracter in '_comboBox'
        Ui_visu.update_param(self, comboBox_name) 











        
    # *****************************************
    # Select the parcellation table file WITH subcortical regions  
    # ***************************************** 

    def parcellation_table_pushButton_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()" , "", "ALL Files (*)", options=QFileDialog.Options())
        if fileName:
            self.parcellation_table_textEdit.setText(fileName)
            json_user_object['Parameters']["PARCELLATION_TABLE"]["value"] = fileName



    # *****************************************
    # Display the connectivity matrix with a specific normalization
    # ***************************************** 

    def display_normalize_matrix_pushButton_clicked(self):
        matrix = os.path.join(self.connectivity_matrix_textEdit.toPlainText(), "fdt_network_matrix")

        # Create the last part of the title: 
        overlapName = ""
        if json_user_object['Parameters']["overlapping"]["value"]: 
            overlapName = "_overlapping"

        end_name = ' without Loopcheck and without Overlapping'
        if len(overlapName)>3 and len(json_user_object['Parameters']["loopcheck"]["value"])>3:
            end_name = ' with Loopcheck and with Overlapping'
        elif len(overlapName)<3 and len(json_user_object['Parameters']["loopcheck"]["value"])>3:
            end_name = ' without Loopcheck and with Overlapping'
        elif len(overlapName)>3 and len(json_user_object['Parameters']["loopcheck"]["value"])<3:
            end_name = ' with Loopcheck and without Overlapping'

        # Remove previous plot:
        for i in reversed(range(self.Layout_normalize_matrix.count())): 
            self.Layout_normalize_matrix.itemAt(i).widget().setParent(None)

        # Create global configuration for figure:
        self.fig_normalize_matrix = plt.figure(num=None)
        self.canvas = FigureCanvas(self.fig_normalize_matrix)
        self.Layout_normalize_matrix.addWidget(self.canvas)

        # Add figure and axes:
        ax = self.fig_normalize_matrix.add_subplot(1,1,1)
        ax.set_xlabel('Seeds')
        ax.set_ylabel('Targets')

        # Title:
        start = 'Connectivity matrix for ' + json_user_object['Parameters']["ID"]["value"] + "\n  "
        self.fig_normalize_matrix.suptitle(start + self.type_of_normalization_comboBox.currentText() + "  and symmetrization by " 
                                                 + self.type_of_symmetrization_comboBox.currentText() +'\n' +end_name, fontsize=10)

        # Specific normalization: 
        if self.type_of_normalization_comboBox.currentText()   == "No normalization":
            a = no_normalization(matrix)
        elif self.type_of_normalization_comboBox.currentText() == "Whole normalization":
            a = whole_normalization(matrix)
        elif self.type_of_normalization_comboBox.currentText() == "Row region normalization":
            a = row_region_normalization(matrix)
        elif self.type_of_normalization_comboBox.currentText() == "Row column normalization":
            a = row_column_normalization(matrix)

        # Specific symmetrization: 
        if self.type_of_symmetrization_comboBox.currentText() == "Average":
            a = average_symmetrization(a)
        elif self.type_of_symmetrization_comboBox.currentText() == "Maximum":
            a = maximum_symmetrization(a)
        elif self.type_of_symmetrization_comboBox.currentText() == "Minimum":
            a = minimum_symmetrization(a)

        min_a, max_a  = (np.min(a), np.max(a))

        self.min_a_norm_label.setText(str(min_a))
        self.max_a_norm_label.setText(str("{:e}".format(max_a)))

        # Plotting the correlation matrix:
        vmin, vmaw = (0,0)
        check_before_display = 'True'
        
        if self.vmin_vmax_percentage_checkBox.isChecked(): 
            if not(self.vmax_normalize_matrix_spinBox.value() <=  100 and self.vmin_normalize_matrix_spinBox.value() >= 0):
                self.error_label.setText('<font color="red">Please select 2 values between 0 to 100</font> ')
                check_before_display = 'False'
        
        elif self.vmin_vmax_real_values_checkBox.isChecked(): 
            max_a = float(max_a)
            if not(self.vmax_normalize_matrix_spinBox.value() <=  float(max_a) and self.vmin_normalize_matrix_spinBox.value() >= min_a):
                self.error_label.setText( '<font color="red">Please select 2 values between ' + str(min_a) + ' to ' + str("%.7f" % (max_a))+ '</font>'  )
                check_before_display = 'False'


        elif self.vmin_vmax_regions_checkBox.isChecked():
            nb = np.shape(a)[0] #number of regions
            max_region_display = float(1/(nb*(nb-1)))  
             
            if not(self.vmax_normalize_matrix_spinBox.value() <=  max_region_display and self.vmin_normalize_matrix_spinBox.value() >= min_a):
                self.error_label.setText('<font color="red">Please select 2 values between ' + str(min_a) + ' to ' + str("%.7f" % (max_region_display)) + '</font>')
                check_before_display = 'False'

        else:
            self.error_label.setText( '<font color="red">Please select a type of range </font>'  )


        if check_before_display == "True":
            self.error_label.setText(' ')
            cax = ax.imshow(a, interpolation='nearest', vmin = self.vmin_normalize_matrix_spinBox.value(), vmax = self.vmax_normalize_matrix_spinBox.value())
            self.fig_normalize_matrix.colorbar(cax)



    # *****************************************
    # Select the path to save the connectivity matrix
    # ***************************************** 

    def connectivity_matrix_pushButton_clicked(self):
        DirName= QtWidgets.QFileDialog.getExistingDirectory(self)
        if DirName:
            self.connectivity_matrix_textEdit.setText(DirName)



    # *****************************************
    # Save the connectivity matrix
    # ***************************************** 

    def save_normalize_matrix_pushButton_clicked(self):
        path_name = os.path.join(self.path_normalize_matrix_textEdit.toPlainText(), 'Connectivity_matrix_normalized_' + self.type_of_normalization_comboBox.currentText() 
                                                                                        + "_symmetrization_by_" + self.type_of_symmetrization_comboBox.currentText()+ '.pdf')
        # Save and display:
        self.fig_normalize_matrix.savefig(path_name, format='pdf')
        self.save_normalize_matrix_textEdit.setText("Figure saved here: " + path_name)


    # *****************************************
    # Checkbox to selecte the type of colormap range
    # ***************************************** 

    def checkBox_vmin_vmax_cliked(self): 
        checkbox_name = self.sender().objectName()

        if checkbox_name == "vmin_vmax_percentage_checkBox":
            if self.vmin_vmax_percentage_checkBox.isChecked(): 
                self.vmin_vmax_real_values_checkBox.setChecked(False)
                self.vmin_vmax_regions_checkBox.setChecked(False)
                Ui_visu.display_normalize_matrix_pushButton_clicked(self)


        elif checkbox_name == "vmin_vmax_real_values_checkBox":
            if self.vmin_vmax_real_values_checkBox.isChecked(): 
                self.vmin_vmax_percentage_checkBox.setChecked(False)
                self.vmin_vmax_regions_checkBox.setChecked(False)
                Ui_visu.display_normalize_matrix_pushButton_clicked(self)

        elif checkbox_name == "vmin_vmax_regions_checkBox":
            if self.vmin_vmax_regions_checkBox.isChecked(): 
                self.vmin_vmax_real_values_checkBox.setChecked(False)
                self.vmin_vmax_percentage_checkBox.setChecked(False)
                Ui_visu.display_normalize_matrix_pushButton_clicked(self)

        




        





    # *****************************************
    # Plot circle connectome
    # ***************************************** 

    def plot_circle_connectome(self):
        global display
        display = 'false'

        # *****************************************
        # Extract name of each regions and create a circular layout
        # *****************************************
       
        # Get the parcellation table with cortical and subcortical regions:
        with open(os.path.join(self.parcellation_table_textEdit.toPlainText()), "r") as table_json_file:
            table_json_object = json.load(table_json_file)

        # Init list to extract name of regions:
        global label_names
        label_names, lh_labels, rh_labels = ([], [], [])
      
        for key in table_json_object:
            # List with all regions names:
            label_names.append(key["name"])

            for i in key["name"].split("_"):
                # Label in the left hemi: 
                if i == "lh" or i.endswith('L') :   #L: for AAL table, lh: for Destrieux table
                    lh_labels.append( key["name"])

                # Label in the right hemi: 
                if i == "rh" or i.endswith('R') :  
                    rh_labels.append( key["name"]) 

        # Save the plot order:    matrixRow in json table: set the order in connectivity matrix
        node_order = list()
        node_order.extend(lh_labels[::-1])  # reverse the order
        node_order.extend(rh_labels)

        # Create a circular layout:
        global node_angles
        node_angles = circular_layout(label_names, node_order, start_pos=90, group_boundaries=[0, len(label_names) / 2])


        # *****************************************
        # Get the normalize connectivity matrix
        # *****************************************
        
        matrix = os.path.join(self.connectivity_matrix_textEdit.toPlainText(), "fdt_network_matrix")

        # Specific normalization: 
        if self.type_of_normalization_circle_comboBox.currentText()   == "No normalization":
            connectivity_score = no_normalization(matrix)
        elif self.type_of_normalization_circle_comboBox.currentText() == "Whole normalization":
            connectivity_score = whole_normalization(matrix)
        elif self.type_of_normalization_circle_comboBox.currentText() == "Row region normalization":
            connectivity_score = row_region_normalization(matrix)
        elif self.type_of_normalization_circle_comboBox.currentText() == "Row column normalization":
            connectivity_score = row_column_normalization(matrix)

        # Specific symmetrization: 
        if self.type_of_symmetrization_circle_comboBox.currentText() == "Average":
            connectivity_score = average_symmetrization(connectivity_score)
        elif self.type_of_symmetrization_circle_comboBox.currentText() == "Maximum":
            connectivity_score = maximum_symmetrization(connectivity_score)
        elif self.type_of_symmetrization_circle_comboBox.currentText() == "Minimum":
            connectivity_score = minimum_symmetrization(connectivity_score)
        
        # Transform a list of list into a numpy array:
        global connectivity_matrix
        connectivity_matrix = np.array(connectivity_score)

        global number_total_line
        number_total_line = np.count_nonzero(np.absolute(connectivity_matrix)) #Doc plot_connectivity_circle: n_lines strongest connections (strength=abs(con))
        max_value = np.amax(connectivity_matrix)


        # *****************************************
        # Strenght of each node with a specific colormap
        # *****************************************

        # Remove previous plot for the colormap associated to node features: 
        for i in reversed(range(self.layout_colormap.count())): 
            self.layout_colormap.itemAt(i).widget().setParent(None)
        
        # New plot for the colormap associated to node features: 
        self.fig2 = plt.figure()
        self.canvas = FigureCanvas(self.fig2)
        self.layout_colormap.addWidget(self.canvas)
        
        # Set information for the colormap associated to node features: 
        ax = self.fig2.add_axes([0.1, 0.4, 0.8, 0.4]) # add_axes([xmin,ymin,dx,dy]) 
        vmax = self.vmax_colorbar_spinBox.value() / 100
        vmin = self.vmin_colorbar_spinBox.value() / 100
    
        # Display colorbar: 
        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=plt.cm.RdBu),  cax=ax, orientation='horizontal', ticks=[0, vmax/4, vmax/2, 3*vmax/4, 1])

        # Set type of colormap to color each node: 
        RdBu = plt.cm.get_cmap('RdBu', 12)

        # Compute the strenght of each node: node strength is the sum of weights of links connected to the node
        if self.node_features_comboBox.currentText() == "Strength":
            # Sum of each column, each line and all elem: 
            waytotal_column = sum_column(connectivity_matrix)
            waytotal_line   = sum_line(connectivity_matrix)
            waytotal        = sum_all(connectivity_matrix)
         
            i = 0
            list_val = []
            for line in connectivity_matrix:
                j = 0 
                for val in line:
                    instrength = waytotal_column[j]      #is = sum(CIJ,1);    % instrength = column sum of CIJ: the instrength is the sum of inward link weights 
                    outstrength = waytotal_line[i]       #os = sum(CIJ,2);    % outstrength = row sum of CIJ:   the outstrength is the sum of outward link weights
                    list_val.append(instrength + outstrength) #str = is+os;        % strength = instrength+outstrength
                    j=j+1
                i=i+1

        # Compute the degree of each node: node degree is the number of links connected to the node
        elif self.node_features_comboBox.currentText() == "Degree": 
            # matrix binarised:  ensure CIJ is binary (CIJ = double(CIJ~=0))
            connectivity_matrix_binarize = np.where(connectivity_matrix > 0, 1, 0)  # > threshold, upper,lower

            waytotal_column = sum_column(connectivity_matrix_binarize)
            waytotal_line   = sum_line(connectivity_matrix_binarize)

            i = 0
            list_val = []
            for line in connectivity_matrix_binarize:
                j = 0
                for val in line:
                    indegree = waytotal_column[j]   # id = sum(CIJ,1);    % indegree = column sum of CIJ: the indegree is the number of inward links
                    outdegree = waytotal_line[i]    # od = sum(CIJ,2);    % outdegree = row sum of CIJ:   the outdegree is the number of outward links.  
                    list_val.append(indegree + outdegree)  # deg = id+od;        % degree = indegree+outdegree
                    j=j+1
                i=i+1

        # To normalized between 0 to 1: 
        max_strenght, min_strenght  = (np.amax(list_val), np.amin(list_val))

        # Normalized printed color:
        norm_map = plt.Normalize(vmin, vmax)

        global label_color
        label_color = [] #list
        for i in range(len(list_val)):
            strenght_norm =(list_val[i] - min_strenght) / (max_strenght - min_strenght)  # norm between 0 to 1 

            # Adjust the color to the range of the colormap: 
            if strenght_norm < vmax and strenght_norm > vmin: 
                label_color.append(RdBu(norm_map(strenght_norm)))
            else:
                label_color.append((0,0,0)) #black node


        # *****************************************
        # Display circle connectome
        # *****************************************

        # Remove previous circle plot:
        for i in reversed(range(self.Layoutcircle.count())): 
            self.Layoutcircle.itemAt(i).widget().setParent(None)
        
        # New circle connectome plot: 
        self.fig = plt.figure(facecolor='black')
        self.canvas = FigureCanvas(self.fig)
        self.Layoutcircle.addWidget(self.canvas)

        plot_connectivity_circle(connectivity_matrix, label_names, n_lines = int((self.n_lines_spinBox.value() / 100) * number_total_line),
                                                                   linewidth = self.linewidth_spinBox.value(),
                                                                   vmin = (self.vmin_connectome_spinBox.value() / 100), 
                                                                   vmax = (self.vmax_connectome_spinBox.value() / 100),
                                                                   node_angles = node_angles, 
                                                                   node_colors = tuple(label_color), 
                                                                   fig = self.fig, show = False,
                                                                   colorbar_pos = (- 0.1, 0.1), 
                                                                   fontsize_names = self.textwidth_spinBox.value(),
                                                                   colormap = self.colormap_connectome_comboBox.currentText(),
                                                                   padding = self.padding_spinBox.value(), 
                                                                   node_linewidth = self.nodelinewidth_spinBox.value() )
        # Udpate text in the interface
        if self.wait_label.text() != "done! ": 
            self.wait_label.setText("done! ")
        else:   
            self.wait_label.setText("done again! ")
        self.nb_line_label.setText(str(int((self.n_lines_spinBox.value() / 100) * number_total_line)) + " lines displayed")
        display = 'true'



    # *****************************************
    # Setup the path to save the circle connectome
    # *****************************************

    def fig_file_pushButton_clicked(self):
        DirName= QtWidgets.QFileDialog.getExistingDirectory(self)
        if DirName:
            self.fig_file_textEdit.setText(DirName)



    # *****************************************
    # Save the circle connectome
    # *****************************************

    def save_circle_connectome_pushButton_clicked(self): 
        path_name = os.path.join(self.fig_file_textEdit.toPlainText(), 'Circle_connectome_' + self.type_of_normalization_comboBox.currentText() 
                                                                                            + "_symmetrization_by_" + self.type_of_symmetrization_comboBox.currentText()+ '.pdf')
        # Display and save: 
        self.save_circle_connectome_textEdit.setText("Figure saved here: " + path_name)
        self.fig.savefig(path_name, format='pdf', facecolor='black')



    # *****************************************
    # Update the circle connectome
    # *****************************************

    def update_cirlcle_connectome(self): 
        print("to do")
        '''
        
        if display == 'true': 
            # Remove previous circle plot:
            for i in reversed(range(self.Layoutcircle.count())): 
                self.Layoutcircle.itemAt(i).widget().setParent(None)
            
            # New circle connectome plot: 
            self.fig = plt.figure(facecolor='black')
            self.canvas = FigureCanvas(self.fig)
            self.Layoutcircle.addWidget(self.canvas)

            plot_connectivity_circle(connectivity_matrix, label_names, n_lines = int((self.n_lines_spinBox.value() / 100) * number_total_line),
                                                                       linewidth = self.linewidth_spinBox.value(),
                                                                       vmin = (self.vmin_connectome_spinBox.value() / 100), 
                                                                       vmax = (self.vmax_connectome_spinBox.value() / 100),
                                                                       node_angles = node_angles, 
                                                                       node_colors = tuple(label_color), 
                                                                       fig = self.fig, show = False,
                                                                       colorbar_pos = (- 0.1, 0.1), 
                                                                       fontsize_names = self.textwidth_spinBox.value(),
                                                                       colormap = self.colormap_connectome_comboBox.currentText(),
                                                                       padding = self.padding_spinBox.value(), 
                                                                       node_linewidth = self.nodelinewidth_spinBox.value() )

            self.nb_line_label.setText(str(int((self.n_lines_spinBox.value() / 100) * number_total_line)) + " lines displayed")
        '''


        
        










    # *****************************************
    # Display the axial/sagittal/coronal background of the brain connectome
    # *****************************************

    def background_axial_brain_connectome(self): 
        self.im1.set_data(self.imarray_axial[ self.num_slice_axial_horizontalSlider.value()])
        self.fig_brain_connectome.canvas.draw_idle()
        plt.close()
        self.num_slice_axial_label.setText("Slice " + str(self.num_slice_axial_horizontalSlider.value()))

    def background_sagittal_brain_connectome(self): 
        self.im2.set_data(self.imarray_sagittal[ self.num_slice_sagittal_horizontalSlider.value()])
        self.fig_brain_connectome.canvas.draw_idle()
        plt.close()
        self.num_slice_sagittal_label.setText("Slice " + str(self.num_slice_sagittal_horizontalSlider.value()))

    def background_coronal_brain_connectome(self): 
        self.im3.set_data(self.imarray_coronal[ self.num_slice_coronal_horizontalSlider.value()])
        self.fig_brain_connectome.canvas.draw_idle()
        plt.close()
        self.num_slice_coronal_label.setText("Slice " + str(self.num_slice_coronal_horizontalSlider.value()))
       


    # *****************************************
    # Display the brain connectome
    # ***************************************** 

    def display_brain_connectome_pushButton_clicked(self):
        now = datetime.datetime.now()
        print(now.strftime("Display brain connectome function: %H:%M %m-%d-%Y"))
        start = time.time()

        # *****************************************
        # Setup the view
        # *****************************************

        # Remove previous plot:
        for i in reversed(range(self.Layout_brain_connectome.count())): 
            self.Layout_brain_connectome.itemAt(i).widget().setParent(None)
        
        # Create figure:
        self.fig_brain_connectome = plt.figure(num=None)
        self.canvas = FigureCanvas(self.fig_brain_connectome)
        self.Layout_brain_connectome.addWidget(self.canvas)
        
        # Set title:
        outputfilename = 'Brain connectome of subject ' + json_user_object['Parameters']["ID"]["value"] + ' (connectivity matrix normalized (row-region))'
        self.fig_brain_connectome.suptitle(outputfilename, fontsize=10)

        self.ax1 = self.fig_brain_connectome.add_subplot(1,3,1) #axial
        self.ax2 = self.fig_brain_connectome.add_subplot(1,3,2) #sagittal left or right
        self.ax3 = self.fig_brain_connectome.add_subplot(1,3,3) #coronal

        # Set subtitles: 
        self.ax1.title.set_text("Axial")
        self.ax2.title.set_text("Sagittal right")
        if self.sagittal_left_checkBox.isChecked():
            self.ax2.title.set_text("Sagittal left")
        self.ax3.title.set_text("Coronal")


        # *****************************************
        # Setup the background: slice brain image
        # *****************************************

        # Find localization of images: 
        self.imarray, header = nrrd.read("./CONTINUITY_QC/T0054-1-1-6yr-T1_SkullStripped_scaled.nrrd") 
        
        # Modify the matrix to select a specific orrientation: 
        self.imarray_axial          = np.rot90(self.imarray, k=1, axes=(0, 2))  
        self.imarray_sagittal_left  = np.flip(np.rot90(self.imarray, k=3, axes=(1, 2)) , axis=1)  
        self.imarray_sagittal_right = np.rot90(self.imarray_sagittal_left, k=2, axes=(0, 2)) 
        self.imarray_coronal        = np.rot90(self.imarray_sagittal_right, k=1, axes=(0, 2))  

        # Sagittal view: right or left: 
        self.imarray_sagittal = self.imarray_sagittal_right
        if self.sagittal_left_checkBox.isChecked():
            self.imarray_sagittal = self.imarray_sagittal_left

        # Plot background with a specific slice:
        self.im1 = self.ax1.imshow(self.imarray_axial[self.num_slice_axial_horizontalSlider.value()]) 
        self.im2 = self.ax2.imshow(self.imarray_sagittal[self.num_slice_sagittal_horizontalSlider.value()])
        self.im3 = self.ax3.imshow(self.imarray_coronal[self.num_slice_coronal_horizontalSlider.value()]) 


        # *****************************************
        # Extract data points in connectivity matrix and display points
        # *****************************************
        
        # Get the parcellation table with Cortical and Subcortical regions: 
        with open(os.path.join(self.parcellation_table_textEdit.toPlainText()), "r") as table_json_file:
            table_json_object = json.load(table_json_file)

        list_x               , list_y               , list_z                = ([], [], [])
        list_x_sagittal_left , list_y_sagittal_left , list_z_sagittal_left  = ([], [], [])
        list_x_sagittal_right, list_y_sagittal_right, list_z_sagittal_right = ([], [], [])
        list_x_coronal       , list_y_coronal       , list_z_coronal        = ([], [], [])
        
        # Extract data point for each view (axial, sagittal, coronal)
        for key in table_json_object:   
            # Header of nrrd-file: array([146, 190, 165])
            x = -(key["coord"][0]) + 146/2
            y = -(key["coord"][1]) + 165/2
            z = -(key["coord"][2]) + 190/2

            # Axial and coronal:
            list_x.append(x)
            list_y.append(y)
            list_z.append(z)

            # Sagittal left:
            if x>= 146/2 : 
                y_sagittal_left = -y + 190
                z_sagittal_left = z
                list_x_sagittal_left.append(x)   
                list_y_sagittal_left.append(y_sagittal_left)
                list_z_sagittal_left.append(z_sagittal_left)

                y_sagittal_right = float('nan')
                z_sagittal_right = float('nan')
                list_x_sagittal_right.append(float('nan'))
                list_y_sagittal_right.append(float('nan'))
                list_z_sagittal_right.append(float('nan'))

            # Sagittal right:
            else: 
                y_sagittal_left = float('nan')
                z_sagittal_left = float('nan')
                list_x_sagittal_left.append(float('nan'))
                list_y_sagittal_left.append(float('nan'))    
                list_z_sagittal_left.append(float('nan'))

                y_sagittal_right = y
                z_sagittal_right = z
                list_x_sagittal_right.append(x)    
                list_y_sagittal_right.append(y) 
                list_z_sagittal_right.append(z)

            if self.plot_unconnected_points_CheckBox.isChecked(): 
                # Plot points for axial view: 
                cax1 = self.ax1.plot(x, y, 'brown', marker=".", markersize=8) 

                # Plot points for sagittal view:
                if self.sagittal_left_checkBox.isChecked():
                    cax2 = self.ax2.plot(y_sagittal_left, z_sagittal_left, 'brown', marker=".", markersize=8) #sagittal left
                else:
                    cax2 = self.ax2.plot(y_sagittal_right, z_sagittal_right, 'brown', marker=".", markersize=8) #sagittal right

                # Plot points for coronal view:
                cax3 = self.ax3.plot(x, z , 'brown', marker=".", markersize=8) 


        # *****************************************
        # Get the normalize connectivity matrix: 
        # *****************************************

        matrix = os.path.join(self.connectivity_matrix_textEdit.toPlainText(), "fdt_network_matrix")

        # Specific normalization: 
        if self.type_of_normalization_brain_comboBox.currentText() == "No normalization":
            a = no_normalization(matrix)
        elif self.type_of_normalization_brain_comboBox.currentText() == "Whole normalization":
            a = whole_normalization(matrix)
        elif self.type_of_normalization_brain_comboBox.currentText() == "Row region normalization":
            a = row_region_normalization(matrix)
        elif self.type_of_normalization_brain_comboBox.currentText() == "Row column normalization":
            a = row_column_normalization(matrix)

        # Specific symmetrization: 
        if self.type_of_symmetrization_brain_comboBox.currentText() == "Average":
            a = average_symmetrization(a)
        elif self.type_of_symmetrization_brain_comboBox.currentText() == "Maximum":
            a = maximum_symmetrization(a)
        elif self.type_of_symmetrization_brain_comboBox.currentText() == "Minimum":
            a = minimum_symmetrization(a)
            
        # Transform in a numpy array:
        a = np.array(a)


        # *****************************************
        # Display lines with colors depending of informations in connectivity matrix
        # *****************************************

        # Colorbar vmin and vmaw used to setup the normalization of each color: 
        vmin_axial    = self.min_colorbar_axial_brain_connectome_doubleSpinBox.value() / 100
        vmax_axial    = self.max_colorbar_axial_brain_connectome_doubleSpinBox.value() / 100
        vmin_sagittal = self.min_colorbar_sagittal_brain_connectome_doubleSpinBox.value() / 100
        vmax_sagittal = self.max_colorbar_sagittal_brain_connectome_doubleSpinBox.value() / 100
        vmin_coronal  = self.min_colorbar_coronal_brain_connectome_doubleSpinBox.value() / 100
        vmax_coronal  = self.max_colorbar_coronal_brain_connectome_doubleSpinBox.value() / 100

        # To normalize colors:
        norm_axial    = mpl.colors.Normalize(vmin=vmin_axial,    vmax=vmax_axial)
        norm_sagittal = mpl.colors.Normalize(vmin=vmin_sagittal, vmax=vmax_sagittal)
        norm_coronal  = mpl.colors.Normalize(vmin=vmin_coronal,  vmax=vmax_coronal)

        # Min and max of the connectivity matrix: 
        mmin, mmax = (np.min(a),np.max(a))

        for i in range(np.shape(a)[0]):
            for j in range(np.shape(a)[1]):

                # Normalize:
                my_norm = (a[i,j] - mmin) / (mmax - mmin) #value between 0 to 1 
       
                # Specific threshold for axial lines (give by the range of the colorbar):
                if my_norm <= vmax_axial and my_norm >= vmin_axial:
                    point1 = [list_x[i], list_y[i],list_z[i]]
                    point2 = [list_x[j], list_y[j],list_z[j]]

                    x_values = [point1[0], point2[0]]
                    y_values = [point1[1], point2[1]]

                    # Display lines for axial view: 
                    cax1 = self.ax1.plot(x_values, y_values, lw=1.5, color= plt.cm.RdBu(norm_axial(my_norm)))

                    if not self.plot_unconnected_points_CheckBox.isChecked(): 
                        # Plot connected points for axial view: 
                        cax1 = self.ax1.plot(list_x[i], list_y[i] , 'brown', marker=".", markersize=8) 
                        cax1 = self.ax1.plot(list_x[j], list_y[j] , 'brown', marker=".", markersize=8) 
                    
                # Specific threshold for coronal lines (give by the range of the colorbar):
                if my_norm <= vmax_coronal and my_norm >= vmin_coronal:
                    point1 = [list_x[i], list_y[i],list_z[i]]
                    point2 = [list_x[j], list_y[j],list_z[j]]

                    x_values = [point1[0], point2[0]]
                    z_values = [point1[2], point2[2]]

                    # Display lines for coronal view: 
                    cax3 = self.ax3.plot(x_values, z_values, lw=1.5, color= plt.cm.RdBu(norm_coronal(my_norm)))

                    if not self.plot_unconnected_points_CheckBox.isChecked(): 
                        # Plot points for coronal view:
                        cax3 = self.ax3.plot(list_x[i], list_z[i] , 'brown', marker=".", markersize=8)
                        cax3 = self.ax3.plot(list_x[j], list_z[j] , 'brown', marker=".", markersize=8) 

                # Specific threshold for sagittal slice (give by the range of the colorbar):
                if my_norm <= vmax_sagittal and my_norm >= vmin_sagittal:

                    if self.sagittal_left_checkBox.isChecked():
                        point1_sagittal_left = [list_x_sagittal_left[i], list_y_sagittal_left[i],list_z_sagittal_left[i]]
                        point2_sagittal_left = [list_x_sagittal_left[j], list_y_sagittal_left[j],list_z_sagittal_left[j]]

                        y_values_sagittal_left = [point1_sagittal_left[1], point2_sagittal_left[1]]
                        z_values_sagittal_left = [point1_sagittal_left[2], point2_sagittal_left[2]]

                        # Display lines for sagittal left view: 
                        cax2 = self.ax2.plot(y_values_sagittal_left,  z_values_sagittal_left , lw=1.5, color= plt.cm.RdBu(norm_sagittal(my_norm))) 

                        if not self.plot_unconnected_points_CheckBox.isChecked(): 
                            # Plot points for sagittal left  view:
                            cax2 = self.ax2.plot(list_y_sagittal_left[i], list_z_sagittal_left[i], 'brown', marker=".", markersize=8) #sagittal left
                            cax2 = self.ax2.plot(list_y_sagittal_left[j], list_z_sagittal_left[j], 'brown', marker=".", markersize=8) #sagittal left

                    else: 
                        point1_sagittal_right = [list_x_sagittal_right[i], list_y_sagittal_right[i],list_z_sagittal_right[i]]
                        point2_sagittal_right = [list_x_sagittal_right[j], list_y_sagittal_right[j],list_z_sagittal_right[j]]

                        y_values_sagittal_right = [point1_sagittal_right[1], point2_sagittal_right[1]]
                        z_values_sagittal_right = [point1_sagittal_right[2], point2_sagittal_right[2]]

                        # Display lines for sagittal right view: 
                        cax2 = self.ax2.plot(y_values_sagittal_right, z_values_sagittal_right, lw=1.5, color= plt.cm.RdBu(norm_sagittal(my_norm))) 
                        
                        if not self.plot_unconnected_points_CheckBox.isChecked(): 
                            # Plot points for sagittal left  view:
                            cax2 = self.ax2.plot(list_y_sagittal_right[i], list_z_sagittal_right[i], 'brown', marker=".", markersize=8) #sagittal right
                            cax2 = self.ax2.plot(list_y_sagittal_right[j], list_z_sagittal_right[j], 'brown', marker=".", markersize=8) #sagittal right
                                

        # *****************************************
        # Setup and display colorbar
        # *****************************************

        # Set colorbar position
        p0 = self.ax1.get_position().get_points().flatten()
        p1 = self.ax2.get_position().get_points().flatten()
        p2 = self.ax3.get_position().get_points().flatten()
      
        ax1_cbar = self.fig_brain_connectome.add_axes([p0[0], 0.07, p0[2]-p0[0]-0.03, 0.03])  #add_axes([xmin,ymin,dx,dy]) 
        ax2_cbar = self.fig_brain_connectome.add_axes([p1[0], 0.07, p1[2]-p1[0]-0.03, 0.03])  
        ax3_cbar = self.fig_brain_connectome.add_axes([p2[0], 0.07, p2[2]-p2[0]-0.03, 0.03]) 

        # Display colorbar
        plt.colorbar(mpl.cm.ScalarMappable(norm=norm_axial,    cmap=plt.cm.RdBu),  cax=ax1_cbar, orientation='horizontal')
        plt.colorbar(mpl.cm.ScalarMappable(norm=norm_sagittal, cmap=plt.cm.RdBu),  cax=ax2_cbar, orientation='horizontal')
        plt.colorbar(mpl.cm.ScalarMappable(norm=norm_coronal,  cmap=plt.cm.RdBu),  cax=ax3_cbar, orientation='horizontal')

        print("End display brain connectome: ",time.strftime("%H h: %M min: %S s",time.gmtime( time.time() - start )))

     







    
       
    



    # *****************************************
    # Display the 3D brain connectome THE FIRST TIME
    # ***************************************** 

    def display_brain_connectome_3D_pushButton_clicked(self):
        now = datetime.datetime.now()
        print(now.strftime("Display 3D brain connectome function: %H:%M %m-%d-%Y"))
        start = time.time()

        # *****************************************
        # Get the connectivity matrix
        # *****************************************

        matrix = os.path.join(self.connectivity_matrix_textEdit.toPlainText(), "fdt_network_matrix") 
      
        # Specific normalization: 
        global a 
        if self.type_of_normalization_brain_comboBox.currentText() == "No normalization":
            a = no_normalization(matrix)
        elif self.type_of_normalization_brain_comboBox.currentText() == "Whole normalization":
            a = whole_normalization(matrix)
        elif self.type_of_normalization_brain_comboBox.currentText() == "Row region normalization":
            a = row_region_normalization(matrix)
        elif self.type_of_normalization_brain_comboBox.currentText() == "Row column normalization":
            a = row_column_normalization(matrix)

        # Specific symmetrization: 
        if self.type_of_symmetrization_brain_comboBox.currentText() == "Average":
            a = average_symmetrization(a)
        elif self.type_of_symmetrization_brain_comboBox.currentText() == "Maximum":
            a = maximum_symmetrization(a)
        elif self.type_of_symmetrization_brain_comboBox.currentText() == "Minimum":
            a = minimum_symmetrization(a)
      
        # Transform in a numpy array: 
        a = np.array(a)

        # Range colorbar and normalization:
        vmin_3D, vmax_3D = ( self.min_colorbar_brain_3D_connectome_doubleSpinBox.value() / 100, self.max_colorbar_brain_3D_connectome_doubleSpinBox.value() / 100)
        norm_3D = mpl.colors.Normalize(vmin=vmin_3D, vmax=vmax_3D)

        # To normalize colors of lines: 
        global mmin, mmax
        mmin, mmax = (np.min(a),np.max(a))
        self.min_a_3D_label.setText(str(mmin))
        self.max_a_3D_label.setText(str(mmax))
        

        # *****************************************
        # Setup figure parameters: remove the previous plot: 
        # *****************************************

        for i in reversed(range(self.Layout_brain_connectome_3D.count())): 
            self.Layout_brain_connectome_3D.itemAt(i).widget().setParent(None)


        # *****************************************
        # Get path to brain surfaces and read the file
        # *****************************************
        
        SURFACE_template = './CONTINUITY_QC/surface_template/surface_template.vtk'
        if not os.path.exists(SURFACE_template): 
            SURFACE_template = './surface_template/surface_template.vtk'

        # Create template surfaces: visualization independente of subject:  (only cortical surfaces but is good for juste visualized)
        #polydatamerge('./CONTINUITY_QC/surface_template/icbm_avg_mid_sym_mc_left.vtk', './CONTINUITY_QC/surface_template/icbm_avg_mid_sym_mc_right.vtk', SURFACE_template)
        # Compute point for Destrieux: function in CONTINUITY_functions.py and use in CONTINUITY_completed_script.py

        # Read the brain surfaces file:
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(SURFACE_template)
        reader.Update() 


        # *****************************************
        # Add a specific VTK window in the PyQt5 interface
        # *****************************************

        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.Layout_brain_connectome_3D.addWidget(self.vtkWidget)

        # Setup output view:
        output = reader.GetOutput()
        output_port = reader.GetOutputPort()
        scalar_range = output.GetScalarRange()

        # Create the mapper for brain surfaces:
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputConnection(output_port)
        mapper.SetScalarRange(scalar_range)

        # Create the actor for brains surfaces:
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(0.2)

        # Create the renderer: 
        self.ren = vtk.vtkRenderer()
        self.ren.AddActor(actor) #brain surfaces


        # *****************************************
        # Get point data thanks to parcellation table
        # *****************************************

        # Get the parcellation table with Cortical and Subcortical regions: 
        with open(os.path.join(self.parcellation_table_textEdit.toPlainText()), "r") as table_json_file:
            table_json_object = json.load(table_json_file)

        # Get data points for connected and unconnected points: 
        list_x, list_y, list_z, list_points = ([], [], [],[])

        for key in table_json_object:    
            list_x.append(key["coord"][0])
            list_y.append(key["coord"][1])
            list_z.append(key["coord"][2])

            # for map()
            point = []
            point.append(key["coord"][0])
            point.append(key["coord"][1])
            point.append(key["coord"][2])
            list_points.append(point)


        # Set 1 if the point is connected and 0 otherwise
        list_visibility_point = []

        if not self.plot_unconnected_points_3D_CheckBox.isChecked(): 
            for i in range(np.shape(a)[0]):
                is_connected = "False"

                for j in range(np.shape(a)[1]):
                    # Normalize the value in connectivity matrix: 
                    my_norm = (a[i,j] - mmin) / (mmax - mmin) # value between 0 to 1 

                    # To be coherent with the range of colorbar: 
                    if my_norm > vmin_3D and my_norm < vmax_3D: 
                        is_connected = "True"
                
                if is_connected == "False":  
                    list_visibility_point.append(0)
                else: 
                    list_visibility_point.append(1)
        else: 
            list_visibility_point = [1] * np.shape(a)[0]


        # Loop for points:
        #map(Ui_visu.loop_for_points, list_points) #9s with map (10s without)

        for i in range(len(list_x)): 
            # *****************************************
            # Creates points thanks to parcellation table 
            # *****************************************

            # Create the polydata where we will store all the geometric data (points and lines):
            pointPolyData = vtk.vtkPolyData()

            # Create points and the topology of the point (a vertex):
            points = vtk.vtkPoints()
            vertices = vtk.vtkCellArray()

            # Add all point: 
            id = points.InsertNextPoint(list_x[i],list_y[i],list_z[i])
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(id)

            # Add the points to the polydata container:
            pointPolyData.SetPoints(points)
            pointPolyData.SetVerts(vertices)


            # *****************************************
            # Points colors
            # *****************************************

            # Setup colors parameters for point:
            colors = vtk.vtkUnsignedCharArray()
            colors.SetNumberOfComponents(3)

            # Add color: 
            colors.InsertNextTypedTuple((0,0,255))
            
            # Add color points to the polydata container: 
            pointPolyData.GetPointData().SetScalars(colors)

            # Create the mapper for point:
            mapper_points = vtk.vtkPolyDataMapper()  
            mapper_points.SetInputData(pointPolyData)

            # Create the actor for points:
            actor_point = vtk.vtkActor()
            actor_point.SetMapper(mapper_points)
            actor_point.GetProperty().SetPointSize(self.point_size_3D_spinBox.value())
            actor_point.GetProperty().SetRenderPointsAsSpheres(1)

            # Set visibility: 
            actor_point.SetVisibility(list_visibility_point[i])                

            # Add point to renderer
            self.ren.AddActor(actor_point) 


        # *****************************************
        # Creates lines thanks to connectivity matrix and add colors
        # *****************************************

        # Create the color map
        colorLookupTable = vtk.vtkLookupTable()
        colorLookupTable.SetTableRange(vmin_3D, vmax_3D)
        n = 255  #n: number of colors
        colorLookupTable.SetNumberOfTableValues(n)
        colorLookupTable.Build()

        # Add value inside the color map:
        my_colormap = plt.cm.get_cmap('RdBu') #RdBu
        for i in range(n):
            my_color = list(my_colormap(i/n)) # tuple: R, G, B, 1 
            my_color = my_color[:-1] # R G B 
            colorLookupTable.SetTableValue(i, my_color[0], my_color[1], my_color[2], 1)

        # Create each lines and add a specific color: 
        '''
        list_index = []
        for index, x in np.ndenumerate(a):
            list_index.append(index)
        
        map(Ui_visu.loop_for_lines, a.flatten(), list_index)

        #map(lambda row: map(Ui_visu.loop_for_lines, row), a)
        '''

        for i in range(np.shape(a)[0]):
            for j in range(np.shape(a)[1]):                

                # Normalize the value in connectivity matrix: 
                my_norm = (a[i,j] - mmin) / (mmax - mmin) # value between 0 to 1 
            
                # Create a container and store the lines in it: 
                lines = vtk.vtkCellArray()

                # Create the polydata where we will store all the geometric data (points and lines):
                linesPolyData = vtk.vtkPolyData()

                # To access to 2 points: 
                two_points = vtk.vtkPoints()
                two_points.InsertNextPoint(list_x[i],list_y[i],list_z[i])
                two_points.InsertNextPoint(list_x[j],list_y[j],list_z[j])

                linesPolyData.SetPoints(two_points)

                # Create each lines: 
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0,0)
                line.GetPointIds().SetId(1,1)
                lines.InsertNextCell(line)

                # Add the lines to the polydata container:
                linesPolyData.SetLines(lines)

                # Setup colors parameters for lines: 
                colors_line = vtk.vtkUnsignedCharArray()
                colors_line.SetNumberOfComponents(3)

                # Add color:
                my_color = [0.0, 0.0, 0.0]
                colorLookupTable.GetColor(my_norm, my_color)

                # Change line to tube: 
                tubes = vtk.vtkTubeFilter()
                tubes.SetInputData(linesPolyData)
                tubes.SetRadius(self.linewidth_3D_spinBox.value())
                tubes.Update()
       
                # Create the mapper per line:
                mapper_lines = vtk.vtkPolyDataMapper()  
                mapper_lines.SetInputData(tubes.GetOutput())   
             
                mapper_lines.SetScalarModeToUseCellData()
                mapper_lines.SetColorModeToMapScalars()
                mapper_lines.Update()   

                mapper_lines.SetLookupTable(colorLookupTable)
                mapper_lines.SetScalarRange(vmin_3D, vmax_3D)
                mapper_lines.Update()  

                # Create one actor per line:
                actor_lines = vtk.vtkActor()
                actor_lines.SetMapper(mapper_lines)
                actor_lines.GetProperty().SetColor(my_color[0], my_color[1], my_color[2])

                # To be coherent with the range of colorbar: 
                actor_lines.SetVisibility(0)
                if my_norm > vmin_3D and my_norm < vmax_3D:
                    actor_lines.SetVisibility(1)

                # Add to the renderer:
                self.ren.AddActor(actor_lines)    

        # Add the color map:
        scalarBar = vtk.vtkScalarBarActor()
        scalarBar.SetNumberOfLabels(8)
        scalarBar.SetLookupTable(colorLookupTable)
        self.ren.AddActor2D(scalarBar)

        # Set color of the background: 
        namedColors = vtk.vtkNamedColors()
        self.ren.SetBackground(namedColors.GetColor3d("SlateGray")) 


        # *****************************************
        # Add a window with an interactor and start visualization
        # *****************************************

        # Create a window and an interactor
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        # Start visualization
        self.ren.ResetCamera()
        self.ren.GetActiveCamera().Zoom(1.3)
        self.iren.Initialize()

        print("End display 3D brain connectome: ",time.strftime("%H h: %M min: %S s",time.gmtime( time.time() - start )))


    



    def loop_for_points(point):
        # *****************************************
        # Creates points thanks to parcellation table 
        # *****************************************

        # Create the polydata where we will store all the geometric data (points and lines):
        pointPolyData = vtk.vtkPolyData()

        # Create points and the topology of the point (a vertex):
        points = vtk.vtkPoints()
        vertices = vtk.vtkCellArray()

        # Add all point: 
        id = points.InsertNextPoint(point[0],point[1],point[2])#list_x[i],list_y[i],list_z[i]
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(id)

        # Add the points to the polydata container:
        pointPolyData.SetPoints(points)
        pointPolyData.SetVerts(vertices)


        # *****************************************
        # Points colors
        # *****************************************

        # Setup colors parameters for point:
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)

        # Add color: 
        colors.InsertNextTypedTuple((0,0,255))
        
        # Add color points to the polydata container: 
        pointPolyData.GetPointData().SetScalars(colors)

        # Create the mapper for point:
        mapper_points = vtk.vtkPolyDataMapper()  
        mapper_points.SetInputData(pointPolyData)

        # Create the actor for points:
        actor_point = vtk.vtkActor()
        actor_point.SetMapper(mapper_points)
        actor_point.GetProperty().SetPointSize(self.point_size_3D_spinBox.value())
        actor_point.GetProperty().SetRenderPointsAsSpheres(1)

        # Set visibility: 
        actor_point.SetVisibility(list_visibility_point[i])                

        # Add point to renderer
        self.ren.AddActor(actor_point) 





    def loop_for_lines(element, index):  #index: (0,0) and element replace a[i,j]
        i = index[0]
        j = index[1]

        # Normalize the value in connectivity matrix: 
        my_norm = (element - mmin) / (mmax - mmin) # value between 0 to 1 
    
        # Create a container and store the lines in it: 
        lines = vtk.vtkCellArray()

        # Create the polydata where we will store all the geometric data (points and lines):
        linesPolyData = vtk.vtkPolyData()

        # To access to 2 points: 
        two_points = vtk.vtkPoints()
        two_points.InsertNextPoint(list_x[i],list_y[i],list_z[i])
        two_points.InsertNextPoint(list_x[j],list_y[j],list_z[j])

        linesPolyData.SetPoints(two_points)

        # Create each lines: 
        line = vtk.vtkLine()
        line.GetPointIds().SetId(0,0)
        line.GetPointIds().SetId(1,1)
        lines.InsertNextCell(line)

        # Add the lines to the polydata container:
        linesPolyData.SetLines(lines)

        # Setup colors parameters for lines: 
        colors_line = vtk.vtkUnsignedCharArray()
        colors_line.SetNumberOfComponents(3)

        # Add color:
        my_color = [0.0, 0.0, 0.0]
        colorLookupTable.GetColor(my_norm, my_color)

        # Change line to tube: 
        tubes = vtk.vtkTubeFilter()
        tubes.SetInputData(linesPolyData)
        tubes.SetRadius(self.linewidth_3D_spinBox.value())
        tubes.Update()

        # Create the mapper per line:
        mapper_lines = vtk.vtkPolyDataMapper()  
        mapper_lines.SetInputData(tubes.GetOutput())   
     
        mapper_lines.SetScalarModeToUseCellData()
        mapper_lines.SetColorModeToMapScalars()
        mapper_lines.Update()   

        mapper_lines.SetLookupTable(colorLookupTable)
        mapper_lines.SetScalarRange(vmin_3D, vmax_3D)
        mapper_lines.Update()  

        # Create one actor per line:
        actor_lines = vtk.vtkActor()
        actor_lines.SetMapper(mapper_lines)
        actor_lines.GetProperty().SetColor(my_color[0], my_color[1], my_color[2])

        # To be coherent with the range of colorbar: 
        actor_lines.SetVisibility(0)
        if my_norm > vmin_3D and my_norm < vmax_3D:
            actor_lines.SetVisibility(1)

        # Add to the renderer:
        self.ren.AddActor(actor_lines)    




    # *****************************************
    # Update the 3D brain connectome if the user change the range: min/max
    # ***************************************** 

    def update_3D_connectome(self): 
        # New range colorbar: 
        vmin_3D,vmax_3D  = (self.min_colorbar_brain_3D_connectome_doubleSpinBox.value() / 100, self.max_colorbar_brain_3D_connectome_doubleSpinBox.value() / 100)

         # Create the new color map:
        colorLookupTable1 = vtk.vtkLookupTable()
        colorLookupTable1.SetTableRange(vmin_3D, vmax_3D)
        n = 255  #n: number of colors
        colorLookupTable1.SetNumberOfTableValues(n)
        colorLookupTable1.Build()

        # Add value inside the new color map:
        my_colormap = plt.cm.get_cmap('RdBu') #RdBu
        for i in range(n):
            my_color = list(my_colormap(i/n)) # tuple: R, G, B, 1 
            my_color = my_color[:-1] # R G B 
            colorLookupTable1.SetTableValue(i, my_color[0], my_color[1], my_color[2], 1)
        
        # Compute again the list with all atribute to know with point to hidde:
        list_visibility_point = []

        if not self.plot_unconnected_points_3D_CheckBox.isChecked(): 
            for i in range(np.shape(a)[0]):
                is_connected = "False"

                for j in range(np.shape(a)[1]):
                    # Normalize the value in connectivity matrix: 
                    my_norm = (a[i,j] - mmin) / (mmax - mmin) # value between 0 to 1 

                    # To be coherent with the range of colorbar: 
                    if my_norm > vmin_3D and my_norm < vmax_3D: 
                        is_connected = "True"
                
                if is_connected == "False":  
                    list_visibility_point.append(0)
                else: 
                    list_visibility_point.append(1)
        else: 
            list_visibility_point = [1] * np.shape(a)[0]

        
        # Compute the list with all atribute to know with lines to hidde: 
        list_visibility_lines,list_color  = ([],[])

        for i in range(np.shape(a)[0]):
            for j in range(np.shape(a)[1]):                

                # Normalize the value in connectivity matrix: 
                my_norm = (a[i,j] - mmin) / (mmax - mmin) # value between 0 to 1 

                # To be coherent with the range of colorbar: 
                my_color = [0.0, 0.0, 0.0]

                if my_norm > vmin_3D and my_norm < vmax_3D:
                    list_visibility_lines.append(1)
                    # Add color:
                    colorLookupTable1.GetColor(my_norm, my_color)
                    list_color.append(my_color)

                else: 
                    list_visibility_lines.append(0)
                    list_color.append(my_color)

        # Update actor:
        actors = vtk.vtkPropCollection() 
        actors = self.ren.GetViewProps()
        actors.InitTraversal()

        iNumberOfActors = actors.GetNumberOfItems()
        #len(list_visibility_point) = 90 points      iNumberOfActors = 8192 points + lines      len(list_visibility_lines) = 8100 lines     

        print(iNumberOfActors)  

        for i in range(iNumberOfActors): 
            if i == 0: 
                actors.GetNextProp().VisibilityOn() # skip brain surfaces actor which is the first actor

            elif i == iNumberOfActors-1: # update colorbar: last actor: actor for colorbar
                actors.GetNextProp().SetLookupTable(colorLookupTable1)

            elif i != 0 and i < len(list_visibility_point)+1: # actor point
                if list_visibility_point[i-1] == 0: 
                    actors.GetNextProp().VisibilityOff()
                else:
                    actors.GetNextProp().VisibilityOn() 

            else: #actor line
                if list_visibility_lines[i-1 - len(list_visibility_point)] == 0: 
                    actors.GetNextProp().VisibilityOff()
                else: 
                    my_actor = actors.GetNextProp()
                    my_actor.VisibilityOn()
                    # Add new color: 
                    my_actor.GetProperty().SetColor(list_color[i-1 - len(list_visibility_point)][0], 
                                                    list_color[i-1 - len(list_visibility_point)][1], 
                                                    list_color[i-1 - len(list_visibility_point)][2])

        # Update visualization
        self.ren.ResetCamera()
        self.ren.GetActiveCamera().Zoom(1.3)
        self.iren.Initialize()

        print("end update 3D connectome")


    
    # *****************************************
    # Update points size 
    # ***************************************** 

    def update_points_size(self):
        # Update actor:
        actors = vtk.vtkPropCollection() 
        actors = self.ren.GetViewProps()
        actors.InitTraversal()

        for i in range(np.shape(a)[0]+1):  
            if i == 0:  #actor for brain surfaces: skip
                actors.GetNextProp().VisibilityOn()
            else: # actor points
                actors.GetNextProp().GetProperty().SetPointSize(self.point_size_3D_spinBox.value())

        # Update visualization
        self.ren.ResetCamera()
        self.ren.GetActiveCamera().Zoom(1.3)
        self.iren.Initialize()

        print("end size point update")


    
    # *****************************************
    # Update line width
    # ***************************************** 

    def update_lines_size(self):
        print('to do ')
        '''
        # Update actor:
        actors = vtk.vtkPropCollection() 
        actors = self.ren.GetViewProps()
        actors.InitTraversal()

        iNumberOfActors = actors.GetNumberOfItems()

        for i in range(iNumberOfActors):  
            if i == 0 or i < np.shape(a)[0]+1:  #actor for brain surfaces + point: skip
                actors.GetNextProp().VisibilityOn()
            else: # actors lines
                actors.GetNextProp().GetMapper().SetRadius(self.linewidth_3D_spinBox.value())

        # Update visualization
        self.ren.ResetCamera()
        self.ren.GetActiveCamera().Zoom(1.3)
        self.iren.Initialize()

        print("end size line update")
        '''



    # *****************************************
    # Display brain surfaces with a specific view 
    # *****************************************

    def view_3D(self):

        # Axial view:
        if self.view_3D_comboBox.currentText() == "Axial": 
            self.ren.GetActiveCamera().SetViewUp(0, 1, 0)
            self.ren.GetActiveCamera().SetFocalPoint(0.0, 0.0, 0.0)  
            self.ren.GetActiveCamera().SetPosition(0,0,1)  
     
        # Sagittal view:
        elif self.view_3D_comboBox.currentText() == "Sagittal": 
            self.ren.GetActiveCamera().SetViewUp(1, 0, 0)
            self.ren.GetActiveCamera().SetFocalPoint(0.0, 0.0, 0.0)
            self.ren.GetActiveCamera().SetPosition(1,0,-1)  

        # Coronal view: 
        else: 
            self.ren.GetActiveCamera().SetViewUp(0, 1, 0 )
            self.ren.GetActiveCamera().SetFocalPoint(0.0, 0.0, 0.0)
            self.ren.GetActiveCamera().SetPosition(0,-1,0) 
           
        # Start visualization
        self.ren.GetActiveCamera().Elevation(30)        
        self.ren.ResetCamera()
        self.ren.GetActiveCamera().Zoom(1.3)
        self.iren.Initialize()
        










    # *****************************************
    # Display a vtk file given by the user
    # *****************************************
    
    def selected_file_clicked(self):
        # Remove the previous plot: 
        for i in reversed(range(self.Layout_vtk_fiber.count())): 
            self.Layout_vtk_fiber.itemAt(i).widget().setParent(None)

        # Add a specific vtk window
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.Layout_vtk_fiber.addWidget(self.vtkWidget)

        # Read the source file
        reader = vtk.vtkPolyDataReader() #vtkPolyDataReader
        reader.SetFileName(self.select_vtk_file_textEdit.toPlainText())
        reader.Update()  

        # Setup output view
        output = reader.GetOutput()
        output_port = reader.GetOutputPort()
        scalar_range = output.GetScalarRange()

        # Create the mapper 
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(output_port)
        mapper.SetScalarRange(scalar_range)

        # Create the Actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Create the Renderer and a window
        self.ren = vtk.vtkRenderer()
        self.ren.AddActor(actor)

        # Set color of the background: 
        namedColors = vtk.vtkNamedColors()
        self.ren.SetBackground(namedColors.GetColor3d("SlateGray")) 
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        # Start visualization
        self.ren.ResetCamera()
        self.iren.Initialize()



    # *****************************************
    # Selected a vtk file to display it
    # *****************************************

    def select_vtk_file_pushButton_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()" , "", "ALL Files (*)", options=QFileDialog.Options())
        if fileName:
            self.select_vtk_file_textEdit.setText(fileName) 


    '''
        # Display a vtk file WITHOUT Qt interface
        file_name = "./input_CONTINUITY/stx_T0054-1-1-6yr-T1_SkullStripped_scaled_BiasCorr_corrected_multi_atlas_white_surface_rsl_left_327680_native_ITKspace.vtk"

        # Read the source file.
        import vtk
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(file_name)
        reader.Update()  # Needed because of GetScalarRange
        output = reader.GetOutput()
        output_port = reader.GetOutputPort()
        scalar_range = output.GetScalarRange()

        # Create the mapper that corresponds the objects of the vtk file
        # into graphics elements
        mapper = vtkDataSetMapper()
        mapper.SetInputConnection(output_port)
        mapper.SetScalarRange(scalar_range)

        # Create the Actor
        actor = vtkActor()
        actor.SetMapper(mapper)

        # Create the Renderer
        renderer = vtkRenderer()
        renderer.AddActor(actor)
        renderer.SetBackground(1, 1, 1) # Set background 

        # Create the RendererWindow
        renderer_window = vtkRenderWindow()
        renderer_window.AddRenderer(renderer)

        # Create the RendererWindowInteractor and display the vtk_file
        interactor = vtkRenderWindowInteractor()
        interactor.SetRenderWindow(renderer_window)

        interactor.Initialize()
        interactor.Start()
    '''             