#!/bin/bash

#CSV="civility_brent_extra.csv"

#rm ${CSV}
#printf "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" name dwi t1 mask table surface labelname overlapping create_tar probtrackParam >> ${CSV}

#bash ./run.sh /NIRAL/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/ListsForBrent/Healthy_SubjectsWith_1Yr_2Yr_4Yr_WMData/Conte1Yrs.txt 0 ${CSV}
#bash ./run.sh /NIRAL/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/ListsForBrent/Healthy_SubjectsWith_1Yr_2Yr_4Yr_WMData/Conte2Yrs.txt 0 ${CSV}
#bash ./run.sh /NIRAL/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/ListsForBrent/Healthy_SubjectsWith_1Yr_2Yr_4Yr_WMData/Conte4Yrs.txt 1 ${CSV}
#bash ./run_MBFix_Twin4Yrs.sh /NIRAL/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/ListsForBrent/Healthy_SubjectsWith_1Yr_2Yr_4Yr_WMData/Twin1Yrs.txt 2 
#bash ./run_MBFix_Twin4Yrs.sh /NIRAL/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/ListsForBrent/Healthy_SubjectsWith_1Yr_2Yr_4Yr_WMData/Twin2Yrs.txt 2 
bash ./run_MBFix_Twin4Yrs.sh /NIRAL/work/maria5/EBDS_CIVILITY/LongitudinalConnectome_PostRegError/ListsForBrent/Healthy_SubjectsWith_1Yr_2Yr_4Yr_WMData/Twin4YrsTruncReRunMB2.orig 3 
