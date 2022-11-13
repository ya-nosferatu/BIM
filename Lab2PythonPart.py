import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Utility as AllplanUtil
import GeometryValidate as GeometryValidate
from HandleDirection import HandleDirection
from HandleProperties import HandleProperties


print('Load Chamfer.py')


def check_allplan_version(build_ele, version):
    del build_ele
    del version
    return True


def create_element(build_ele, doc):
    element = Chamfer(doc)
    return element.create(build_ele)


def move_handle(build_ele, handle_prop, input_pnt, doc):
    build_ele.change_property(handle_prop, input_pnt)
    return create_element(build_ele, doc)


class Chamfer:

    def __init__(self, doc):
        self.model_ele_list = []
        self.handle_list = []
        self.document = doc

    def create(self, build_ele):
        self.upper_part(build_ele)
        self.create_handles(build_ele)
        return (self.model_ele_list, self.handle_list)

    def lower_part(self, build_ele):
        brep = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0),
                                       AllplanGeo.Vector3D(1, 0, 0),
                                       AllplanGeo.Vector3D(0, 0, 1)),
            build_ele.Width_low.value,
            build_ele._Length.value,
            build_ele.Height_low.value)

        brep_inter = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0),
                                       AllplanGeo.Vector3D(1, 0, 0),
                                       AllplanGeo.Vector3D(0, 0, 1)),
            build_ele.Width_low.value,
            build_ele._Length.value,
            build_ele.Height_low.value)

        chamfer_width = build_ele.ChamferWidth_low.value
        chamfer_width_bottom = build_ele.ChamferWidthBottom_low.value

        if chamfer_width > 0:
            edges = AllplanUtil.VecSizeTList()
            edges.append(1)
            edges.append(3)

            err, brep = AllplanGeo.ChamferCalculus.Calculate(
                brep, edges, chamfer_width, False)

            if not GeometryValidate.polyhedron(err):
                return

        if chamfer_width_bottom > 0:
            edges2 = AllplanUtil.VecSizeTList()
            edges2.append(8)
            edges2.append(10)

            err, brep_inter = AllplanGeo.ChamferCalculus.Calculate(
                brep_inter, edges2, chamfer_width_bottom, False)

            if not GeometryValidate.polyhedron(err):
                return

        err, final_fragment = AllplanGeo.MakeIntersection(brep, brep_inter)

        return final_fragment

    def central_part(self, build_ele):
        brep = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(build_ele.Width_low.value / 2 - build_ele.CentralWidth.value / 2, 0, build_ele.Height_low.value),
                                       AllplanGeo.Vector3D(1, 0, 0),
                                       AllplanGeo.Vector3D(0, 0, 1)),
            build_ele.CentralWidth.value,
            build_ele._Length.value,
            build_ele.CentralHeight.value)

        cone = AllplanGeo.BRep3D.CreateCylinder(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(build_ele.ChamferWidth_low.value - build_ele.CentralWidth.value/2, 450, build_ele.Height_low.value + build_ele.CentralHeight.value / 2),
                                       AllplanGeo.Vector3D(0, 0, 1),
                                       AllplanGeo.Vector3D(1, 0, 0)),
            build_ele.Radius.value , build_ele.CentralWidth.value * build_ele.ChamferWidth_low.value)

        cone1 = AllplanGeo.BRep3D.CreateCylinder(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(build_ele.ChamferWidth_low.value - build_ele.CentralWidth.value/2, build_ele._Length.value - 450, build_ele.Height_low.value + build_ele.CentralHeight.value / 2),
                                       AllplanGeo.Vector3D(0, 0, 1),
                                       AllplanGeo.Vector3D(1, 0, 0)),
            build_ele.Radius.value , build_ele.CentralWidth.value * build_ele.ChamferWidth_low.value)


        err, brep = AllplanGeo.MakeSubtraction(brep, cone)
        err, brep = AllplanGeo.MakeSubtraction(brep, cone1)

        err, final_fragment = AllplanGeo.MakeUnion(
            brep, self.lower_part(build_ele))
        return final_fragment

    def upper_part(self, build_ele):
        brep = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0 - (build_ele.Width_up.value - build_ele.Width_low.value) / 2, 0, build_ele.Height_low.value + build_ele.CentralHeight.value),
                                       AllplanGeo.Vector3D(1, 0, 0),
                                       AllplanGeo.Vector3D(0, 0, 1)),
            build_ele.Width_up.value,
            build_ele._Length.value,
            build_ele.Height_up.value)

        brep_plate = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(build_ele.PlateSpace.value - (build_ele.Width_up.value - build_ele.Width_low.value) / 2, 0, build_ele.Height_low.value + build_ele.CentralHeight.value + build_ele.Height_up.value),
                                       AllplanGeo.Vector3D(1, 0, 0),
                                       AllplanGeo.Vector3D(0, 0, 1)),
            build_ele.Width_up.value - build_ele.PlateSpace.value*2,
            build_ele._Length.value,
            build_ele.PlateHeight.value)

        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        com_prop.Pen = 1
        com_prop.Color = build_ele.MainColor.value

        chamfer_width_top = build_ele.ChamferWidth_up.value

        if chamfer_width_top > 0:
            edges2 = AllplanUtil.VecSizeTList()
            edges2.append(8)
            edges2.append(10)

            err, brep = AllplanGeo.ChamferCalculus.Calculate(
                brep, edges2, chamfer_width_top, False)

            if not GeometryValidate.polyhedron(err):
                return

        err, final_fragment = AllplanGeo.MakeUnion(
            brep, self.central_part(build_ele))
        err, final_fragment = AllplanGeo.MakeUnion(final_fragment, brep_plate)
        self.model_ele_list.append(
            AllplanBasisElements.ModelElement3D(com_prop, final_fragment))

    def create_handles(self, build_ele):
        origin = AllplanGeo.Point3D(
            build_ele.Width_low.value / 2, build_ele._Length.value, build_ele.CentralHeight.value + build_ele.Height_low.value)
        origin2 = AllplanGeo.Point3D(
            build_ele.Width_low.value / 2, 0, build_ele.Height_low.value / 2)
        origin3 = AllplanGeo.Point3D(
            0, build_ele._Length.value, (build_ele.Height_low.value - build_ele.ChamferWidth_low.value) / 2)
        origin4 = AllplanGeo.Point3D(
            0 - (build_ele.Width_up.value - build_ele.Width_low.value) / 2, build_ele._Length.value, build_ele.CentralHeight.value + build_ele.Height_low.value + build_ele.ChamferWidth_up.value)
        origin5 = AllplanGeo.Point3D(
            build_ele.Width_low.value / 2, build_ele._Length.value, build_ele.CentralHeight.value + build_ele.Height_low.value - build_ele.Height_low.value / 4)
        origin6 = AllplanGeo.Point3D(
            build_ele.Width_low.value / 2, build_ele._Length.value, build_ele.CentralHeight.value + build_ele.Height_low.value + build_ele.Height_up.value)
        origin7 = AllplanGeo.Point3D(
            build_ele.Width_low.value / 2, build_ele._Length.value, 0)
        origin8 = AllplanGeo.Point3D(
            build_ele.Width_low.value / 2 - build_ele.CentralWidth.value / 2, build_ele._Length.value, build_ele.CentralHeight.value / 2 + build_ele.Height_low.value)

        self.handle_list.append(
            HandleProperties("CentralHeight",
                             AllplanGeo.Point3D(origin.X,
                                                origin.Y,
                                                origin.Z),
                             AllplanGeo.Point3D(origin.X,
                                                origin.Y,
                                                origin.Z - build_ele.CentralHeight.value),
                             [("CentralHeight", HandleDirection.z_dir)],
                             HandleDirection.z_dir,
                             False))

        self.handle_list.append(
            HandleProperties("_Length",
                             AllplanGeo.Point3D(origin2.X,
                                                origin2.Y + build_ele._Length.value,
                                                origin2.Z),
                             AllplanGeo.Point3D(origin2.X,
                                                origin2.Y,
                                                origin2.Z),
                             [("_Length", HandleDirection.y_dir)],
                             HandleDirection.y_dir,
                             False))

        self.handle_list.append(
            HandleProperties("Width_low", AllplanGeo.Point3D(origin3.X + build_ele.Width_low.value, origin3.Y, origin3.Z),
                             AllplanGeo.Point3D(
                                 origin3.X, origin3.Y, origin3.Z),
                             [("Width_low", HandleDirection.x_dir)],
                             HandleDirection.x_dir,
                             False))

        self.handle_list.append(
            HandleProperties("Width_up",
                             AllplanGeo.Point3D(origin4.X + build_ele.Width_up.value,
                                                origin4.Y,
                                                origin4.Z),
                             AllplanGeo.Point3D(origin4.X,
                                                origin4.Y,
                                                origin4.Z),
                             [("Width_up", HandleDirection.x_dir)],
                             HandleDirection.x_dir,
                             False))

        self.handle_list.append(
            HandleProperties("Height_up",
                             AllplanGeo.Point3D(origin5.X,
                                                origin5.Y,
                                                origin5.Z + build_ele.Height_up.value),
                             AllplanGeo.Point3D(origin5.X,
                                                origin5.Y,
                                                origin5.Z),
                             [("Height_up", HandleDirection.z_dir)],
                             HandleDirection.z_dir,
                             False))

        self.handle_list.append(
            HandleProperties("PlateHeight",
                             AllplanGeo.Point3D(origin6.X,
                                                origin6.Y,
                                                origin6.Z + build_ele.PlateHeight.value),
                             AllplanGeo.Point3D(origin6.X,
                                                origin6.Y,
                                                origin6.Z),
                             [("PlateHeight", HandleDirection.z_dir)],
                             HandleDirection.z_dir,
                             False))

        self.handle_list.append(
            HandleProperties("Height_low",
                             AllplanGeo.Point3D(origin7.X,
                                                origin7.Y,
                                                origin7.Z + build_ele.Height_low.value),
                             AllplanGeo.Point3D(origin7.X,
                                                origin7.Y,
                                                origin7.Z),
                             [("Height_low", HandleDirection.z_dir)],
                             HandleDirection.z_dir,
                             False))

        self.handle_list.append(
            HandleProperties("CentralWidth",
                             AllplanGeo.Point3D(origin8.X + build_ele.CentralWidth.value,
                                                origin8.Y,
                                                origin8.Z),
                             AllplanGeo.Point3D(origin8.X,
                                                origin8.Y,
                                                origin8.Z),
                             [("CentralWidth", HandleDirection.x_dir)],
                             HandleDirection.x_dir,
                             False))