import sys
import os
from math import sqrt
import ij
from ij.gui import GenericDialog
from ij.io import OpenDialog  
from ij.process import ImageStatistics as IS
from java.awt.Dialog import ModalExclusionType 
from ij import IJ
from ij.plugin import ImageCalculator
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
    lowerThreshold = 80;
    upperThreshold = 255;
    stepNumber = 1
    stepThreshold = 5;
    #p3DOCThreshold = 70;
    #p3DOCSlice = 1;
    p3DOCmin = 100;
    p3DOCmax = 2658480;
    gd = GenericDialog( "Parameters" )
    gd.addMessage("Binary mask thresholds")
    gd.addNumericField("Lower Threshold", lowerThreshold, 0)  # show 2 decimals  
    gd.addNumericField("Upper threshold", upperThreshold, 0)  # show 2 decimals  
    gd.addNumericField("Step number", stepNumber, 0)  # show 2 decimals  
    gd.addNumericField("Step threshold", stepThreshold, 0)  # show 2 decimals      
    gd.addMessage("3D Object Counter parameters")
    #gd.addNumericField("threshold", p3DOCThreshold, 0)  # show 2 decimals  
    gd.addNumericField("min.", p3DOCmin, 0)  # show 2 decimals  
    gd.addNumericField("max.", p3DOCmax, 0)  # show 2 decimals  
    gd.showDialog()  
    if gd.wasCanceled():  
        return  
    # Read out the options  
    lowerThreshold = gd.getNextNumber()
    upperThreshold = gd.getNextNumber()
    stepNumber = gd.getNextNumber()
    stepThreshold = gd.getNextNumber()
    #p3DOCThreshold = gd.getNextNumber()
    p3DOCmin = gd.getNextNumber()
    p3DOCmax = gd.getNextNumber()   
    return lowerThreshold, upperThreshold, stepNumber, stepThreshold, p3DOCmin, p3DOCmax      
	#return lowerThreshold, upperThreshold, stepNumber, stepThreshold, p3DOCThreshold, p3DOCmin, p3DOCmax
	
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
# Borrar todas las ventanas 
##########################################################################
def closeall():
	win = IJ.getImage()
	while win != None:
		win.close()
		win = IJ.getImage()				
	return 


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
#imp.show()
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



# Get parameters from dialog
options = getOptions()
if options is not None:  
	lowerThreshold, upperThreshold, stepNumber, stepThreshold, p3DOCmin, p3DOCmax = options  
	#lowerThreshold, upperThreshold, stepNumber, stepThreshold, p3DOCThreshold, p3DOCmin, p3DOCmax = options  
#p3DOCSlice = 1



#genero duplicados de x1 para efectuar umbralización en cada uno
list_x2 = [] #guarda las imagenes umbralizadas
list_x3 = []#guarda las mascaras
list_x4 = []#guarda los esqueletos
ic = ImageCalculator() #para hacer llamadas más cortas de la clase

#UMBRALIZACION
for i in range(stepNumber):#hacer tantas veces como diga stepNumber
	x2= x1.duplicate() 
	x2.setTitle('x2_'+repr(i))
	#x2.show()
	#efectúo la umbralización con OTSU
	#IJ.run("Threshold...")#si se quiere correr las opciones Fiji
	IJ.setThreshold(x2, (lowerThreshold +stepThreshold*i) , upperThreshold, "Black & White")
	IJ.run(x2, "Convert to Mask", "method=Otsu background=Dark black" )
	#se guarda resultado umbralización en list_x2
	list_x2.append( x2 )
	#
	#

