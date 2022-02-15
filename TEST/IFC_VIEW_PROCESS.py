import sys
sys.path.append('.')

from ifcManipulation import IFC_Viewer

import ifcopenshell

ifc_file=ifcopenshell.open("DATA/IFC_FILES/IfcOpenHouse.ifc")
IFC_Viewer(ifc_file).DisplayIFC()
