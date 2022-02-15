#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ifcmanipulations/__init__.py: This module has been build to have a standard API to connect with .IFC files
"""
__author__          = "Robert Rijnbeek"
__version__         = "1.0.1"
__maintainer__      = "Robert Rijnbeek"
__email__           = "robert270384@gmail.com"
__status__          = "Development"

__creation_date__   = '15/02/2022'
__last_update__     = '15/02/2022'

# =============== IMPORTS ===============

import uuid
import ifcopenshell
import ifcopenshell.geom

from datetime import datetime
from time import time, gmtime, strftime

import tempfile

from pathlib import Path

from math import sqrt

from OCC.Display.SimpleGui import init_display
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB

from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepGProp import brepgprop_SurfaceProperties, brepgprop_VolumeProperties
from OCC.Core.TopoDS import topods_Wire,topods_Vertex
from OCC.Core.BRep import BRep_Tool

#from ..EXT.Common import get_boundingbox

from OCC.Extend.TopologyUtils import TopologyExplorer


# ===============  CODE  ===============

class IFCManipulations:
    def __init__(self, FILE):
        """
        CONSTRUCTOR FUCTIONS

        """
        self.ifc_file=FILE
        
        self.project = {}

        self.site_list=[]
        self.site={}

        self.building_list=[]
        self.building={}

        self.buildingstorey_list=[]
        self.buildingstorey={}

        self.product_list=[]
        self.product={}

        self.wall_list=[]
        self.wall={}

        self.O = 0., 0., 0.
        self.X = 1., 0., 0.
        self.Y = 0., 1., 0.
        self.Z = 0., 0., 1.

        self.owner_history=None
        self.cost_value_id = 0
        self.task_id=0


        self.settings = ifcopenshell.geom.settings()
        self.settings.set(self.settings.USE_PYTHON_OPENCASCADE, True)

# ====== G E T    B A S E   I N F O R M A T I O N  ======

    def GetBaseInfoFromIFC_File(self):
        self.owner_history = self.ifc_file.by_type("IfcOwnerHistory")[0]
        self.project = self.ifc_file.by_type("IfcProject")[0]
        self.context = self.ifc_file.by_type("IfcGeometricRepresentationContext")[0]
        self.IfcDimensionalExponents = self.ifc_file.by_type("IfcDimensionalExponents")[0]
        self.areaunit = self.GetStandardAreaUnit()
        #self.ifc_O=self.ifc_file.by_type("IFCCARTESIANPOINT")[0]
        self.axis_placment, self.ifc_O, self.dir_z, self.ifc_x = self.GetStandardAxisData()
        return True

    def GetStandardAreaUnit(self):
        si_units=self.ifc_file.by_type("IfcSIUnit")
        for si_unit in si_units:
            if si_unit.UnitType == "AREAUNIT":
                return si_unit

    def GetStandardAxisData(self):
        axis_placments=self.ifc_file.by_type("IFCAXIS2PLACEMENT3D")
        for axis_placment in axis_placments:
            o=axis_placment.Location
            z_dir=axis_placment.Axis
            x_dir=axis_placment.RefDirection
            return axis_placment,o,z_dir,x_dir


# ====== P R O J E C T ======

    def DefineProjectObject(self):
        """
        return Boolean true: When project is difined
        return Boolean false: whene project is not difined
        """
        project_list=self.ifc_file.by_type("IfcProject")
        length_proyect_list=len(project_list)
        if length_proyect_list==1:
            self.project=project_list[0]
            return True
        elif length_proyect_list > 1:
            print("there is more than one proyect in the ifcfile")
            return False
        else:
            print("There is no poyect in the ifc File")
            return False

    def GetProjectInformation(self):
        if self.project == {}:
            print("there is no ifc proyect in ifc file")
            return False
        else:
            obj=self.project.__dict__
            obj["IsDecomposedBy"]=self.project.IsDecomposedBy
            obj["Decomposes"]=self.project.Decomposes
            return obj

# ====== S I T E ======

    def DefineSiteListObject(self):
        sitelist=self.ifc_file.by_type("IfcSite")
        len_sitelist=len(sitelist) 
        if len_sitelist == 0:
            print("there is no site object in ifc file")
            return False
        else:
            self.site_list=sitelist
            self.site=sitelist[0]
            return True



    def GetSiteInformation(self):
        if self.site == {}:
            print("there is no ifc site in ifc file")
            return False
        else:
            obj=self.site.__dict__
            obj["IsDecomposedBy"]=self.site.IsDecomposedBy
            obj["Decomposes"]=self.site.Decomposes
            obj["ContainsElements"]=self.site.ContainsElements
            return obj

    # CREATE SITE
    


    def CreateNewSiteObject(self,NAME="site",OWNER_HISTORY=None,PROJECT=None):
        if OWNER_HISTORY==None:
            OWNER_HISTORY=self.owner_history
        if PROJECT==None:
            PROJECT = self.project
        self.site_placement = self.create_ifclocalplacement(self.ifc_file)
        self.site = self.ifc_file.createIfcSite(self.create_guid(), OWNER_HISTORY, NAME, None, None, self.site_placement, None, None, "ELEMENT", None, None, None, None, None)
        self.container_project = self.ifc_file.createIfcRelAggregates(self.create_guid(), OWNER_HISTORY, "Project Container", None, PROJECT, [self.site])
        return True

# ====== B U L D I N G ======
        
    def DefineBuildingListObject(self):
        buildinglist=self.ifc_file.by_type("IfcBuilding")
        len_buildinglist=len(buildinglist) 
        if len_buildinglist == 0:
            print("there is no Building object in ifc file")
            return False
        else:
            self.building_list=buildinglist
            self.building=buildinglist[0]
            return True   

    def GetBuildingInformation(self):
        if self.building == {}:
            print("there is no ifc building in ifc file")
            return False
        else:
            obj=self.building.__dict__
            obj["IsDecomposedBy"]=self.building.IsDecomposedBy
            obj["Decomposes"]=self.building.Decomposes
            obj["ContainsElements"]=self.building.ContainsElements
            return obj  

    # CREATE BUILDING
    def CreateNewBuildingObject(self,NAME="building",OWNER_HISTORY=None,SITE=None,SITE_PLACEMENT=None):
        if OWNER_HISTORY==None:
            OWNER_HISTORY=self.owner_history
        if SITE==None:
            SITE = self.site
        if SITE_PLACEMENT==None:
            SITE_PLACEMENT=self.site_placement
        self.building_placement = self.create_ifclocalplacement(self.ifc_file, relative_to=SITE_PLACEMENT)
        self.building = self.ifc_file.createIfcBuilding(self.create_guid(), OWNER_HISTORY, 'Building', None, None, self.building_placement, None, None, "ELEMENT", None, None, None)
        self.container_site = self.ifc_file.createIfcRelAggregates(self.create_guid(), OWNER_HISTORY, "Site Container", None, SITE, [self.building])
        return True

# ====== B U L D I N G    S T O R E Y ======

    def DefineBuildingStoreyListObject(self):
        buildingstoreylist=self.ifc_file.by_type("IfcBuildingStorey")
        len_buildingstoreylist=len(buildingstoreylist) 
        if len_buildingstoreylist == 0:
            print("there is no Building Storey object in ifc file")
            return False
        else:
            self.buildingstorey_list=buildingstoreylist
            self.buildingstorey=buildingstoreylist[0]
            return True

    def GetBuildingStoreyInformation(self):
        if self.buildingstorey == {}:
            print("there is no ifc building storey in ifc file")
            return False
        else:
            obj=self.buildingstorey.__dict__
            obj["IsDecomposedBy"]=self.buildingstorey.IsDecomposedBy
            obj["Decomposes"]=self.buildingstorey.Decomposes
            obj["ContainsElements"]=self.buildingstorey.ContainsElements
            return obj   

    # CREATE BUILDING STOREY
    def CreateNewBuildingStoreyObject(self,NAME="building_storey",OWNER_HISTORY=None,BUILDING=None,BUILDING_PLACEMENT=None):
        if OWNER_HISTORY==None:
            OWNER_HISTORY=self.owner_history
        if BUILDING==None:
            BUILDING = self.building
        if BUILDING_PLACEMENT==None:
            BUILDING_PLACEMENT=self.building_placement
        elevation=0.0
        self.storey_placement = self.create_ifclocalplacement(self.ifc_file, relative_to=BUILDING_PLACEMENT)
        self.building_storey = self.ifc_file.createIfcBuildingStorey(self.create_guid(), OWNER_HISTORY, 'Storey', None, None, self.storey_placement, None, None, "ELEMENT", elevation)
        self.container_storey = self.ifc_file.createIfcRelAggregates(self.create_guid(), OWNER_HISTORY, " Building Container", None, BUILDING, [self.building_storey])
        return True

# ====== W A L L =====

    def GetWallListFromProyect(self):
        walllist=self.ifc_file.by_type("IfcWall")
        len_walllist=len(walllist)
        if len_walllist == 0:
            print("thee are no ifc wall in file")
            return False
        else:
            self.wall_list=walllist
            self.wall=walllist[0]
            return True

    def SetWallObject(self,OBJECT):
        try:
            if OBJECT.is_a("IfcWall"):
                self.wall = OBJECT
                return True
            else:
                print("OBJECT is a ifc element but not a ifc wall element")
                return False 
        except:
            print("OBJECT is not a standart ifc wall element")
            return False

    def GetWallInformation(self):
        if self.wall == {}:
            print("there is no ifc wall defined")
            return False
        else:
            obj=self.wall.__dict__
            obj["IsDecomposedBy"]=self.wall.IsDecomposedBy
            obj["Decomposes"]=self.wall.Decomposes
            obj["ContainedInStructure"]=self.wall.ContainedInStructure
            obj["HasAssociations"]=self.wall.HasAssociations
            obj["HasOpenings"]=self.wall.HasOpenings

            return obj

# ====== P R O D U C T S ======   
     
    def GetProductListFromProject(self):
        productlist=self.ifc_file.by_type("IfcProduct")
        len_productlist = len(productlist)
        if len_productlist == 0:
            print("There is no products in ifc file")
            return False
        else:
            self.product_list=productlist
            self.product = productlist[0]
            return True

    def SetProductObject(self,OBJECT):
        try:
            if OBJECT.is_a("IfcProduct"):
                self.product = OBJECT
                return True
            else:
                print("OBJECT is a ifc element but not a ifc product element")
                return False 
        except:
            print("OBJECT is not a standart ifc Product element")
            return False

# ====== S H A P E S ======
    
    def GetShapeFromProduct(self, PRODUCT):
        shape = ifcopenshell.geom.create_shape(self.settings, PRODUCT).geometry
        return shape

# ====== G E T    G E O M E T R Y    I N F O R M A T I O N    F R O M    I F C O B J E C T   ======
    
    def GetVolumenFromObject(self,IFC_OBJECT):
        shape=self.GetShapeFromProduct(IFC_OBJECT)
        shape_instance = OCC_API(shape)
        volumen=shape_instance.GetVolumenFromShape()
        return volumen

    def GetTotalSurfaceFromObject(self,IFC_OBJECT):
        shape=self.GetShapeFromProduct(IFC_OBJECT)
        shape_instance = OCC_API(shape)
        surface=shape_instance.GetSurfaceFromShape()
        return surface

    def GetMaxAreaOfFaceFromObject(self,IFC_OBJECT):
        shape=self.GetShapeFromProduct(IFC_OBJECT)
        shape_instance = OCC_API(shape)
        area=shape_instance.GetMaxAreaOfFacesFromShape()
        return area

    def GetLenghtFromObject(self,IFC_OBJECT):
        shape=self.GetShapeFromProduct(IFC_OBJECT)
        shape_instance = OCC_API(shape)
        lenght=shape_instance.GetMaxDistanceFromShape()
        return lenght

    def GetBoxFromObject(self,IFC_OBJECT):
        shape=self.GetShapeFromProduct(IFC_OBJECT)
        shape_instance = OCC_API(shape)
        box =shape_instance.GetBoxFromShape()
        return box
    

# ====== O W N E R =======

    def GetOwnerInformationFromObject(self,OBJECT):
        try:
            owner_object=OBJECT.OwnerHistory
            owner_object=owner_object.__dict__
            headers=list(owner_object.keys())
            for key in headers:
                value=owner_object[key]
                if str(type(value)) == "<class 'ifcopenshell.entity_instance.entity_instance'>":
                    owner_object[key]=value.__dict__
                    #print(value)
                    secondlevel=owner_object[key]
                    headers_second_level=list(secondlevel.keys())
                    for key1 in headers_second_level:
                        value2=secondlevel[key1]
                        if str(type(value2)) == "<class 'ifcopenshell.entity_instance.entity_instance'>":
                            owner_object[key][key1]=value2.__dict__
            return owner_object
        except:
            print("problems to get owner information from object")
            return False

# ====== G E T    S C H E D U L E D T A S K   I N F O R M A T I O N    F R O M    P R O D U C T ======

    def GetDateTime_from_ScheduleObject(self,SCHEDULE_OBJECT):
        """
        INPUT: 
            - SCHEDULE_OBJECT: Is the IfcDateTime Object
        OUTPUT:
            - {"year":Year,"Month":Month,"Day":Day,"Hour":Hour,"Minute":Minute,"Second":Second}
        """
        date_object=SCHEDULE_OBJECT.DateComponent
        time_object=SCHEDULE_OBJECT.TimeComponent
        time_object={
                    "year":date_object.YearComponent,
                    "Month":date_object.MonthComponent,
                    "Day":date_object.DayComponent,
                    "Hour":time_object.HourComponent,
                    "Minute":time_object.MinuteComponent,
                    "Second":0
                    }
        return time_object

    def Get_Time_Date(self, IFC_PRODUCT):
        """
        INPUT: 
            - IFC_PRODUCT: Is an standard IFC Product
        OUTPUT: Typle of lenght 2 
            DATE FOUND => TRUE
                - [0] start_date  = {"year":Year,"Month":Month,"Day":Day,"Hour":Hour,"Minute":Minute,"Second":Second}
                - [1] finish_date = {"year":Year,"Month":Month,"Day":Day,"Hour":Hour,"Minute":Minute,"Second":Second}
             DATE FOUND => FALSE
                - [0] start_date  = None
                - [1] finish_date = None
        """
        assignments = IFC_PRODUCT.HasAssignments
        if len(assignments)>0:
            for assigment in assignments:
                if assigment.is_a("IfcRelAssignsToProcess"):
                    relating_process = assigment.RelatingProcess
                    if relating_process.is_a("IfcTask"):
                        has_assignments = relating_process.HasAssignments
                        if len(has_assignments)>0:
                            for has_assignment in has_assignments:
                                if has_assignment.is_a("IfcRelAssignsTasks"):
                                    time_for_task = has_assignment.TimeForTask
                                    finish_date_object=time_for_task.ScheduleFinish
                                    start_date_object=time_for_task.ScheduleStart
                                    finish_date=self.GetDateTime_from_ScheduleObject(finish_date_object)
                                    start_date=self.GetDateTime_from_ScheduleObject(start_date_object)
                                    return start_date, finish_date
        start_date = None
        finish_date = None      
        return start_date, finish_date  


# ======  A G R E G A T E   S C H E D U L E D T A S K    T O    P R O D U C T    =======

    def GetCurrentDateTimeList(self):
        return list(datetime.now().timetuple())[0:6]
    
    def CreateScheduledTask(self,OWNER_HISTORY=None):
        if OWNER_HISTORY==None:
            OWNER_HISTORY=self.owner_history
        current_date=self.GetCurrentDateTimeList()
        finish_date=[current_date[0],current_date[1],current_date[2],9,0,0]
        [begin_year,begin_month,begin_day,begin_hour,begin_minute,begin_second]=current_date
        [finish_year,finish_month,finish_day,finish_hour,finish_minute,finish_seconds]=finish_date
        ifc_begin_local_time=self.ifc_file.createIfcLocaltime(begin_hour,begin_minute,begin_second,None,None)     #Optional link timezone
        ifc_finish_local_time=self.ifc_file.createIfcLocaltime(finish_hour,finish_minute,finish_seconds,None,None)#Optional link timezone
        ifc_begin_date=self.ifc_file.createIfcCalendardate(begin_month,begin_day,begin_year)
        #ifc_finish_date=self.ifc_file.createIfcCalendardate(finish_month,finish_day,finish_year)
        ifc_begin_date_and_time=self.ifc_file.createIfcDateandtime(ifc_begin_date,ifc_begin_local_time)
        ifc_finish_date_and_time=self.ifc_file.createIfcDateandtime(ifc_begin_date,ifc_finish_local_time)
        self.ifc_workschedule=self.ifc_file.createIfcWorkschedule(self.create_guid(),OWNER_HISTORY,"Work schedule",None,None,'Python auto Scheduled agregates',ifc_begin_date_and_time,None,None,None,None,ifc_finish_date_and_time,None,None,None)
        ifc_workplan=self.ifc_file.createIfcWorkplan(self.create_guid(),OWNER_HISTORY,"Work plan",None,None,'Python auto Scheduled agregates',ifc_begin_date_and_time,None,None,None,None,ifc_finish_date_and_time,None,None,None)
        self.ifc_file.createIfcRelaggregates(self.create_guid(),OWNER_HISTORY,None,None,ifc_workplan,[self.ifc_workschedule])
        return True
    
    
    def CreateIFCDateTime(self,DATE_LIST):
        (year,month,day,hour,minute,second)=DATE_LIST
        ifc_begin_local_time=self.ifc_file.createIfcLocaltime(hour,minute,None,None,None)
        ifc_begin_date=self.ifc_file.createIfcCalendardate(day,month,year)
        ifc_begin_date_and_time=self.ifc_file.createIfcDateandtime(ifc_begin_date,ifc_begin_local_time)
        return ifc_begin_date_and_time

    def WorkingTimeForTask(self,BEGIN_DATE_LIST,FINISH_DATE_LIST):
        (begin_year,begin_month,begin_day,begin_hour,begin_minute,begin_second)=BEGIN_DATE_LIST
        (finish_year,finish_month,finish_day,finish_hour,finish_minute,finish_second)=FINISH_DATE_LIST
        time_difference = ((datetime(finish_year,finish_month,finish_day,finish_hour,finish_minute,finish_second)-datetime(begin_year,begin_month,begin_day,begin_hour,begin_minute,begin_second)).total_seconds())/3.
        return time_difference

    def AgregateScheduledTaskToObject(self,IFC_OBJECT, BEGIN_DATE, FINISH_DATE, OWNER_HISTORY=None):
        if OWNER_HISTORY==None:
            OWNER_HISTORY=self.owner_history
        
        begin_date=BEGIN_DATE
        finish_date=FINISH_DATE
        
        ifc_begin_date_and_time=self.CreateIFCDateTime(begin_date)
        ifc_finish_date_and_time=self.CreateIFCDateTime(finish_date)

        time_difference=self.WorkingTimeForTask(begin_date,finish_date)

        ifc_scheduletimecontrol= self.ifc_file.createIfcscheduletimecontrol(self.create_guid(),OWNER_HISTORY,None,None,None,None,None,None,ifc_begin_date_and_time,None,None,None,ifc_finish_date_and_time,time_difference,None,None,None,None,None,None,None,None,None)#calculo de segudos
        task_name = ('task_' + str(self.task_id))
        task_id = ("ST000"+(str(self.task_id + 2))+"0")
        ifc_task = self.ifc_file.createIfcTask(self.create_guid(),OWNER_HISTORY,task_name,'1',None,task_id,None,None,False,None)#¿1,stooo2o, f ?
        self.ifc_file.createIfcRelassignstasks(self.create_guid(),OWNER_HISTORY,None,None,[ifc_task],None ,self.ifc_workschedule ,ifc_scheduletimecontrol)#before ifc_scheduletimecontrol #88
        self.ifc_file.createIfcRelassignstoprocess(self.create_guid(),OWNER_HISTORY,None,None,[IFC_OBJECT],None,ifc_task,None)
        self.task_id +=1
        return True


# ======  G E T   T E X T U R E    I N F O M A T I O N   F R O M   P R O D U C T   =======

    def GetTextureFromIfcProduct(self,IFC_PRODUCT,MODE=""):
        """
        INPUT:
            - PRODUCT => IfcProduct object
        OUTPUT:
            - Typle of lenght 4
                COLOR FOUND: True
                    - [0] RED => Float in range (0,1)
                    - [1] GREEN => Float in range (0,1)
                    - [2] BLUE => Float in range (0,1)
                    - [3] OPACITY => Float in range (0,1)
                COLOR FOUND: False
                    - [0] RED     = 1. Float 
                    - [1] GREEN   = 1. Float 
                    - [2] BLUE    = 1. Float
                    - [3] OPACITY = 1. Float
        """
        try:
            representation=IFC_PRODUCT.Representation
            representations=representation.Representations
            for the_representation in representations:
                if (the_representation.RepresentationIdentifier in ["Body","Facetation"]):
                    #the_representation=representations[0]
                    Items=the_representation.Items
                    Item=Items[0]
                    StyledByItems=Item.StyledByItem
                    if len(StyledByItems)>0:
                        StyledByItem=StyledByItems[0]
                        Styles=StyledByItem.Styles
                        Style=Styles[0]
                        Styles_2=Style.Styles
                        Style_2=Styles_2[0]
                        Styles_3=Style_2.Styles
                        Style_3=Styles_3[0]
                        Surface_Colour=Style_3.SurfaceColour
                        Red=Surface_Colour.Red
                        Green=Surface_Colour.Green
                        Blue=Surface_Colour.Blue
                        if "Transparency" in list(Style_3.__dict__):
                            transparency = Style_3.Transparency
                            if transparency is None:
                                opacity = 1.
                            else:
                                if MODE == "Sketchup":
                                    opacity = transparency
                                else:
                                    opacity = 1-transparency
                        else:
                            opacity = 1.
                        return Red, Green, Blue, opacity
            Red=1.
            Green=1.
            Blue=1.
            opacity=1.
            return Red, Green, Blue, opacity
        except:
            Red=1.
            Green=1.
            Blue=1.
            opacity=1.
            return Red, Green, Blue, opacity


# ====== A G R E G A T E    T E X T U R E   T O    P R O D U C T  ======

    def ApplyTextureToProduct(self,PRODUCT,RGBA):
        """

        """
        solid_is=""
        representation=PRODUCT.Representation
        representations=representation.Representations
        for shape_representation in representations:
                if shape_representation.RepresentationIdentifier=="Body":
                    Items = shape_representation.Items
                    if len(Items)>0:
                        solid=Items[0]
                        solid_is=solid.is_a()


        if (len(RGBA)==4) and (solid_is in ["IfcExtrudedAreaSolid","IfcFacetedBrep"]):
            red= RGBA[0]
            green= RGBA[1]
            blue= RGBA[2]
            opacity=RGBA[3]
            ifc_color = self.ifc_file.createIfcColourRGB(None, red, green, blue)
            surface_rendering = self.ifc_file.createIfcSurfacestylerendering(ifc_color, opacity, None, None, None, None, None, None, "NOTDEFINED")
            surface_style = self.ifc_file.createIfcSurfacestyle(None, "POSITIVE", [surface_rendering])
            presentation_style_asignment = self.ifc_file.createIfcPresentationstyleassignment([surface_style])
            self.ifc_file.createIfcStyleditem(solid, [presentation_style_asignment], None)
            return True
        else:
            print("Wrong data format")
            return False

# ====== G E T   C O S T   I N F O R M A T I O N   F R O M    P R O D U C T ======

    def Get_CostFromProduct(self, IFC_PRODUCT):
        """
        INPUT:
            - PRODUCT => IfcProduct object
        OUTPUT:
            - Typle of lenght 2
                COST FOUND: True
                    - [0] COST_VALUE    => FLOAT
                    - [1] COST_UNIT     => STRING
                COST FOUND: False
                    - [0] COST_VALUE    = None
                    - [1] COST_UNIT     = None 
        """
        Assigments = IFC_PRODUCT.HasAssignments
        if len(Assigments)>0:
            for assigment in Assigments:
                if assigment.is_a("IfcRelAssignsToControl"):
                    related_control= assigment.RelatingControl
                    if related_control.is_a("IfcCostItem"):
                        associations=related_control.HasAssociations
                        if len(associations)>0:
                            for association in associations:
                                if association.is_a("IfcRelAssociatesAppliedValue"):
                                    Ifc_cost_value=association.RelatingAppliedValue
                                    cost_value=Ifc_cost_value.AppliedValue.wrappedValue
                                    UnitBasis=Ifc_cost_value.UnitBasis
                                    cost_unit=UnitBasis.UnitComponent.Currency
                                    return cost_value, cost_unit
        cost_value = None
        cost_unit = None
        return cost_value, cost_unit

# ===== A G R E G A T E     C O S T   I N F O R M A T I O N    T O    P R O D U C T =======
    
    def CreateIfcCostItem(self,COSTVALUE):
        cost_value=COSTVALUE
        ifc_monetary_measure = self.ifc_file.createIfcMonetaryMeasure(cost_value)
        ifc_value_component = self.ifc_file.createIfcReal(cost_value)
        ifc_unit_component = self.ifc_file.createIfcMonetaryUnit("EUR")
        ifc_Measure_with_Unit = self.ifc_file.createIfcMeasureWithUnit(ifc_value_component,ifc_unit_component)
        ifc_cost_value=self.ifc_file.createIfcCostValue("cost_value_" + str(self.cost_value_id) ,"cost_description",ifc_monetary_measure,ifc_Measure_with_Unit,None,None,"Estimated cost",None)#cambiar 0.6.0a0 por 0.6.0a1 sino pasar al version 050
        return ifc_cost_value

    def ApplyCostToProduct(self, IFC_OBJECT, COSTVALUE,OWNER_HISTORY=None): 
        if OWNER_HISTORY==None:
            OWNER_HISTORY=self.owner_history
        ifc_cost_value = self.CreateIfcCostItem(COSTVALUE)     
        ifc_cost_item = self.ifc_file.createIfcCostItem(self.create_guid(),OWNER_HISTORY,"cost_item_" + str(self.cost_value_id),"description of cost item",None)
        ifc_aplied_to_value = self.ifc_file.createIfcRelAssociatesAppliedValue(self.create_guid(), OWNER_HISTORY,"costitem - costvalue relationnship","The relation to connect the cost value to a cost item",[ifc_cost_item],ifc_cost_value)
        ifc_cost_assigns_to_control = self.ifc_file.createIfcRelAssignsToControl(self.create_guid(),OWNER_HISTORY,"costitem - object relationnship","The relation to connect the cost item to a ifcobject",[IFC_OBJECT],"PRODUCT",ifc_cost_item)
        self.cost_value_id += 1
        return True

# ====== A P P L Y    B A S E    Q U A L I T I E S     T O   O B J E C T   =======

    def ApplyBaseQualitiesToIfcObject(self,IFC_OBJECT,OWNER_HISTORY=None):
        if OWNER_HISTORY==None:
            OWNER_HISTORY=self.owner_history
        volumen_value=self.GetVolumenFromObject(IFC_OBJECT)
        surface_value=self.GetMaxAreaOfFaceFromObject(IFC_OBJECT)
        #surface_value_1=self.GetTotalSurfaceFromObject(IFC_OBJECT) # Maybe we must catch only the biggest area of the wall
        lenght_value=self.GetLenghtFromObject(IFC_OBJECT) # Maybe need to implement some filter actions when geometry is complex or have a lot of faces
        quality_volumen = self.ifc_file.createIfcQuantityVolume("Volume", "Total Volume of the ifc_object", None, volumen_value)
        quality_surface = self.ifc_file.createIfcQuantityArea("Area", "Total Area of the ifc_object", None, surface_value)
        #quality_surface_1 = self.ifc_file.createIfcQuantityArea("Area", "Total Area2 of the ifc_object", None, surface_value_1)
        quality_lenght = self.ifc_file.createIfcQuantityLength("Length", "Length of the ifc_object", None, lenght_value )
        quantity_values  = [quality_volumen,quality_surface,quality_lenght]
        element_quantity = self.ifc_file.createIfcElementQuantity(self.create_guid(), OWNER_HISTORY, "BaseQuantities", None, None, quantity_values)
        self.ifc_file.createIfcRelDefinesByProperties(self.create_guid(), OWNER_HISTORY, None, None, [IFC_OBJECT], element_quantity)
        return True

# ====== A P P L Y   P R O P E R T I E S    S I N G L E    V A L U E S    T O    O B J E C T   =====

    def ApplyPropertySingleValueToObject(self,IFC_OBJECT,OWNER_HISTORY=None):
        if OWNER_HISTORY==None:
            OWNER_HISTORY=self.owner_history
        surface_value=self.GetTotalSurfaceFromObject(IFC_OBJECT)
        ifc_value = self.ifc_file.createIfcReal(surface_value)
        total_surface=self.ifc_file.createIfcPropertySingleValue("Total surface", "total surface",ifc_value, self.areaunit)
        property_values = [total_surface]
        property_set = self.ifc_file.createIfcPropertySet(self.create_guid(), OWNER_HISTORY, "Pset_WallCommon", None, property_values)
        self.ifc_file.createIfcRelDefinesByProperties(self.create_guid(), OWNER_HISTORY, None, None, [IFC_OBJECT], property_set)
        return True  

# ====== G E T   F U N C T I O N S  =====

    def GetObjectByGlobalID(self,GLOBALID):
        try:
            return self.ifc_file.by_guid(GLOBALID)
        except:
            return False

    def GetObjectByID(self,ID):
        try:
            return self.ifc_file.by_id(ID)
        except:
            return False
    
    def GetObjectByType(self,TYPE):
        try:
            return self.ifc_file.by_type(TYPE)
        except:
            return False

# ===== U N I T   I N F O R M A T I O N =======

    def GetUnitInformationFromProyect(self, OBJECT):
        try:
            unit_object=OBJECT.UnitsInContext
            unit_object=unit_object.__dict__
            headers=list(unit_object.keys())
            for key in headers:
                value=unit_object[key]
                if str(type(value)) == "<class 'tuple'>":
                    #value = list(value)
                    for element in value:
                        if str(type(element)) == "<class 'ifcopenshell.entity_instance.entity_instance'>":
                            index = value.index(element)
                            unit_object[key]=list(unit_object[key])
                            unit_object[key][index]=element.__dict__
                            secondlevel=unit_object[key][index]
                            headers_second_level=list(secondlevel.keys())
                            for key1 in headers_second_level:
                                value2=secondlevel[key1]
                                if str(type(value2)) == "<class 'ifcopenshell.entity_instance.entity_instance'>":
                                    unit_object[key][index][key1]=value2.__dict__
                                    thirdlevel=unit_object[key][index][key1]
                                    headers_third_level=list(thirdlevel.keys())
                                    #print(headers_third_level)
                                    for key2 in headers_third_level:
                                        value3=thirdlevel[key2]
                                        if str(type(value3))=="<class 'ifcopenshell.entity_instance.entity_instance'>":
                                            unit_object[key][index][key1][key2]=value3.__dict__
            return unit_object
        except:
            print("problems to te unit nformation fron proyect file")
            return False

# ===== H I E R A R C H Y    F U N C T I O N S =====

    def IsDecomposedBy(self, OBJECT):
        try:
            LIST=[]
            decom=OBJECT.IsDecomposedBy
            for row1 in decom:
                decom1=row1.RelatedObjects
                for row2 in decom1:
                    LIST.append(row2)
            return LIST
        except:
            print("Object has no 'Isdecomposesby' atribute")
            return False
    
    def Decomposes(self,OBJECT):
        try:
            LIST=[]
            decom=OBJECT.Decomposes
            for row1 in decom:
                decom1=row1.RelatingObject
                LIST.append(decom1)
            return LIST
        except:
            print("Object has no Decomposes atribute")
            return False

    def ObjectOFSameGroup(self,OBJECT):
        try:
            LIST=[]
            if OBJECT.is_a("IfcProject"):
                decom=OBJECT.IsDecomposedBy
                for row1 in decom:
                    decom1=row1.RelatingObject
                    LIST.append(decom1)
                return LIST
            else:
                decom=OBJECT.Decomposes
                for row1 in decom:
                    decom1=row1.RelatedObjects
                    for row2 in decom1:
                        LIST.append(row2)
                return LIST
        except:
            print("Object has no 'Isdecomposesby' atribute")
            return False

    def ContainsElements(self,OBJECT):
        try:
            LIST=[]
            elements=OBJECT.ContainsElements
            for row1 in elements:
                elements1=row1.RelatedElements
                for row2 in elements1:
                    LIST.append(row2)
            return LIST
        except:
            print("Object has no 'ContainsElements' atribute")
            return False

# ===== I F C    W R I T E ======

    def IFCWrite(self,PATH):
        if Path(PATH).parent.is_dir():
            self.ifc_file.write(PATH)
            return True
        else:
            print("Directory do not exists")
            return False

# ===== G E N E R I C   F U N C T I O N S ========

 
    def create_ifcaxis2placement(self,ifcfile, point=None, dir1=None, dir2=None):
        """
        Creates an IfcAxis2Placement3D from Location, Axis and RefDirection specified as Python tuples
        """
        if (point==None) and (dir1==None) and (dir2 == None):
            return self.axis_placment
        else:
            if point==None:
                point=self.O
            if dir1==None:
                dir1=self.Z
            if dir2==None:
                dir2=self.X

            
            point = ifcfile.createIfcCartesianPoint(point)
            dir1 = ifcfile.createIfcDirection(dir1)
            dir2 = ifcfile.createIfcDirection(dir2)
            axis2placement = ifcfile.createIfcAxis2Placement3D(point, dir1, dir2)
            return axis2placement

 
    def create_ifclocalplacement(self,ifcfile, point=None, dir1=None, dir2=None, relative_to=None):
        
        """
        Creates an IfcLocalPlacement from Location, Axis and RefDirection, specified as Python tuples, and relative placement
        """
        if (point==None) and (dir1==None) and (dir2 == None):
            ifclocalplacement2 = ifcfile.createIfcLocalPlacement(relative_to,self.axis_placment)
            return ifclocalplacement2 
        else:
            if point==None:
                point=self.O
            if dir1==None:
                dir1=self.Z
            if dir2==None:
                dir2=self.X
            axis2placement = self.create_ifcaxis2placement(ifcfile,point,dir1,dir2)
            ifclocalplacement2 = ifcfile.createIfcLocalPlacement(relative_to,axis2placement)
            return ifclocalplacement2


    def create_ifcpolyline(self,ifcfile, point_list):
        """
        Creates an IfcPolyLine from a list of points, specified as Python tuples
        """
        ifcpts = []
        for point in point_list:
            point = ifcfile.createIfcCartesianPoint(point)
            ifcpts.append(point)
        polyline = ifcfile.createIfcPolyLine(ifcpts)
        return polyline

    def create_ifcpolyloop(self,ifcfile, point_list):
        """
        Creates an IfcPolyLoop from a list of points, specified as Python tuples
        """
        ifcpts = []
        for point in point_list:
            point = ifcfile.createIfcCartesianPoint(point)
            ifcpts.append(point)
        polyloop = ifcfile.createIfcPolyLoop(ifcpts)
        return polyloop
    
 
    def create_ifcextrudedareasolid(self,ifcfile, point_list, ifcaxis2placement, extrude_dir, extrusion):
        """
        Creates an IfcExtrudedAreaSolid from a list of points, specified as Python tuples
        """
        polyline = self.create_ifcpolyline(ifcfile, point_list)
        ifcclosedprofile = ifcfile.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
        ifcdir = ifcfile.createIfcDirection(extrude_dir)
        ifcextrudedareasolid = ifcfile.createIfcExtrudedAreaSolid(ifcclosedprofile, ifcaxis2placement, ifcdir, extrusion)
        return ifcextrudedareasolid

    def create_guid(self):
        return ifcopenshell.guid.compress(uuid.uuid1().hex)


    """
    def UnfoldingOfObject(self,OBJECT):
        
        INPUT: IFC OBJECT Afther  <.__dict__>
        OUTPUT: IFC OBJECT UNFOLDED
        
        headers=list(OBJECT.keys())
        for key in headers:
                value=OBJECT[key]
                if str(type(value)) == "<class 'ifcopenshell.entity_instance.entity_instance'>":
                    OBJECT[key]=value.__dict__
        return OBJECT
    """

def GetTextureFromIfcProduct(IFC_PRODUCT,MODE=""):
    """
    INPUT:
        - PRODUCT => IfcProduct object
    OUTPUT:
        - Typle of lenght 4
            COLOR FOUND: True
                - [0] RED => Float in range (0,1)
                - [1] GREEN => Float in range (0,1)
                - [2] BLUE => Float in range (0,1)
                - [3] OPACITY => Float in range (0,1)
            COLOR FOUND: False
                - [0] RED     = 1. Float 
                - [1] GREEN   = 1. Float 
                - [2] BLUE    = 1. Float
                - [3] OPACITY = 1. Float
    """
    try:
        representation=IFC_PRODUCT.Representation
        representations=representation.Representations
        for the_representation in representations:
            if (the_representation.RepresentationIdentifier in ["Body","Facetation"]):
                #the_representation=representations[0]
                Items=the_representation.Items
                Item=Items[0]
                StyledByItems=Item.StyledByItem
                if len(StyledByItems)>0:
                    StyledByItem=StyledByItems[0]
                    Styles=StyledByItem.Styles
                    Style=Styles[0]
                    Styles_2=Style.Styles
                    Style_2=Styles_2[0]
                    Styles_3=Style_2.Styles
                    Style_3=Styles_3[0]
                    Surface_Colour=Style_3.SurfaceColour
                    Red=Surface_Colour.Red
                    Green=Surface_Colour.Green
                    Blue=Surface_Colour.Blue
                    if "Transparency" in list(Style_3.__dict__):
                        transparency = Style_3.Transparency
                        if transparency is None:
                            opacity = 1.
                        else:
                            if MODE == "Sketchup":
                                opacity = transparency
                            else:
                                opacity = 1-transparency
                    else:
                        opacity = 1.
                    return Red, Green, Blue, opacity
        Red=1.
        Green=1.
        Blue=1.
        opacity=1.
        return Red, Green, Blue, opacity
    except:
        Red=1.
        Green=1.
        Blue=1.
        opacity=1.
        return Red, Green, Blue, opacity

class IFC_Viewer(IFCManipulations):
    def __init__(self,IFC_FILE):
        self.ifc_file = IFC_FILE
        self.settings=ifcopenshell.geom.settings()
        self.settings.set(self.settings.USE_PYTHON_OPENCASCADE, True)

    
    def DisplayIFC(self):
        display, start_display, add_menu, add_function_to_menu = init_display()
        #occ_display = ifcopenshell.geom.utils.initialize_display()
        products = self.ifc_file.by_type("IfcProduct")
        
        for product in products:
            if product.is_a("IfcOpeningElement"): continue
            r,g,b,o = GetTextureFromIfcProduct(product,MODE="")
            if product.Representation:
                color = Quantity_Color(r, g, b, Quantity_TOC_RGB)
                shape = ifcopenshell.geom.create_shape(self.settings, product).geometry
                
                display.DisplayShape(shape,color =color,transparency=1-o, update=False) #Need to get color and transparency from shape
                
                """
                ifcopenshell.geom.utils.set_shape_transparency(display_shape, 0.8)
                
                if product.is_a("IfcWindow"):
                    # Plates are the transparent parts of the window assembly
                    # in the IfcOpenHouse model
                    ifcopenshell.geom.utils.set_shape_transparency(display_shape, 0.8)
                """       
        start_display()


def New_IFC_Object(FILENAME,CREATOR,ORGANISATION_NAME,APPLICATION,APPLICATION_VERSION,PROYECT_NAME):
    """
    CONSTRUCTOR FUCTIONS
    """
    timestamp = time()
    timestring = strftime("%Y-%m-%dT%H:%M:%S", gmtime(timestamp))
    project_globalid = ifcopenshell.guid.compress(uuid.uuid1().hex)
    
    template = ("""ISO-10303-21;
                HEADER;
                FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');
                FILE_NAME('%(FILENAME)s','%(timestring)s',('%(CREATOR)s'),('%(ORGANISATION_NAME)s'),'%(APPLICATION)s','%(APPLICATION)s','');
                FILE_SCHEMA(('IFC2X3'));
                ENDSEC;
                DATA;
                #1=IFCPERSON($,$,'%(CREATOR)s',$,$,$,$,$);
                #2=IFCORGANIZATION($,'%(ORGANISATION_NAME)s',$,$,$);
                #3=IFCPERSONANDORGANIZATION(#1,#2,$);
                #4=IFCAPPLICATION(#2,'%(APPLICATION_VERSION)s','%(APPLICATION)s','');
                #5=IFCOWNERHISTORY(#3,#4,$,.ADDED.,$,#3,#4,%(timestamp)s);
                #6=IFCDIRECTION((1.,0.,0.));
                #7=IFCDIRECTION((0.,0.,1.));
                #8=IFCCARTESIANPOINT((0.,0.,0.));
                #9=IFCAXIS2PLACEMENT3D(#8,#7,#6);
                #10=IFCDIRECTION((0.,1.,0.));
                #11=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#9,#10);
                #12=IFCDIMENSIONALEXPONENTS(0,0,0,0,0,0,0);
                #13=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);
                #14=IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);
                #15=IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.);
                #16=IFCSIUNIT(*,.PLANEANGLEUNIT.,$,.RADIAN.);
                #17=IFCMEASUREWITHUNIT(IFCPLANEANGLEMEASURE(0.017453292519943295),#16);
                #18=IFCCONVERSIONBASEDUNIT(#12,.PLANEANGLEUNIT.,'DEGREE',#17);
                #19=IFCUNITASSIGNMENT((#13,#14,#15,#18));
                #20=IFCPROJECT('%(project_globalid)s',#5,'%(PROYECT_NAME)s',$,$,$,$,(#11),#19);
                ENDSEC;
                END-ISO-10303-21;
                """ % locals()).encode()

    # Write the template to a temporary file 
    temp_handle, temp_filename = tempfile.mkstemp(suffix=".ifc")
    with open(temp_filename, "wb") as f:
        f.write(template)
    
    ifc_file=ifcopenshell.open(temp_filename)

    return ifc_file


# ===============  OCC TOOLS  ===============
class OCC_API(TopologyExplorer):
    def __init__(self, OCC_OBJECT):
       TopologyExplorer.__init__(self,OCC_OBJECT)

       self.shape=OCC_OBJECT

    def GetSurfaceFromShape(self,SHAPE=None):
        if SHAPE==None:
            SHAPE = self.shape
        surface_props = GProp_GProps()
        brepgprop_SurfaceProperties(SHAPE, surface_props)
        surface=surface_props.Mass()
        return surface

    def GetVolumenFromShape(self,SHAPE=None):
        if SHAPE==None:
            SHAPE = self.shape
        volume_props = GProp_GProps()
        brepgprop_VolumeProperties(self.shape, volume_props)
        volume=volume_props.Mass()
        if volume < 0:
            volume = - volume
        return volume

    def getAll_TopoDS_Wire_list(self):
        Topods_wire_list=[]
        wires=self.wires()
        for wire in wires:
            wire_instance = topods_Wire(wire)
            Topods_wire_list.append(wire_instance)
        return Topods_wire_list

    def GetMaxDistanceFromShape(self):
        distance=0
        edges=self.edges()
        for edge in edges:
            vertices=self.vertices_from_edge(edge)
            point_list=[]
            for vertex in vertices:
                vertex_1=topods_Vertex(vertex)
                point_instance=BRep_Tool.Pnt(vertex_1)
                point=[point_instance.X(),point_instance.Y(),point_instance.Z()]
                point_list.append(point)
            [P1,P2]=point_list
            dist=sqrt((P1[0]-P2[0])**2+(P1[1]-P2[1])**2+(P1[2]-P2[2])**2)
            if dist > distance:
                distance=dist
        return distance 

    def GetMaxAreaOfFacesFromShape(self):
        area=0
        faces=self.faces()
        for face in faces:
            surface=self.GetSurfaceFromShape(SHAPE=face)
            if surface > area:
                area = surface
        return area

    """
    def GetBoxFromShape(self):
        box=get_boundingbox(self.shape)
        return box

    """

if __name__ == '__main__':
    pass