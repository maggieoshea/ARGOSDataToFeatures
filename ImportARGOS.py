##---------------------------------------------------------------------
## ImportARGOS.py
##
## Description: Read in ARGOS formatted tracking data and create a line
##    feature class from the [filtered] tracking points
##
## Usage: ImportArgos <ARGOS folder> <Output feature class> 
##
## Created: Fall 2020
## Author: margaret.oshea@duke.edu (for ENV859)
##---------------------------------------------------------------------

#Import modules
import sys, os, arcpy

arcpy.env.overwriteOutput = True

#Set input variables (hard-wired)
inputFile = 'V:/ARGOSTracking/ARGOSTracking/data/ARGOSData/1997dg.txt'

outputSR = arcpy.SpatialReference(54002)

outputFC = "V:/ARGOSTracking/ARGOSTracking/scratch/ARGOStrack.shp"

## Prepare a new feature class to which we'll add tracking points
# Create an empty feature class; requires the path and name as separate parameters
outPath,outName = os.path.split(outputFC)
arcpy.management.CreateFeatureclass(outPath,outName,"POINT","","","",outputSR)

# Add TagID, LC, IQ, and Date fields to the output feature class
arcpy.AddField_management(outputFC,"TagID","LONG")
arcpy.AddField_management(outputFC,"LC","TEXT")
arcpy.AddField_management(outputFC,"Date","DATE")

#%% Construct a while loop to iterate through all lines in the datafile
# Read Folder
inputFolder = arcpy.GetParameterAsText(0)
outputSR = arcpy.GetParameterAsText(1)
outputFC = arcpy.GetParameterAsText(2)


inputFiles = os.listdir(inputFolder)

# Get the first line of data, so we can use a while loop
lineString = inputFiles.readline()

lineData = lineString.split()
headerLineString = lineData[0]

        #Print the contents of the headerLine
print(headerLineString)
        
# Create the insert cursor
cur = arcpy.da.InsertCursor(outputFC,['Shape@','TagID','LC','Date'])

# Start the while loop
while lineString:
    
    # Set code to run only if the line contains the string "Date: "
    if ("Date :" in lineString):
        
        # Parse the line into a list
        lineData = lineString.split()
        
        # Extract attributes from the datum header line
        tagID = lineData[0]
        
        # Extract location info from the next line
        line2String = inputFiles.readline()
        
        # Parse the line into a list
        line2Data = line2String.split()
        
        # Extract the date we need to variables
        obsLat = line2Data[2]
        obsLon= line2Data[5]
        
        date = lineData[3]
        time = lineData[4]
        LocationClass = lineData[7]
        
        # #Try to convert coordinates to point object
        try:
            # Convert raw coordinate strings to numbers
            if obsLat[-1] == 'N':
                obsLat = float(obsLat[:-1])
            else:
                obsLat = float(obsLat[:-1]) * -1
            if obsLon[-1] == 'E':
                obsLon = float(obsLon[:-1])
            else:
                obsLon = float(obsLon[:-1]) * -1
                
            
            # Create point object from lat/long coordinates
            obsPoint = arcpy.Point()
            obsPoint.X = obsLon
            obsPoint.Y = obsLat
            # Convert the point to a point geometry object with spatial reference
            inputSR = arcpy.SpatialReference(4326)
            obsPointGeom = arcpy.PointGeometry(obsPoint,inputSR)
            
            feature =cur.insertRow((obsPointGeom,tagID,LocationClass,date.replace(".","/") + " " + time)) 
        #Handle any error
        except Exception as e:
            arcpy.AddWarning(f"Error adding record {tagID} to the output: {e}")
        
    # Create a feature object
        
        # Move to the next line so the while loop progresses
    lineString = inputFiles.readline()
  #Delete the cursor object
del cur  
#Close the file object
inputFiles.close()

