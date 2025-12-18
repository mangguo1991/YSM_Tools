import bpy
from bpy.props import EnumProperty
from mathutils import Vector


def _selected_mesh_objects(context):
    if context.mode != "OBJECT":
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except RuntimeError:
            pass
    return [o for o in context.selected_objects if o.type == "MESH"]


_AXIS_MAP = {
    "X+": Vector((1.0, 0.0, 0.0)),
    "X-": Vector((-1.0, 0.0, 0.0)),
    "Y+": Vector((0.0, 1.0, 0.0)),
    "Y-": Vector((0.0, -1.0, 0.0)),
    "Z+": Vector((0.0, 0.0, 1.0)),
    "Z-": Vector((0.0, 0.0, -1.0)),
}


def _basis_from_axes(front_axis: str, up_axis: str):
    f = _AXIS_MAP.get(front_axis, Vector((1, 0, 0))).normalized()
    u = _AXIS_MAP.get(up_axis, Vector((0, 0, 1))).normalized()

    # ✅ 修复左右：Right = Up × Front
    r = u.cross(f)
    if r.length < 1e-8:
        return None, None, None
    r.normalize()

    # 重新正交 up，保证一套干净基向量
    u = f.cross(r)
    if u.length < 1e-8:
        return None, None, None
    u.normalize()

    return f, r, u  # FRONT, RIGHT, UP


def _bbox_proj_ranges(obj, f: Vector, r: Vector, u: Vector):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]

    df = [p.dot(f) for p in pts]
    dr = [p.dot(r) for p in pts]
    du = [p.dot(u) for p in pts]

    min_f, max_f = min(df), max(df)
    min_r, max_r = min(dr), max(dr)
    min_u, max_u = min(du), max(du)

    mid_f = (min_f + max_f) * 0.5
    mid_r = (min_r + max_r) * 0.5
    mid_u = (min_u + max_u) * 0.5

    return (min_f, max_f, mid_f, min_r, max_r, mid_r, min_u, max_u, mid_u)


def _set_origin_world(context, obj, world_point: Vector):
    scene = context.scene
    view_layer = context.view_layer

    cursor_old = scene.cursor.location.copy()
    active_old = view_layer.objects.active

    for o in view_layer.objects:
        o.select_set(False)
    obj.select_set(True)
    view_layer.objects.active = obj

    scene.cursor.location = world_point
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")

    scene.cursor.location = cursor_old
    if active_old:
        view_layer.objects.active = active_old


_AXIS_ITEMS = [
    ("X+", "X+", ""),
    ("X-", "X-", ""),
    ("Y+", "Y+", ""),
    ("Y-", "Y-", ""),
    ("Z+", "Z+", ""),
    ("Z-", "Z-", ""),
]


class YSM_OT_origin_offset(bpy.types.Operator):
    bl_idname = "ysm.origin_offset"
    bl_label = "原点偏移"
    bl_options = {"UNDO"}

    front_axis: EnumProperty(name="前向", items=_AXIS_ITEMS, default="X+")
    up_axis: EnumProperty(name="上向", items=_AXIS_ITEMS, default="Z+")

    direction: EnumProperty(
        items=[
            ("CENTER", "", ""),
            ("UP", "", ""),
            ("DOWN", "", ""),
            ("LEFT", "", ""),
            ("RIGHT", "", ""),
            ("FRONT", "", ""),
            ("BACK", "", ""),
            ("UL", "", ""),
            ("UR", "", ""),
            ("DL", "", ""),
            ("DR", "", ""),
        ],
        default="CENTER",
    )

    offset_mode: EnumProperty(
        items=[("FULL", "整体", ""), ("SINGLE", "单轴", "")],
        default="FULL",
    )

    def execute(self, context):
        objs = _selected_mesh_objects(context)
        if not objs:
            self.report({"ERROR"}, "No mesh selected")
            return {"CANCELLED"}

        f, r, u = _basis_from_axes(self.front_axis, self.up_axis)
        if f is None:
            self.report({"ERROR"}, "front 和 up 不能共线")
            return {"CANCELLED"}

        for obj in objs:
            min_f, max_f, mid_f, min_r, max_r, mid_r, min_u, max_u, mid_u = _bbox_proj_ranges(obj, f, r, u)

            origin = obj.matrix_world.translation
            of = origin.dot(f)
            orr = origin.dot(r)
            ou = origin.dot(u)

            if self.offset_mode == "FULL":
                sf, sr, su = mid_f, mid_r, mid_u

                if self.direction == "CENTER":
                    sf, sr, su = mid_f, mid_r, mid_u

                elif self.direction == "FRONT":
                    sf, sr, su = max_f, mid_r, mid_u
                elif self.direction == "BACK":
                    sf, sr, su = min_f, mid_r, mid_u

                elif self.direction == "LEFT":
                    sf, sr, su = mid_f, min_r, mid_u
                elif self.direction == "RIGHT":
                    sf, sr, su = mid_f, max_r, mid_u

                elif self.direction == "UP":
                    sf, sr, su = mid_f, mid_r, max_u
                elif self.direction == "DOWN":
                    sf, sr, su = mid_f, mid_r, min_u

                # 角点：只动 R/U，F 固定中心
                elif self.direction == "UL":
                    sf, sr, su = mid_f, min_r, max_u
                elif self.direction == "UR":
                    sf, sr, su = mid_f, max_r, max_u
                elif self.direction == "DL":
                    sf, sr, su = mid_f, min_r, min_u
                elif self.direction == "DR":
                    sf, sr, su = mid_f, max_r, min_u

            else:
                # SINGLE：默认保持原值（F不动，除非点前/后）
                sf, sr, su = of, orr, ou

                if self.direction == "CENTER":
                    sf, sr, su = mid_f, mid_r, mid_u

                elif self.direction == "FRONT":
                    sf = max_f
                elif self.direction == "BACK":
                    sf = min_f

                elif self.direction == "LEFT":
                    sr = min_r
                elif self.direction == "RIGHT":
                    sr = max_r

                elif self.direction == "UP":
                    su = max_u
                elif self.direction == "DOWN":
                    su = min_u

                # 角点：只改 R/U，F 保持原先 sf=of
                elif self.direction == "UL":
                    sr, su = min_r, max_u
                elif self.direction == "UR":
                    sr, su = max_r, max_u
                elif self.direction == "DL":
                    sr, su = min_r, min_u
                elif self.direction == "DR":
                    sr, su = max_r, min_u

            target_world = f * sf + r * sr + u * su
            _set_origin_world(context, obj, target_world)

        return {"FINISHED"}


def register():
    try:
        bpy.utils.unregister_class(YSM_OT_origin_offset)
    except Exception:
        pass
    bpy.utils.register_class(YSM_OT_origin_offset)


def unregister():
    try:
        bpy.utils.unregister_class(YSM_OT_origin_offset)
    except Exception:
        pass
