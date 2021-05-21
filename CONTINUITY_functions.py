#!/usr/bin/env python3
import json
import os 
import sys 
import shutil
import subprocess
from termcolor import colored
import csv

import vtk
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


##########################################################################################################################################
  
     # Functions for new CONTINUITY tool
 
##########################################################################################################################################
    
# *************************************************************************************
# Function to run a specific command
# *************************************************************************************

def run_command(text_printed, command):
    # Display command 
    print(colored("\n"+" ".join(command)+"\n", 'blue'))
    # Run command and display output and error
    run = subprocess.Popen(command, stdout=0, stderr=subprocess.PIPE)
    out, err = run.communicate()
    print(text_printed, "out: ", colored("\n" + str(out) + "\n", 'green')) 
    print(text_printed, "err: ", colored("\n" + str(err) + "\n", 'red'))





# *************************************************************************************
# Extract name of subcortical regions
# *************************************************************************************

def extract_name_sc_region(SALTDir, KWMDir , ID):

    list_sc_region_SALT, list_sc_region_KWM = ([],[])

    (_, _, filenames) = next(os.walk(SALTDir))
    for entry in filenames:
        
        if entry.startswith( str( ID + "-T1_SkullStripped_scaled_label_")):
            start = entry.find("-T1_SkullStripped_scaled_label_") + len("-T1_SkullStripped_scaled_label_")
            end = entry.find("_",len(ID) + len("-T1_SkullStripped_scaled_label_") )

            if str(end) == "-1": #no underscore found
                end = entry.find(".", len(ID) + len("-T1_SkullStripped_scaled_label_") ) 
       
            region = entry[start:end]
            if region not in list_sc_region_SALT: 
                list_sc_region_SALT.append(region)


    (_, _, filenames) = next(os.walk(KWMDir))
    for entry in filenames:
     
        if entry.endswith("_1002_KWM.txt"):
            end = entry.find("_1002_KWM.txt")

            region = entry[:end]
            if region not in list_sc_region_KWM: 
                list_sc_region_KWM.append(region)

    return list_sc_region_SALT, list_sc_region_KWM









# *************************************************************************************
# Identify the location of executables
# *************************************************************************************

def my_which(name):
    for path in os.getenv("PATH").split(os.path.pathsep):
        full_path = os.path.join(path,name)
        if os.path.exists(full_path):
            return full_path
    return "False"



# *************************************************************************************
# Find and write path of executables
# *************************************************************************************

