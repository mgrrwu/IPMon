import sys
import os
from math import sqrt
import ij
from ij.gui import GenericDialog
from ij.io import OpenDialog  
from ij.process import ImageStatistics as IS
from java.awt.Dialog import ModalExclusionType 
from ij import IJ

###########################################################################
def getChannels():
	gd = GenericDialog( "Select stack's channels" )
	# print gd.getModalityType() 
	# gd.setModal( False )
	# print gd.getModalityType() 
	color = ["red", "green", "blue"]
	gd.addChoice("Channel for mask", color, color[2])
	gd.addChoice("Channel for particles", color, color[1])
	gd.showDialog()
	maskChannel = gd.getNextChoice()  
	partChannel = gd.getNextChoice()  
	if gd.wasCanceled():  
		sys.exit()
	return maskChannel, partChannel
 
##########################################################################
# Create dialog for input parameters
##########################################################################
def getOptions():
    lowerThreshold = 40;
    upperThreshold = 255;
    p3DOCThreshold = 70;
    p3DOCSlice = 1;
    p3DOCmin = 100;
    p3DOCmax = 2658480;
    gd = GenericDialog( "Parameters" )
    gd.addMessage("Binary mask thresholds")
    gd.addNumericField("Lower Threshold", lowerThreshold, 0)  # show 2 decimals  
    gd.addNumericField("Upper threshold", upperThreshold, 0)  # show 2 decimals  
    gd.addMessage("3D Object Counter parameters")
    gd.addNumericField("threshold", p3DOCThreshold, 0)  # show 2 decimals  
    gd.addNumericField("min.", p3DOCmin, 0)  # show 2 decimals  
    gd.addNumericField("max.", p3DOCmax, 0)  # show 2 decimals  
    gd.showDialog()  
    if gd.wasCanceled():  
        return  
    # Read out the options  
    lowerThreshold = gd.getNextNumber()
    upperThreshold = gd.getNextNumber()
    p3DOCThreshold = gd.getNextNumber()
    p3DOCmin = gd.getNextNumber()
    p3DOCmax = gd.getNextNumber()   
    return lowerThreshold, upperThreshold, p3DOCThreshold, p3DOCmin, p3DOCmax
  
##########################################################################
# Remove file
##########################################################################
def RemoveFile ( filename ):
    if os.path.isfile( filename ):
        os.remove( filename )
        
##########################################################################
# Emulate the fantastic C printf function
##########################################################################
def printf(format, *args):
    sys.stdout.write(format % args)

##########################################################################
# Get parameters from the result files.
##########################################################################
def GetParameters ( filename ):
    
    f = open( filename )
    f.readline() # Skip first line
    array = [[float(x) for x in line.split()] for line in f]

    col_id = 0
    col_vol = 3
    col_XM = 17
    col_YM = 18
    col_ZM = 19

    ind = [row[col_id] for row in array]
    vox = [row[col_vol] for row in array]
    XM = [row[col_XM] for row in array]
    YM = [row[col_YM] for row in array]
    ZM = [row[col_ZM] for row in array]

    return ind, vox, XM, YM, ZM

##########################################################################
# Compute euclidian distance
##########################################################################
def L2Distance( a, b ):
    return sqrt((a[0] - b[0]) ** 2 +
                (a[1] - b[1]) ** 2 +
                (a[2] - b[2]) ** 2)    

##########################################################################
# Main function
##########################################################################


#Selección de la imagen de entrada
od = OpenDialog("Select the image stack...", None)  
filename = od.getFileName()
if filename is None:  
	sys.exit()
inputdir = od.getDirectory()
filepath = inputdir + filename  

#se abren las opciones de stack
imp = IJ.openImage( filepath )#por algún motivo no se carga el objeto ImagePlus en la salida imp
imp = IJ.getImage()#línea agregada para obtener el objeto ImagePlus en la variable imp
imp.show()
imp.setTitle( "X0" )

#me quedo con el canal que tiene la cilia que por lo general es el verde (canal C1)
IJ.run( "Split Channels", "" )
IJ.selectWindow("C1-X0")
x1 = IJ.getImage();
x1.setTitle('x1')

#borrado de los canales que no utilizo
IJ.selectWindow("C2-X0")
IJ.getImage().close()
IJ.selectWindow("C3-X0")
IJ.getImage().close()


#genero duplicado de x1 para efectuar umbralización
x2 = x1.duplicate()
x2.setTitle('x2')
x2.show()

# Get parameters from dialog
options = getOptions()
if options is not None:  
	lowerThreshold, upperThreshold, p3DOCThreshold, p3DOCmin, p3DOCmax = options  
p3DOCSlice = 1

IJ.setThreshold(x2, lowerThreshold, upperThreshold)
IJ.run(x2, "Convert to Mask", "method=Otsu background=Dark black" )

#efectúo la umbralización con OTSU
#lowerThreshold = 0  
#upperThresold = 108
#IJ.setThreshold(x2, 0, 108, "Black & White") 