#3D OBJECTS COUNTER
for i in range(stepNumber):
	x2  = list_x2[i] 	
	x2_aux = x2.duplicate()
	x2_aux.setTitle('x2_aux')
	#run("3D OC Options", "volume surface nb_of_obj._voxels nb_of_surf._voxels integrated_density mean_gray_value std_dev_gray_value median_gray_value minimum_gray_value maximum_gray_value centroid mean_distance_to_surface std_dev_distance_to_surface median_distance_to_surface centre_of_mass bounding_box show_masked_image_(redirection_requiered) dots_size=5 font_size=10 store_results_within_a_table_named_after_the_image_(macro_friendly) redirect_to=x1")
	IJ.run("3D OC Options", "show_masked_image_(redirection_requiered) dots_size=5 font_size=10 store_results_within_a_table_named_after_the_image_(macro_friendly) redirect_to=x2_aux")
	IJ.run(x2, "3D Objects Counter", "threshold=0 slice=0 min.=" + repr(p3DOCmin)+" max.=" + repr(p3DOCmax)+ " exclude_objects_on_edges objects")
	#guardo la mascara en list_x3
	IJ.selectWindow("Objects map of x2_"+repr(i))		
	#IJ.selectWindow("Masked image for x2_"+repr(i)+" redirect to x2_aux")		
	img = IJ.getImage()
	mask = img.duplicate()##ERROR MISTICO!!!! por alguna clase de magia rara si no duplico img como mask, luego de hacer list_x3.append(img) y luego img.close(), la cantidad de slice declarados en cada elemento de list_x3 no es igual al que contiene la img  correspondiente!!!  
	mask.setTitle('mask_'+repr(i))
	list_x3.append( mask )
	x2_aux.close()	
	img.close()
	#


	
#SKELETONIZE
for i in range(stepNumber):	
	skeleton = list_x3[i].duplicate()	
	skeleton.setTitle('skeleton_'+repr(i))
	IJ.run(skeleton, "Skeletonize (2D/3D)", "");#se corre el plugin sobre la ventana activa que es mask	
	#recorto con la máscara más restrictiva ("la mas corta")
	skeleton = ic.run("AND create stack", list_x3[-1] ,skeleton )
	list_x4.append( skeleton )#guardo el esqueleto
	#skeleton.show()
	

#ADD mask para sumar todos los skeletons
for i in range(stepNumber):	
	skeleton = list_x4[i]
	if i==0:#en caso que esté en la primera iteración
		sum_skeletons = skeleton 
		sum_skeletons.setTitle('sum_skeletons_'+repr(i))
		#sum_skeletons.show()
	else:
		sum_skeletons.setTitle('sum_skeletons_'+repr(i))
		#sum_skeletons.show()
		sum_skeletons = ic.run("Add create stack", sum_skeletons , skeleton )
		#sum_skeletons.close()
		
				
sum_skeletons.setTitle('sumOfSkeletons_'+repr(stepNumber))
sum_skeletons.show()	
mask = list_x3[-1].duplicate()
#modifico el color de mask para visualizar superpuesta a skeleton si efectívamente la cosa está funcionando
#from java.awt import Color #para generar colores en una LUT que ayude en presentacion de imagenes
LUT = mask.getLuts()[0]
LUT.max = 3
mask.setLut(LUT)
#mask.show()
#IJ.run("Window/Level...", "")
maskANDskeleton = ic.run("Transparent-zero create stack", mask, sum_skeletons)
maskANDskeleton.show()
maskANDskeleton.setRoi(551,202,43,48);#no selecciona la ROI solo la marca, hay que aprender a duplicar solo la ROI
IJ.run(maskANDskeleton, "RGB Color", "")#llevo a color la imagen que quiero visualizar
#visualización 3D
#IJ.run("3D Viewer", "");
#call("ij3d.ImageJ3DViewer.setCoordinateSystem", "false");
#call("ij3d.ImageJ3DViewer.add", "Result of DUP_mask_6-1", "None", "Result of DUP_mask_6-1", "0", "true", "true", "true", "2", "0");



'''ERROR MISTICO
>>> x2_aux = x2.duplicate()

>>> x2_aux.setTitle('x2_aux')

>>> x2_aux.show()

>>> x2_aux
img[x2_aux (1024x512x1x1x1)]

>>> list_x2[0]
img[x2_0 (1024x512x1x23x1)]

>>> x2
img[x2_0 (1024x512x1x23x1)]

>>> x2_aux.getStackSize()
1

>>> x2.getStackSize()
23

>>> x2.duplicate()
img[DUP_x2_0 (1024x512x1x23x1)]

>>> x2_aux=x2.duplicate()

>>> x2_aux
img[DUP_x2_0 (1024x512x1x23x1)]

>>> x2_aux.setTitle('x2_aux')

>>> x2_aux
img[x2_aux (1024x512x1x23x1)]'''






