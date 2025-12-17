import bpy
from bpy.props import EnumProperty, FloatProperty


class YSM_PT_tools(bpy.types.Panel):
    bl_label = "YSM Blender Tools"
    bl_idname = "YSM_PT_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "YSM"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # -----------------
        # Dev
        # -----------------
        box = layout.box()
        box.label(text="Dev")
        box.operator("ysm.dev_reload", text="Reload")

        # -----------------
        # 原点偏移
        # -----------------
        box = layout.box()
        box.label(text="原点偏移")

        row = box.row(align=True)
        row.prop(scene, "ysm_origin_mode", expand=True)
        mode = scene.ysm_origin_mode

        row = box.row(align=True)
        op = row.operator("ysm.origin_offset", text="中心 (C)")
        op.direction = "CENTER"
        op.offset_mode = mode

        row = box.row(align=True)
        op = row.operator("ysm.origin_offset", text="上 (Z+)")
        op.direction = "Z_PLUS"
        op.offset_mode = mode
        op = row.operator("ysm.origin_offset", text="下 (Z-)")
        op.direction = "Z_MINUS"
        op.offset_mode = mode

        row = box.row(align=True)
        op = row.operator("ysm.origin_offset", text="前 (X-)")
        op.direction = "X_MINUS"
        op.offset_mode = mode
        op = row.operator("ysm.origin_offset", text="后 (X+)")
        op.direction = "X_PLUS"
        op.offset_mode = mode

        row = box.row(align=True)
        op = row.operator("ysm.origin_offset", text="左 (Y-)")
        op.direction = "Y_MINUS"
        op.offset_mode = mode
        op = row.operator("ysm.origin_offset", text="右 (Y+)")
        op.direction = "Y_PLUS"
        op.offset_mode = mode

        # -----------------
        # 坐标归零
        # -----------------
        box = layout.box()
        box.label(text="坐标归零")

        row = box.row(align=True)
        row.operator("ysm.zero_location", text="整体").axis = "ALL"

        row = box.row(align=True)
        row.operator("ysm.zero_location", text="X").axis = "X"
        row.operator("ysm.zero_location", text="Y").axis = "Y"
        row.operator("ysm.zero_location", text="Z").axis = "Z"

        # -----------------
        # 排列物体
        # -----------------
        box = layout.box()
        box.label(text="排列物体")

        row = box.row(align=True)
        row.prop(scene, "ysm_arrange_spacing", text="间距")
        row.operator("ysm.arrange_objects", text="排列")


# =========================
# register / unregister
# =========================
def register():
    try:
        bpy.utils.unregister_class(YSM_PT_tools)
    except Exception:
        pass
    bpy.utils.register_class(YSM_PT_tools)

    # 确保 Scene 属性存在（避免 Reload / 新开文件时报错）
    if not hasattr(bpy.types.Scene, "ysm_origin_mode"):
        bpy.types.Scene.ysm_origin_mode = EnumProperty(
            name="模式",
            items=[("FULL", "整体", ""), ("SINGLE", "单轴", "")],
            default="FULL",
        )

    if not hasattr(bpy.types.Scene, "ysm_arrange_spacing"):
        bpy.types.Scene.ysm_arrange_spacing = FloatProperty(
            name="间距",
            default=10.0,
            min=0.0,
        )


def unregister():
    for p in ("ysm_origin_mode", "ysm_arrange_spacing"):
        if hasattr(bpy.types.Scene, p):
            try:
                delattr(bpy.types.Scene, p)
            except Exception:
                pass

    try:
        bpy.utils.unregister_class(YSM_PT_tools)
    except Exception:
        pass
