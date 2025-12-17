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


# =========================
# 坐标归零
# =========================
class YSM_OT_zero_location(bpy.types.Operator):
    bl_idname = "ysm.zero_location"
    bl_label = "坐标归零"
    bl_options = {"UNDO"}

    axis: EnumProperty(
        name="Axis",
        items=[
            ("ALL", "整体", ""),
            ("X", "X", ""),
            ("Y", "Y", ""),
            ("Z", "Z", ""),
        ],
        default="ALL",
    )

    def execute(self, context):
        objs = _selected_mesh_objects(context)
        if not objs:
            self.report({"ERROR"}, "No mesh selected")
            return {"CANCELLED"}

        for obj in objs:
            loc = obj.location.copy()
            if self.axis == "ALL":
                obj.location = Vector((0.0, 0.0, 0.0))
            elif self.axis == "X":
                obj.location = Vector((0.0, loc.y, loc.z))
            elif self.axis == "Y":
                obj.location = Vector((loc.x, 0.0, loc.z))
            elif self.axis == "Z":
                obj.location = Vector((loc.x, loc.y, 0.0))

        return {"FINISHED"}


# =========================
# 排列物体
# =========================
class YSM_OT_arrange_objects(bpy.types.Operator):
    bl_idname = "ysm.arrange_objects"
    bl_label = "排列物体"
    bl_options = {"UNDO"}

    def execute(self, context):
        objs = _selected_mesh_objects(context)
        if not objs:
            self.report({"ERROR"}, "No mesh selected")
            return {"CANCELLED"}

        # 防御式读取（属性不存在也不会炸）
        spacing = getattr(context.scene, "ysm_arrange_spacing", 10.0)
        spacing = abs(spacing)

        max_per_row = 10
        base = objs[0].location.copy()

        for i, obj in enumerate(objs):
            row = i // max_per_row
            col = i % max_per_row

            # 正方向：X-
            x = base.x - col * spacing
            # 换行：Y-
            y = base.y - row * spacing
            # Z 不变
            z = obj.location.z

            obj.location = Vector((x, y, z))

        return {"FINISHED"}


# =========================
# register / unregister
# =========================
def register():
    for cls in (YSM_OT_zero_location, YSM_OT_arrange_objects):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
        bpy.utils.register_class(cls)


def unregister():
    for cls in (YSM_OT_arrange_objects, YSM_OT_zero_location):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