'''ERROR MISTICO 
>>> list_x3=[]

>>> for i in range(stepNumber):
	x2  = list_x2[i] 	
	x2_aux = x2.duplicate()
	x2_aux.setTitle('x2_aux')
	#run("3D OC Options", "volume surface nb_of_obj._voxels nb_of_surf._voxels integrated_density mean_gray_value std_dev_gray_value median_gray_value minimum_gray_value maximum_gray_value centroid mean_distance_to_surface std_dev_distance_to_surface median_distance_to_surface centre_of_mass bounding_box show_masked_image_(redirection_requiered) dots_size=5 font_size=10 store_results_within_a_table_named_after_the_image_(macro_friendly) redirect_to=x1")
	IJ.run("3D OC Options", "show_masked_image_(redirection_requiered) dots_size=5 font_size=10 store_results_within_a_table_named_after_the_image_(macro_friendly) redirect_to=x2_aux")
	IJ.run(x2, "3D Objects Counter", "threshold=0 slice=0 min.=" + repr(p3DOCmin)+" max.=" + repr(p3DOCmax)+ " exclude_objects_on_edges objects")
	#guardo la mascara en list_x3
	IJ.selectWindow("Objects map of x2_"+repr(i))		
	#IJ.selectWindow("Masked image for x2_"+repr(i)+" redirect to x2_aux")		
	mask = IJ.getImage()
	mask.setTitle('mask_'+repr(i))
	list_x3.append( mask )

>>> list_x3
[img[mask_0 (1024x512x1x23x1)], img[mask_1 (1024x512x1x23x1)], img[mask_2 (1024x512x1x23x1)], img[mask_3 (1024x512x1x23x1)], img[mask_4 (1024x512x1x23x1)], img[mask_5 (1024x512x1x23x1)], img[mask_6 (1024x512x1x23x1)]]

>>> list_x3 = []

>>> for i in range(stepNumber):
	x2  = list_x2[i] 	
	x2_aux = x2.duplicate()
	x2_aux.setTitle('x2_aux')
	#run("3D OC Options", "volume surface nb_of_obj._voxels nb_of_surf._voxels integrated_density mean_gray_value std_dev_gray_value median_gray_value minimum_gray_value maximum_gray_value centroid mean_distance_to_surface std_dev_distance_to_surface median_distance_to_surface centre_of_mass bounding_box show_masked_image_(redirection_requiered) dots_size=5 font_size=10 store_results_within_a_table_named_after_the_image_(macro_friendly) redirect_to=x1")
	IJ.run("3D OC Options", "show_masked_image_(redirection_requiered) dots_size=5 font_size=10 store_results_within_a_table_named_after_the_image_(macro_friendly) redirect_to=x2_aux")
	IJ.run(x2, "3D Objects Counter", "threshold=0 slice=0 min.=" + repr(p3DOCmin)+" max.=" + repr(p3DOCmax)+ " exclude_objects_on_edges objects")
	#guardo la mascara en list_x3
	IJ.selectWindow("Objects map of x2_"+repr(i))		
	#IJ.selectWindow("Masked image for x2_"+repr(i)+" redirect to x2_aux")		
	mask = IJ.getImage()
	mask.setTitle('mask_'+repr(i))
	list_x3.append( mask )
	x2_aux.close()
	mask.close()

>>> list_x3
[img[mask_0 (1024x512x1x1x1)], img[mask_1 (1024x512x1x1x1)], img[mask_2 (1024x512x1x1x1)], img[mask_3 (1024x512x1x1x1)], img[mask_4 (1024x512x1x1x1)], img[mask_5 (1024x512x1x1x1)], img[mask_6 (1024x512x1x1x1)]]




'''
