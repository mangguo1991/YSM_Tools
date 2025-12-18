import bpy
from bpy.props import EnumProperty


# =========================================================
# 坐标归零（Object Location）
# - 整体：XYZ 全归零
# - X/Y/Z：单轴归零
# =========================================================
class YSM_OT_zero_location(bpy.types.Operator):
    bl_idname = "ysm.zero_location"
    bl_label = "坐标归零"
    bl_options = {"REGISTER", "UNDO"}

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
        if context.mode != "OBJECT":
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError:
                pass

        objs = list(context.selected_objects)
        if not objs:
            return {"CANCELLED"}

        for obj in objs:
            if self.axis == "ALL":
                obj.location = (0.0, 0.0, 0.0)
            elif self.axis == "X":
                obj.location.x = 0.0
            elif self.axis == "Y":
                obj.location.y = 0.0
            elif self.axis == "Z":
                obj.location.z = 0.0

        return {"FINISHED"}


# =========================================================
# 排列物体（Object Location）
# - 每行最多10个，超过自动换行
# - 间距从 Scene.yms_arrange_spacing 读取（默认 10.0）
# - 正方向：X-（向左排）
# - 以 active 为起点；没有 active 用第一个选中
# - Z 不改
# =========================================================
class YSM_OT_arrange_objects(bpy.types.Operator):
    bl_idname = "ysm.arrange_objects"
    bl_label = "排列物体"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if context.mode != "OBJECT":
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError:
                pass

        objs = list(context.selected_objects)
        if not objs:
            return {"CANCELLED"}

        spacing = float(getattr(context.scene, "ysm_arrange_spacing", 10.0))
        per_row = 10

        anchor = context.view_layer.objects.active if context.view_layer.objects.active in objs else objs[0]
        start = anchor.location.copy()

        objs_sorted = sorted(objs, key=lambda o: o.name)

        for i, obj in enumerate(objs_sorted):
            col = i % per_row
            row = i // per_row

            obj.location.x = start.x - col * spacing   # X- 方向
            obj.location.y = start.y + row * spacing   # Y+ 换行
            # Z 保持不动

        return {"FINISHED"}


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
