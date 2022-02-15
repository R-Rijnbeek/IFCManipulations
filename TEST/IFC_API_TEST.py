import sys
sys.path.append('.')
from ifcManipulation import IFCManipulations
import ifcopenshell


#FILE=ifcopenshell.open("C:/Users/r.rijnbeek/Documents/Ifcimportado NSA6 .ifc")
#FILE=ifcopenshell.open("IFC_FILES/Ifcimportado NSA6.ifc")
FILE=ifcopenshell.open("DATA/IFC_FILES/IfcOpenHouse.ifc")
#IFCinstance=IFC_BUILD("ffff","rob","dinsa","ifc","nose","primera prueba")
#FILE=IFCinstance.file 

pr = IFCManipulations(FILE)

pr.DefineProjectObject()
pr.GetWallListFromProyect()
print(pr.GetObjectByGlobalID("2f0veX5Vj59AhEg6WqGnhO"))
print(pr.GetObjectByID(19))
walls = pr.GetObjectByType("IFCWALL")
for wall in walls:
    print(pr.GetVolumenFromObject(wall))