def executable_path(default_filename, user_filename):
    with open(default_filename) as default_file:
        data_default = json.load(default_file)
        
    with open(user_filename) as user_file:
        data_user = json.load(user_file)

    for categories, infos in data_default.items():
        if categories == "Executables":
            for key in infos: 
                if key == "ITKTransformTools_v1":
                    path = my_which("ITKTransformTools_v1.2.3")
                    if path == "False":
                        path = my_which("ITKTransformTools")

                elif key == "polydatatransform_v1":
                    path = my_which("polydatatransform_v1.2.1")
                    if path == "False":
                            path = my_which("polydatatransform")

                elif key == "MRtrix": 
                    run = subprocess.Popen(['whereis', "mrtrix"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    out, err = run.communicate()
                    #print("out: ", colored("\n" + str(out) + "\n", 'green')) #b'mrtrix: /home/elodie/anaconda3/bin/mrtrix3.py /home/elodie/anaconda3/bin/mrtrix3.pyc\n'
                    section = str(out).split()
                   
                    if len(section) > 1:
                        all = os.path.split(section[1]) #(b'/home/elodie/anaconda3/bin', b'mrtrix3.py')
                        path = all[0]
                    else:
                        path = 'False'
                                 
                elif key == "fsl": 
                    path = my_which("fsl") #/tools/FSL/fsl-6.0.3/bin/fsl
                   
                    if path != "False":
                        listFSLPath = os.path.split(path) 
                        path = listFSLPath[0] #/tools/FSL/fsl-6.0.3/bin/probtrackx2  /tools/FSL/fsl-6.0.3/bin/bedpostx

                elif key == "slicer":
                    path = "/proj/NIRAL/tools/Slicer-4.11.0-2020-05-27-linux-amd64/Slicer" # On longleaf to have a specific version and not version in /nas ect
                    if not os.path.exists(path): 
                        path = "/tools/Slicer4/Slicer-4.10.2-2019-07-11-linux-amd64/Slicer" # On pegasus
                        if not os.path.exists(path): 
                            path = my_which(key)
                else:
                    path = my_which(key)
                data_user[categories][key]["value"] = path

                with open(user_filename, "w+") as user_file:
                    user_file.write(json.dumps(data_user, indent=4)) 
    '''
    with open(user_filename) as user_file:
        data_user = json.load(user_file)
        for categories, infos in data_user.items():
            for key in infos: 
                if categories == "Executables":
                    print("After exe fct: ",key, ": ", data_user[categories][key]["value"])
    '''
      


# *************************************************************************************
# Function : CONTINUITY scripts
# *************************************************************************************

def CONTINUITY(user_filename):
    run_command("CONTINUITY script", [sys.executable, "./CONTINUITY_completed_script.py", user_filename ])



# *************************************************************************************
# Write a csv file
# *************************************************************************************

def write_csv_file(csv_filename, user_filename):
    with open(csv_filename, mode='w') as csv_file:
        with open(user_filename) as user_file:
            data_user = json.load(user_file)

        # Extract field name: name of each column
        fieldnames = []
        list_data = ["ID", "DWI_DATA", "T1_DATA", "BRAINMASK", "PARCELLATION_TABLE", "WM_L_Surf", "WM_R_Surf","OUT_PATH"]

        for categories, infos in data_user.items():
            for key in infos:
                if key in list_data:
                    fieldnames.append(key)
        writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=fieldnames)

        # Write data
        line = "{"
        for categories, infos in data_user.items():
            for key in infos:
                if key in list_data:
                    line += "'" + key + "' : '" + data_user[categories][key]['default'] + "',"
        line += "}"
        writer.writeheader()
        writer.writerow( eval(line) )       



# *************************************************************************************
# Run the script in longleaf: python3 main_CONTINUITY.py -noGUI -cluster -cluster_command_line test
# *************************************************************************************

def cluster(slurm_job_filename, cluster_command_line):  
    print("Cluster: run script in longleaf")
    print(cluster_command_line)

    # Open and write the command line given by the user:
    slurm_job_file = open(slurm_job_filename, 'w') 
    slurm_job_file.write(cluster_command_line) 
    slurm_job_file.close()  

    # Run 
    run_command("cluster", ['sbatch', "./slurm-job" ])
    


# *************************************************************************************
# Function to replace MeshMath KWMtoPolyData: applies the label in the KWM file to the SPHARM surface
# *************************************************************************************

def KWMtoPolyData(SPHARMSurf, SPHARMSurfL, KWMFile, NAME_PARCELLATION_TABLE):
    #                   input mesh ,outputFileName,inputTxtFile, scalar field name
    # https://github.com/NIRALUser/SPHARM-PDM/blob/master/Modules/CLI/MetaMeshTools/MeshMath.cxx   line 4443 to 4531

    polyIn = vtk.vtkPolyDataReader() 
    polyIn.SetFileName(SPHARMSurf)
    polyIn.Update()
    polydataAtt = polyIn.GetOutput() #vtkPolyData

    # Start parsing KWMeshVisu file
    KWM_file = open(KWMFile, 'r')     

    # Get number of points
    first_line = KWM_file.readline(70) 
    first_line_list = first_line.split("=") 
    NPoints =int(first_line_list[1].strip()) #"NUMBER_OF_POINTS=1002"
   
    # Get number of dimension
    second_line = KWM_file.readline(70)
    second_line_list = second_line.split("=") 
    NDimension = int(second_line_list[1].strip()) #"DIMENSION=1"

    KWM_file.readline(70) # third line in txt file: "TYPE=Scalar" : just read a non important line to skip it and achieve line with data

    scalars = vtk.vtkFloatArray()
    scalars.SetNumberOfComponents(NDimension)
    scalars.SetName(NAME_PARCELLATION_TABLE)

    for i in range(0, NPoints):
        line = str(KWM_file.readline(70)) #read a line
        sub_string = line.split(" ") 
        sub_string[-1] = sub_string[-1].strip() # remove \n at the end of each line

        my_list = []
        count = 0
        for sub in sub_string:
            if sub != "":
                if count >= NDimension:
                    print("Error in input file format: one line contains too many components")
                    return 1
                my_list.append(float(sub))  #int(sub)
                count += 1

        if count != NDimension:
            print("Error in input file format: one line does not contain enough components","Line:", line,"Components found:", count  )
            return 1 

        # Add scalar map to the mesh
        scalars.InsertNextTuple(tuple(my_list))

    KWM_file.close()

    # End reading the Input
    polydataAtt.GetPointData().AddArray(scalars)

    # Writing the new mesh
    SurfaceWriter = vtk.vtkPolyDataWriter()
    SurfaceWriter.SetInputData(polydataAtt)
    SurfaceWriter.SetFileName(SPHARMSurfL)
    SurfaceWriter.Update()



# *************************************************************************************
# Function to replace polydatamerge (NIRAL function)
# *************************************************************************************

def polydatamerge(fiberFile1, fiberFile2, fiberOutput):
    # Read fiberfile 1:
    reader1 = vtk.vtkPolyDataReader()
    reader1.SetFileName(fiberFile1)
    reader1.Update()
    polydata1 = reader1.GetOutput()

    # Read fiberfile 2:
    reader2 = vtk.vtkPolyDataReader()
    reader2.SetFileName(fiberFile2)
    reader2.Update()
    polydata2 = reader2.GetOutput()

    polydata = vtk.vtkPolyData()
    apd = vtk.vtkAppendPolyData()

    if (vtk.VTK_MAJOR_VERSION < 6):
        apd.AddInput(polydata2)
        apd.AddInput(polydata1)
    else:
        apd.AddInputData(polydata2)
        apd.AddInputData(polydata1)

    apd.Update()
    polydata = apd.GetOutput()

    # print("Saving fibers in ", fiberOutput)
    fiberwriter = vtk.vtkPolyDataWriter()
    fiberwriter.SetFileName(fiberOutput)

    if (vtk.VTK_MAJOR_VERSION < 6):
        fiberwriter.SetInput(polydata)
    else:
        fiberwriter.SetInputData(polydata)

    fiberwriter.SetFileTypeToBinary()
    fiberwriter.Update()

    try:
        fiberwriter.Write()
        print("Merging done!")
    except:
        print("Error while saving fiber file.")
        exit()

    

def polydatamerge_ascii(fiberFile1, fiberFile2, fiberOutput):
    # Read fiberfile 1:
    reader1 = vtk.vtkPolyDataReader()
    reader1.SetFileName(fiberFile1)
    reader1.Update()
    polydata1 = reader1.GetOutput()

    # Read fiberfile 2:
    reader2 = vtk.vtkPolyDataReader()
    reader2.SetFileName(fiberFile2)
    reader2.Update()
    polydata2 = reader2.GetOutput()

    polydata = vtk.vtkPolyData()
    apd = vtk.vtkAppendPolyData()

    if (vtk.VTK_MAJOR_VERSION < 6):
        apd.AddInput(polydata2)
        apd.AddInput(polydata1)
    else:
        apd.AddInputData(polydata2)
        apd.AddInputData(polydata1)

    apd.Update()
    polydata = apd.GetOutput()

    # print("Saving fibers in ", fiberOutput)
    fiberwriter = vtk.vtkPolyDataWriter()
    fiberwriter.SetFileName(fiberOutput)

    if (vtk.VTK_MAJOR_VERSION < 6):
        fiberwriter.SetInput(polydata)
    else:
        fiberwriter.SetInputData(polydata)

    #fiberwriter.SetFileTypeToBinary()
    fiberwriter.Update()

    try:
        fiberwriter.Write()
        print("Merging done!")
    except:
        print("Error while saving fiber file.")
        exit()



# *************************************************************************************
# Sum by line
# *************************************************************************************

def sum_line(matrix):
    waytotal_line = []
    for line in matrix:
        sumLine = 0
        for val in line:
            sumLine += float(val)
        waytotal_line.append(sumLine)
    return waytotal_line



# *************************************************************************************
# Sum by column
# *************************************************************************************

def sum_column(matrix):
    waytotal_column = []
    for i in range(len(matrix[0])):
        sum_column = 0
        for j in range(len(matrix)) :
            sum_column += float(matrix[j][i])
        waytotal_column.append(sum_column)
    return waytotal_column



# *************************************************************************************
# Sum all
# *************************************************************************************

def sum_all(matrix):
    waytotal = 0
    for line in matrix:
        for val in line:
          waytotal = waytotal + float(val)
    return waytotal



# *************************************************************************************
# No normalization
# *************************************************************************************

def no_normalization(matrix):
    fin = open(matrix,'r')
    a=[]
    for line in fin.readlines():
        a.append( [ float(x) for x in line.split('  ') if x != "\n" ] )   
    return a 



# *************************************************************************************
# Whole normalization
# *************************************************************************************

def whole_normalization(matrix):
    fin = open(matrix,'r')
    a=[]
    for line in fin.readlines():
        a.append( [ float(x) for x in line.split('  ') if x != "\n" ] )   

    # Sum of all coef: 
    waytotal = sum_all(a)
    
    i=0
    for line in a:
        j=0
        for val in line:
          a[i][j]= val / waytotal
          j=j+1
        i=i+1
    return a 



# *************************************************************************************
# Region normalization
# *************************************************************************************

def row_region_normalization(matrix):
    fin = open(matrix,'r')
    a=[]
    for line in fin.readlines():
        a.append( [ float(x) for x in line.split('  ') if x != "\n" ] )   

    # Sum of each line: 
    waytotal_line = sum_line(a)

    i=0
    for line in a:
        j=0
        for val in line:
          a[i][j]=val / waytotal_line[i]
          j=j+1
        i=i+1
    return a 



# *************************************************************************************
# Row/column normalization
# *************************************************************************************

def row_column_normalization(matrix):
    fin = open(matrix,'r')
    a=[]
    for line in fin.readlines():
        a.append( [ float(x) for x in line.split('  ') if x != "\n" ] )  

    # Sum of each column and each line: 
    waytotal_column = sum_column(a)
    waytotal_line   = sum_line(a)

    i=0
    for line in a:
        j=0
        for val in line:
            newVal = val / (waytotal_line[i] + waytotal_column[j]) 
            a[i][j]=newVal
            j=j+1
        i=i+1
    return a 



# *************************************************************************************
# Symmetrization: average
# *************************************************************************************

def average_symmetrization(a):
    i=0
    for line in a:
        j=0
        for val in line:
            if i<j: #lower triangle matrix
                newVal = (a[i][j] + a[j][i]) / 2  #average
                a[i][j]= newVal
                a[j][i]= newVal
            j=j+1
        i=i+1
    return a 


# *************************************************************************************
# Symmetrization: maximum
# *************************************************************************************

def maximum_symmetrization(a):
    i=0
    for line in a:
        j=0
        for val in line:
            if i<j: #lower triangle matrix
                if a[i][j] > a[j][i]: 
                    newVal = a[i][j]  
                else: 
                    newVal = a[j][i]   
                a[i][j]= newVal
                a[j][i]= newVal
            j=j+1
        i=i+1
    return a 



# *************************************************************************************
# Symmetrization: minimum
# *************************************************************************************

def minimum_symmetrization(a):
    i=0
    for line in a:
        j=0
        for val in line:
            if i<j: #lower triangle matrix
                if a[i][j] > a[j][i]: 
                    newVal = a[j][i]  
                else: 
                    newVal = a[i][j] 
                a[i][j]= newVal
                a[j][i]= newVal
            j=j+1
        i=i+1
    return a 



# *************************************************************************************
# Save in pdf 
# *************************************************************************************

def save_connectivity_matrix(type_of_normalization, a, OutputDir, subject, overlapName, loopcheck): 
    
    # plotting the correlation matrix and clear figure: 
    fig = plt.figure(num=None, figsize=(15, 15))
    fig.clf()

    outputfilename = 'Connectivity matrix of data \n' + subject + ' normalized type: ' + type_of_normalization + '\n'

    if len(overlapName)>3 and len(loopcheck)>3:
      outputfilename += 'with Loopcheck and with Overlapping'
    elif len(overlapName)<3 and len(loopcheck)>3:
      outputfilename += 'without Loopcheck and with Overlapping'
    elif len(overlapName)>3 and len(loopcheck)<3:
      outputfilename += 'with Loopcheck and without Overlapping'
    else:
      outputfilename += 'without Loopcheck and without Overlapping'
  
    # Subtitle and axes: 
    fig.suptitle(outputfilename, fontsize=18)
    plt.xlabel('Seeds')
    plt.ylabel('Targets')
    ax = fig.add_subplot(1,1,1)

    # Colorbar: 
    cax = ax.imshow(a, interpolation='nearest', vmin=0.0, vmax=0.99)
    fig.colorbar(cax)

    # Save
    fig.savefig(os.path.join(OutputDir, 'Connectivity_matrix_normalized_' + type_of_normalization + '.pdf'), format='pdf')
    print("connectivity matrix for", type_of_normalization ,"normalization saved")   



# *************************************************************************************
# Compute the radius of each seed
# *************************************************************************************

def compute_radius_of_each_seed(line):
    # Init list with X, Y Z and radius:
    list_radius = []

    # Open the .asc file for one region:
    seed_region_data = open(line, "r+") 

    # 2 first lines: header
    seed_region_data.readline() # "!ascii - generated by CreateLabelFiles project "

    # Get the number of points:
    second_line = seed_region_data.readline() # " 2170    4121 "   --> first number: number of point    --> second number: number of polygon
    second_line = second_line.strip('\n')  
    second_line_nb = second_line.split(" ")
    number_point = int(second_line_nb[0])

    # First real line/point to init the computation of distance: 
    first = seed_region_data.readline().strip('\n')
    previous_line = first.split(" ")

    for elem in range(4): # X,Y,Z AND radius
        previous_line[elem] = round(float(previous_line[elem]),3)

        if elem == 3: # default value for first radius
            previous_line[elem] = float(100)

    previous_line = np.array(previous_line)
  
    # Return coordinate for this point with original radius:
    list_radius.append(previous_line.tolist())
   
    # For all lines/points, compute the radius: 
    i = 1 # first point already considered 
    number_point_end = 0 # number of good point = with 3 cordinates

    while i <= number_point: 
        # Cordinates of the considering point: 
        point = seed_region_data.readline()
        point = point.strip('\n')
        coord = point.split(" ")

        if len(coord) == 4: #check if this point is a real point
            # Considering point: 
            for elem in range(3):
                coord[elem] = round(float(coord[elem]),3)
            a = np.array(coord[:-1]) # only X,Y,Z to compute distance

            # Previous point:
            b = np.array(previous_line[:-1]) # only X,Y,Z to compute distance
       
            # Compute distance and add radius to the cordinates of this point:
            distance = abs( float(np.linalg.norm(a-b)))  # distance between two point   (distance has to be positive )
            coord = np.append(a, round(float(distance*100),3)) #radius = distance / 2    round: to keep juste 3 decimal in the float 

            # Update the compute the next distance/radius
            previous_line = coord

            # Return coordinate for points with radius:
            list_radius.append(coord.tolist())
        
            number_point_end +=1
        i += 1 

    seed_region_data.close()

    return list_radius, number_point_end



# *************************************************************************************
# Compute one point per Destrieux region
# *************************************************************************************

def compute_point_destrieux(new_parcellation_table, subcorticals_list_checked_with_surfaces, KWMDir, SALTDir, ID):
    print('subcorticals_list_checked_with_surfaces', subcorticals_list_checked_with_surfaces)

    # KWM file for left and right surfaces:
    left_KWM  = './CONTINUITY_QC/Destrieux_points/Atlas_Left_Destrieux.KWM.txt'
    right_KWM = './CONTINUITY_QC/Destrieux_points/Atlas_Right_Destrieux.KWM.txt'

    # Left and right surfaces: 
    left  = './CONTINUITY_QC/Destrieux_points/icbm_avg_mid_sym_mc_left_hires.vtk'
    right = './CONTINUITY_QC/Destrieux_points/icbm_avg_mid_sym_mc_right_hires.vtk'

    # Output: 
    left_out  = './CONTINUITY_QC/Destrieux_points/surface_destrieux_left.vtk'
    right_out = './CONTINUITY_QC/Destrieux_points/surface_destrieux_rigth.vtk'

    # Combine surfaces and scalar: 
    if not os.path.exists(left_out):
        KWMtoPolyData(left , left_out , left_KWM , 'Destrieux') 
        KWMtoPolyData(right, right_out, right_KWM, 'Destrieux') 


    # *****************************************
    # Cortical left regions:
    # ***************************************** 

    # Reader left output: 
    reader1 = vtk.vtkPolyDataReader()
    reader1.SetFileName(left_out)
    reader1.Update()

    # Get scalars of the left output : 163842 scalars and then extract all different scalar (+sort them)
    scalar1 = vtk_to_numpy(reader1.GetOutput().GetPointData().GetArray(1)) # 'Array 0 name = normals    Array 1 name = Destrieux' [11106. 11166. 11112. ... 11166.]
    scalar_sorted_without_duplicate1 = [ int(x) for x in  sorted(list( dict.fromkeys( scalar1.tolist() ) ))  ]

    # Get all points of the surfaces: 163842 points with 3 cordinates:
    numpy_nodes1 = vtk_to_numpy( reader1.GetOutput().GetPoints().GetData() ) #[[ -4.03771  40.0262   15.9554 ] ... [-18.2709  -55.9488   16.5177 ]] 
    
    # Initialize a list with the gravity center of each region: 
    gravity_center_of_each_Region1 = [ [0,0,0] ] * len(scalar_sorted_without_duplicate1)

    # Compute the gravity center of each region:  
    for i in range(len(numpy_nodes1)):
        # Get the index of the specific scalar of the considering point to be able to compute the appropriate gravity center: 
        index_scalar = scalar_sorted_without_duplicate1.index(scalar1[i]) # 5
                
        # Compute the gravity center: average of each cordinates 
        my_new_tuple = [0,0,0]
        for v in range(3):
            my_new_tuple[v] = (gravity_center_of_each_Region1[index_scalar][v] + numpy_nodes1[i][v] ) / 2 #average x, y and z 
       
        # Update the value of the gravity center for this region: 
        gravity_center_of_each_Region1[index_scalar] = my_new_tuple


    # *****************************************
    # Cortical right regions: 
    # ***************************************** 

    # Reader right output: 
    reader2 = vtk.vtkPolyDataReader()
    reader2.SetFileName(right_out)
    reader2.Update()

    # Get scalars of the left output : 163842 scalars and then extract all different scalar (+sort them)
    scalar2 = vtk_to_numpy(reader2.GetOutput().GetPointData().GetArray(1)) # 'Array 0 name = normals    Array 1 name = Destrieux'
    scalar_sorted_without_duplicate2 = [ int(x) for x in  sorted(list( dict.fromkeys( scalar2.tolist() ) ))  ]

    # Get all points of the surfaces: 163842 points with 3 cordinates:
    numpy_nodes2 = vtk_to_numpy( reader2.GetOutput().GetPoints().GetData() )
    
    # Initialize a list with the gravity center of each region: 
    gravity_center_of_each_Region2 = [ [0,0,0] ] * len(scalar_sorted_without_duplicate2)
    
    # Compute the gravity center of each region: average of each cordinates  
    for i in range(len(numpy_nodes2)):
        # Get the index of the specific scalar of the considering point to be able to compute the appropriate gravity center: 
        index_scalar = scalar_sorted_without_duplicate2.index(scalar2[i]) # 5
                    
        # Compute the gravity center: average of each cordinates 
        my_new_tuple = [0,0,0]
        for v in range(3):
            my_new_tuple[v] = (gravity_center_of_each_Region2[index_scalar][v] + numpy_nodes2[i][v] ) / 2 #average x, y and z 
    
        # Update the value of the gravity center for this region: 
        gravity_center_of_each_Region2[index_scalar] = my_new_tuple

    # Add left AND right data: scalar and then gravity center 
    scalar_sorted_without_duplicate_all = scalar_sorted_without_duplicate1 + scalar_sorted_without_duplicate2
    gravity_center_of_each_Region_all = gravity_center_of_each_Region1 + gravity_center_of_each_Region2


    # *****************************************
    # Subcortical regions:
    # ***************************************** 

    # Compute the gravity center for each subcortical region: one scalar per region: AmyL AmyR CaudL CaudR GPL GPR HippoL HippoR PutL PutR ThalL ThalR
    for region in subcorticals_list_checked_with_surfaces:
        # Extract the scalar: region name --> scalar 
        with open(new_parcellation_table) as data_file:    
            data = json.load(data_file)

        my_name_according_to_parcellation_table = 'sub_' + region[-1].lower() + 'h_' +  region[:-1].lower()
        
        for key in data:
            if my_name_according_to_parcellation_table == key["name"]:
                scalar = key["labelValue"]

        # Read the surface of this subcortical region: 
        out_surface_destrieux = './CONTINUITY_QC/sc_surf_organize/surface_merge' + region + '.vtk'

        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(out_surface_destrieux)
        reader.Update()
        
        # Get points of this region: 
        numpy_nodes = vtk_to_numpy( reader.GetOutput().GetPoints().GetData() )

        # Initialize the gravity center: 
        gravity_center_of_this_Region = [0,0,0]

        # Compute the gravity center of this region: average of each coordinates  
        for i in range(len(numpy_nodes)):
            # Compute the average of each cordinates:                    
            my_new_tuple = [0,0,0]
            for v in range(3):
                my_new_tuple[v] = (gravity_center_of_this_Region[v] + numpy_nodes[i][v] ) / 2 #average x, y and z 
    
            # Update the value ot the gravity center: 
            gravity_center_of_this_Region = my_new_tuple

        # Initilize the transformation to move subcortical point in DWI space (same space as icbm space)
        # load surfaces in DWI in Slicer and move each average surfaces thanks to the tab called 'transform' after a threshold to visualize only sc surfaces in the brain surfaces
        # Output transform: LR: -96, PA: -99, IS: -63 (mm)
        x_move = 96; y_move = 99; z_move = -63
        
        gravity_center_of_this_Region[0] = gravity_center_of_this_Region[0] + x_move
        gravity_center_of_this_Region[1] = gravity_center_of_this_Region[1] + y_move
        gravity_center_of_this_Region[2] = gravity_center_of_this_Region[2] + z_move
        
        # Add scalar and gravity center of this region: 
        scalar_sorted_without_duplicate_all.append(int(scalar))
        gravity_center_of_each_Region_all.append(gravity_center_of_this_Region)

    print('scalar_sorted_without_duplicate_all',scalar_sorted_without_duplicate_all)
        

    # *****************************************
    # Update parcellation table: 
    # ***************************************** 

    # Open new_parcellation_table json file to update the coordinates of each region :
    with open(new_parcellation_table) as data_file:    
        data = json.load(data_file)

    for key in data: 
        if key['labelValue'] != '12182': # specific futur script for Brainstrem
            # Get the index of the scalar of this region to be able to find the corresponding cordinates: 
            index_scalar = scalar_sorted_without_duplicate_all.index( int(key['labelValue']) ) 

            # Update the cordiantes of this region :
            key["coord"] = gravity_center_of_each_Region_all[index_scalar]

    # Write :
    with open(new_parcellation_table, 'w') as txtfile:
        json.dump(data, txtfile, indent = 2)



# *************************************************************************************
# Generating subcortical surfaces: generate SALT dir ?
# *************************************************************************************

def generating_subcortical_surfaces(OUT_FOLDER, ID, labeled_image, Labels, LabelNames, 
                                    SegPostProcessCLPPath, GenParaMeshCLPPath, ParaToSPHARMMeshCLPPath, 
                                    sx,sy,sz, nb_iteration_GenParaMeshCLP, spharmDegree, subdivLevel): 

    # Script from Maria: RunSPHARM-PDM_8Year.script  
    # Image with labels: labeled_image: id-T1_SkullStripped_scaled_label.nrrd
    # Labels of subcortical: The number of the labels depends on the input label segmentation .nrrd file 

    # Output folder of subcortical surfaces: 
    OutputDir = os.path.join(OUT_FOLDER, 'my_SALT') 
    if not os.path.exists(OutputDir):
        os.mkdir(OutputDir) 

    # Already created files (by other scripts) located in this folder: 
    TemplateDir = os.path.join('./SALT', 'Template')
    ProcessDir  = os.path.join(os.getcwd() +'/SALT', 'processing')

    # Loop throught all subcortical regions:
    index = 0
    while index < len(Labels) :  
        if Labels[index] != 0: 
            print( 'Doing label', Labels[index], ' corresponding region:', LabelNames[index] )

            # *****************************************
            # SegPostProcessCLP
            # *****************************************

            PPtarget = os.path.join(OutputDir, ID + '-T1_SkullStripped_scaled_label_' + LabelNames[index] +'_pp.nrrd')   #tsch: -r : remove extension 

            if os.path.exists(PPtarget):
                print('SegPostProcessCLP already done')
            else: 
                print('Do SegPostProcessCLP ') 

                # Processing of Binary Labels: it ensures spherical topology of the segmentation
                command = [SegPostProcessCLPPath, labeled_image, # Input image to be filtered (Tissue segmentation file)
                                                  PPtarget, # Output filtered
                                                  '--label', str(Labels[index]), # Extract this label before processing
                                                  '--rescale', #Enforced spacing in x,y and z direction before any processing
                                                  '--space ' + str(sx) +',' + str(sy) + ',' + str(sz)  ] #x,y and z directions
                run_command("SegPostProcessCLP", command) 

                '''
/tools/bin_linux64/SegPostProcessCLP ./input_CONTINUITY/T0054-1-1-6yr-T1_SkullStripped_scaled_label.nrrd ./output_CONTINUITY/T0054-1-1-6yr/my_SALT/T0054-1-1-6yr-T1_SkullStripped_scaled_label_AmyL_pp.nrrd --label 1 --rescale --space 0.5,0.5,0.5


/tools/bin_linux64/GenParaMeshCLP --EulerFile --outEulerName ./output_CONTINUITY/T0054-1-1-6yr/my_SALT/T0054-1-1-6yr-T1_SkullStripped_scaled_label_AmyL_pp_Euler.txt ./output_CONTINUITY/T0054-1-1-6yr/my_SALT/T0054-1-1-6yr-T1_SkullStripped_scaled_label_AmyL_pp.nrrd ./output_CONTINUITY/T0054-1-1-6yr/my_SALT/T0054-1-1-6yr-T1_SkullStripped_scaled_label_AmyL_pp_para.vtk ./output_CONTINUITY/T0054-1-1-6yr/my_SALT/T0054-1-1-6yr-T1_SkullStripped_scaled_label_AmyL_pp_surf.vtk --iter 500 --outLogName ./output_CONTINUITY/T0054-1-1-6yr/my_SALT/T0054-1-1-6yr-T1_SkullStripped_scaled_label_AmyL_pp_genparamesh.txt


/tools/bin_linux64/ParaToSPHARMMeshCLP ./output_CONTINUITY/T0054-1-1-6yr/my_SALT/T0054-1-1-6yr-T1_SkullStripped_scaled_label_AmyL_pp_para.vtk ./output_CONTINUITY/T0054-1-1-6yr/my_SALT/T0054-1-1-6yr-T1_SkullStripped_scaled_label_AmyL_pp_surf.vtk ./output_CONTINUITY/T0054-1-1-6yr/my_SALT/T0054-1-1-6yr-T1_SkullStripped_scaled_label_AmyL_pp_surf --flipTemplateOn --spharmDegree 10 --subdivLevel 15

                '''


            # *****************************************
            # GenParaMeshCLP
            # ***************************************** 

            Paratarget = os.path.join(OutputDir, ID + '-T1_SkullStripped_scaled_label_' + LabelNames[index] +'_pp_para.vtk')
            Surftarget = os.path.join(OutputDir, ID + '-T1_SkullStripped_scaled_label_' + LabelNames[index] +'_pp_surf.vtk')
            
            if os.path.exists(Paratarget):
                print('GenParaMeshCLP already done')
            else: 
                print('Do GenParaMeshCLP')
                genparamesh_log = os.path.join(OutputDir, ID + '-T1_SkullStripped_scaled_label_' + LabelNames[index] + '_pp_genparamesh.txt')
                Euler_txt       = os.path.join(OutputDir, ID + '-T1_SkullStripped_scaled_label_' + LabelNames[index] + '_pp_Euler.txt')

                # Spherical Parametrization : The output is two meshes, one for the surface and one for the spherical parametrization
                command = [GenParaMeshCLPPath, '--EulerFile',  #write a .txt file with the euler number
                                               '--outEulerName', Euler_txt, 
                                               PPtarget, #Input volume to be filtered
                                               Paratarget, #Output Para Mesh (default: _para)
                                               Surftarget, #Output Surface Mesh (default: _surf)
                                               '--iter', str(nb_iteration_GenParaMeshCLP), 
                                               '--outLogName', genparamesh_log]
                run_command("GenParaMeshCLP", command)


            # Check to see if output succfessful
            if not os.path.exists(Surftarget):
                print('Error calculating ',Surftarget)
            else:
                print('Surftarget already done, try to run the SPHARM ')

                SurfVTKtarget =  os.path.join(OutputDir, ID + '-T1_SkullStripped_scaled_label_' + LabelNames[index] +'_pp_surfSPHARM.vtk')

                if os.path.exists(SurfVTKtarget):
                    print("SurfVTKtarget found ")
                else: 
                    # *****************************************
                    # ParaToSPHARMMeshCLP
                    # ***************************************** 

                    print('Do ParaToSPHARMMeshCLP ')

                    Surftarget_prefix = os.path.join(OutputDir, ID + '-T1_SkullStripped_scaled_label_' + LabelNames[index] +'_pp_surf')

                    # Compute SPHARM coefs and associated Mesh : The output is a series of SPHARM coefficients and SPHARM-PDM meshes, 
                    #one set in the original coordinate system, one in the first order ellipsoid aligned coordinate system and one in the Procrustes aligned coordinate system.
                    command = [ParaToSPHARMMeshCLPPath, Paratarget, #input para mesh dataset
                                                        Surftarget, #input surface mesh dataset
                                                        Surftarget_prefix, #Output Directory and base filename
                                                        '--flipTemplateOn', 
                                                        '--spharmDegree', str(spharmDegree) , #set the maximal degree for the SPHARM computation
                                                        '--subdivLevel', str(subdivLevel)] #set the subdivision level for the icosahedron subdivision
                    run_command("ParaToSPHARMMeshCLP", command)

                # Check if successful
                if os.path.exists(SurfVTKtarget):
                    print("SurfVTKtarget complete ")
                else: 
                    print('Error calcullating ',SurfVTKtarget)



        else: #Labels[index] == 0: 
            print("this region will be ignore: ", LabelNames[index])


        index +=  + 1
        print('******************************************************')




# *************************************************************************************
# Create KWM files
# *************************************************************************************

def create_kwm_files(OUT_FOLDER, Labels, LabelNames, number_of_points): 

    # Output folder of subcortical surfaces: 
    OutputDir = os.path.join(OUT_FOLDER, 'my_KWM') 
    if not os.path.exists(OutputDir):
        os.mkdir(OutputDir) 

    for region in range(len(LabelNames)): 

        # Creation of the file for this region: 
        Output_file_region = os.path.join(OUT_FOLDER, 'my_KWM', str(LabelNames[region]) + "_" + str(number_of_points) + "_KWM.txt") 
        if not os.path.exists(Output_file_region):
            os.mkdir(Output_file_region) 


        # Open to 'write and read'
        file = open(Output_file_region,"w+")

        # First line: 'NUMBER_OF_POINTS=1002'
        file.write("NUMBER_OF_POINTS=" + number_of_points + "\n" )

        # Second line: 'DIMENSION=1'
        file.write("DIMENSION=1 \n" )

        # Third line: 'TYPE=Scalar'
        file.write("TYPE=Scalar \n" )

        # Loop to write the label of this region * the number of point (number_of_point lines)
        for i in number_of_points:
            file.write(Labels[region] + "\n" )
