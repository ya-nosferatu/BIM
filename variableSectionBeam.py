import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Utility as AllplanUtil
import GeometryValidate as GeometryValidate
from HandleDirection import HandleDirection
from HandleProperties import HandleProperties


def check_allplan_version(build_ele, version):
    del build_ele
    del version
    return True


def create_element(build_ele, doc):
    element = Beam(doc)
    return element.create(build_ele)


class Beam:
    def __init__(self, doc):
        self.model_ele_list = []
        self.handle_list = []
        self.document = doc

    def create(self, build_ele):
        self.connect_all_parts(build_ele)
        self.create_lower_part_beam(build_ele)
        return (self.model_ele_list, self.handle_list)

    def connect_all_parts(self, build_ele):
        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        com_prop.Pen = 1
        com_prop.Color = 3
        com_prop.Stroke = 1
        polyhedron_bottom = self.create_lower_part_beam(build_ele)
        polyhedron_center = self.create_central_part_beam(build_ele)
        polyhedron_top = self.create_upper_part_beam(build_ele)
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron_bottom, polyhedron_center)
        if err:
            return
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, polyhedron_top)
        if err:
            return 
        self.model_ele_list.append(
            AllplanBasisElements.ModelElement3D(com_prop, polyhedron))

    def create_lower_part_beam(self, build_ele):
        polyhedron = self.lower_part_dependance_1(build_ele)
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_dependance_2(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_dependance_3(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_dependance_4(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_dependance_2_2(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_dependance_3_2(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_dependance_4_2(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_dependance_2_3(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_dependance_3_3(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_dependance_2_4(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_dependance_3_4(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.last_lower_part(build_ele))
        return polyhedron

    def create_central_part_beam(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(0, build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + build_ele.LengthTransition.value, 
                                        build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, 
                                        build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - (build_ele.LengthThicker_central.value + build_ele.LengthTransition.value), 
                                        build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, 
                                        build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value,
                                         build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, 
                                         build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - build_ele.LengthTransition.value,
                                        build_ele.ChamferLength_low.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, 
                                        build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + build_ele.LengthTransition.value,
                                        build_ele.ChamferLength_low.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, 
                                        build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value,
                                        build_ele.ChamferLength_low.value, 
                                        build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.ChamferLength_low.value, build_ele.Height_low.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        path += AllplanGeo.Point3D(0, build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        if err:
            return []

        return polyhedron

    def create_upper_part_beam(self, build_ele):
        polyhedron = self.upper_part_dependance_1(build_ele)
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.upper_part_dependance_3(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.upper_part_dependance_2(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.upper_part_dependance_3(build_ele, plus=(build_ele.Length.value - build_ele.LengthThicker_central.value)))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.upper_part_dependance_4(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.upper_part_dependance_2_2(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.upper_part_dependance_4(build_ele, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2, build_ele.Width_up.value, 10))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.upper_part_dependance_2_3(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.upper_part_dependance_4_2(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.upper_part_dependance_4_2(build_ele, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2, build_ele.Width_up.value, 10))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.upper_part_dependance_3_3(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.last_upper_part(build_ele))
        return polyhedron

    def upper_part_dependance_1(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, 
                                        build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2,
                                        build_ele.Height_low.value + build_ele.Height_central.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, 
                                        build_ele.Width_up.value - (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2,
                                        build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, 
                                        -(build_ele.Width_up.value - build_ele.WidthBottom.value) / 2,
                                        build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, 
                                        build_ele.ChamferLength_low.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2,
                                        build_ele.Height_low.value + build_ele.Height_central.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, 
                                        build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2,
                                        build_ele.Height_low.value + build_ele.Height_central.value)
        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, 
                                        build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2,
                                        build_ele.Height_low.value + build_ele.Height_central.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, 
                                        build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2,
                                        build_ele.Height_low.value + build_ele.Height_central.value)
        
        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        if err:
            return []

        return polyhedron

    def upper_part_dependance_2(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - build_ele.LengthTransition.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2 , build_ele.Height_low.value + build_ele.Height_central.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - build_ele.LengthTransition.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2 , build_ele.WidthBottom.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2 + (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.WidthBottom.value + (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value + 10, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - 10, build_ele.Height_low.value + build_ele.Height_central.value + 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def upper_part_dependance_3(self, build_ele, plus=0):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(plus, build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)
        base_pol += AllplanGeo.Point3D(plus, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)
        base_pol += AllplanGeo.Point3D(plus, build_ele.WidthBottom.value + (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(plus, -(build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(plus, build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(plus, build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)
        path += AllplanGeo.Point3D(plus + build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def upper_part_dependance_4(self, build_ele, minus_1 = 0, minus_2 = 0, digit = -10):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - minus_1, build_ele.Height_low.value + build_ele.Height_central.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.Width_up.value - (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2 - minus_2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.WidthBottom.value + (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2 - minus_2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - minus_1, build_ele.Height_low.value + build_ele.Height_central.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - minus_1, build_ele.Height_low.value + build_ele.Height_central.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value + digit - minus_1, build_ele.Height_low.value + build_ele.Height_central.value)
        print(base_pol)
        print(path)
        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def upper_part_dependance_2_2(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - build_ele.LengthTransition.value, build_ele.ChamferLength_low.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - build_ele.LengthTransition.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2 - (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, -(build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value + 10, build_ele.ChamferLength_low.value + 10, build_ele.Height_low.value + build_ele.Height_central.value + 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def upper_part_dependance_2_3(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + build_ele.LengthTransition.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + build_ele.LengthTransition.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.WidthBottom.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2 + (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.WidthBottom.value + (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value - 10, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - 10, build_ele.Height_low.value + build_ele.Height_central.value - 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def upper_part_dependance_4_2(self, build_ele, minus_1 = 0, minus_2 = 0, digit = -10):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - minus_1, build_ele.Height_low.value + build_ele.Height_central.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value + (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2 - minus_2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.WidthBottom.value + (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2 - minus_2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - minus_1, build_ele.Height_low.value + build_ele.Height_central.value)
        
        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - minus_1, build_ele.Height_low.value + build_ele.Height_central.value)
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - minus_1 + digit, build_ele.Height_low.value + build_ele.Height_central.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        if err:
            return []

        return polyhedron

    def upper_part_dependance_3_3(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + build_ele.LengthTransition.value, build_ele.ChamferLength_low.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + build_ele.LengthTransition.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2 - (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, -(build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value + build_ele.Height_central.value)
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value - 10, build_ele.ChamferLength_low.value + 10, build_ele.Height_low.value + build_ele.Height_central.value - 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def last_upper_part(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(0, -(build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.Width_up.value - (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.Width_up.value - (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.Height_up.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.Width_up.value - (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2 - build_ele.PlateSpace.value, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.Height_up.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.Width_up.value - (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2 - build_ele.PlateSpace.value, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.Height_up.value + build_ele.PlateHeight.value)
        base_pol += AllplanGeo.Point3D(0, - (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2 + build_ele.PlateSpace.value, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.Height_up.value + build_ele.PlateHeight.value)
        base_pol += AllplanGeo.Point3D(0, - (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2 + build_ele.PlateSpace.value, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.Height_up.value)
        base_pol += AllplanGeo.Point3D(0, - (build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.Height_up.value)
        base_pol += AllplanGeo.Point3D(0, -(build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, -(build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        path += AllplanGeo.Point3D(build_ele.Length.value, -(build_ele.Width_up.value - build_ele.WidthBottom.value) / 2, build_ele.Height_low.value + build_ele.Height_central.value + build_ele.ChamferHeight_up.value)
        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_dependance_1(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, 
                                    build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2,
                                    build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, 
                                    build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2 - build_ele.WidthThinner_central.value,
                                    build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, 0, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        if err:
            return []

        return polyhedron

    def lower_part_dependance_2(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + build_ele.LengthTransition.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + build_ele.LengthTransition.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.WidthBottom.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value - 10 , build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - 10, build_ele.Height_low.value - 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_dependance_3(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(0, 0, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_dependance_4(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        
        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - 10, build_ele.Height_low.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        if err:
            return []

        return polyhedron

    def lower_part_dependance_2_2(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + build_ele.LengthTransition.value, build_ele.ChamferLength_low.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + build_ele.LengthTransition.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, 0, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value,build_ele.ChamferLength_low.value, build_ele.Height_low.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value,build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value - 10 ,build_ele.ChamferLength_low.value + 10, build_ele.Height_low.value - 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_dependance_3_2(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, 0, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        path += AllplanGeo.Point3D(build_ele.Length.value, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_dependance_4_2(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, 0, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, 0, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        
        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        path += AllplanGeo.Point3D(build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value + 10, build_ele.Height_low.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        if err:
            return []

        return polyhedron

    def lower_part_dependance_2_3(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - build_ele.LengthTransition.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - build_ele.LengthTransition.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.WidthBottom.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value + 10, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - 10, build_ele.Height_low.value + 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_dependance_3_3(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.WidthBottom.value - build_ele.ChamferLength_low.value - 10, build_ele.Height_low.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_dependance_2_4(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - build_ele.LengthTransition.value, build_ele.ChamferLength_low.value + (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - build_ele.LengthTransition.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, 0, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - 10, build_ele.ChamferLength_low.value + 10, build_ele.Height_low.value - 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_dependance_3_4(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, 0, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value - (build_ele.WidthBottom.value - build_ele.ChamferLength_low.value * 2 - build_ele.WidthThinner_central.value) / 2, 0, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value, build_ele.Height_low.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthThicker_central.value, build_ele.ChamferLength_low.value + 10, build_ele.Height_low.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def last_lower_part(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(0, 60, 0)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthBottom.value - 60, 0)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthBottom.value, 60)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthBottom.value, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(0, 0, build_ele.Height_low.value - build_ele.ChamferHeight_low.value)
        base_pol += AllplanGeo.Point3D(0, 0, 60)
        base_pol += AllplanGeo.Point3D(0, 60, 0)

        if not GeometryValidate.is_valid(base_pol):
            return

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, 60, 0)
        path += AllplanGeo.Point3D(build_ele.Length.value,60,0)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

