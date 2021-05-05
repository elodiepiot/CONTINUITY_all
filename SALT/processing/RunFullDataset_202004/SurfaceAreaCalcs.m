function [ output_args ] = SurfaceAreaCalcs(listOfNames,mainIn,outDir,outName)
%SurfaceAreaCalcs: find all .ascii files and load 
% listOfNames: .txt file with IDs to collect in the final .csv. 
%
tIn = readtable(listOfNames,'ReadVariableNames',false); 
    
   IDs = tIn.Var1; 
   
for iID = 1:numel(IDs)
    ID = IDs{iID}; 
    
    inDir = [mainIn filesep ID filesep 'AutoSegTissue_1year_v2-MultiAtlas' filesep 'SALT' filesep 'SurfaceAreas' ]; 

display(inDir)
    
x = dir(inDir); 

x = x(3:end); 

idx = arrayfun(@(i) ~isempty(regexp(x(i).name,'ascii')), 1:length(x)); 
x = x(idx); 

clear valuesCell
clear values 

for i = 1:length(x) 
    valuesCell{i,1} = load([inDir filesep x(i).name]); 
end 

values = reformatDataCell(valuesCell);

varnames = arrayfun(@(i) strrep(x(i).name,'.ascii.txt',''), 1:length(x),'uniformoutput',0); 

SA{iID} = nansum(values,1)*2; 
 
end 
SAAll = vertcat(SA{:}); 
m = mean(SAAll,1); 
SAAll = [SAAll; m]; 


t= array2table(SAAll,'VariableNames',varnames);
IDs{end+1} = 'mean'; 
t.ID = IDs; 
writetable(t,[outDir filesep outName '_SurfaceAreas.csv']); 

quit()
end