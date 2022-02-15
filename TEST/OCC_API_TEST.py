import sys
sys.path.append('.')
from ifcManipulation import OCC_API

import ifcopenshell
import ifcopenshell.geom

settings=ifcopenshell.geom.settings()
settings.set(settings.USE_PYTHON_OPENCASCADE, True)

ifc_file=ifcopenshell.open("DATA/IFC_FILES/Fase2_COLOR_SHCEDULER_COST.ifc")

walls=ifc_file.by_type("Ifcwall")
for wall in walls:
    shape = ifcopenshell.geom.create_shape(settings, wall).geometry

    shape_instance=OCC_API(shape)
    surface = shape_instance.GetSurfaceFromShape()
    volume = shape_instance.GetVolumenFromShape()
    print(volume)

    wire_list = shape_instance.getAll_TopoDS_Wire_list()
    print(wire_list)

    #print(shape_instance.GetBoxFromShape())