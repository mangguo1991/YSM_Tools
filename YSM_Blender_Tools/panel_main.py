import bpy
from bpy.props import EnumProperty, FloatProperty


_AXIS_ITEMS = [
    ("X+", "X+", ""),
    ("X-", "X-", ""),
    ("Y+", "Y+", ""),
    ("Y-", "Y-", ""),
    ("Z+", "Z+", ""),
    ("Z-", "Z-", ""),
]


class YSM_PT_tools(bpy.types.Panel):
    bl_label = "YSM Blender Tools"
    bl_idname = "YSM_PT_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "YSM"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Dev
        box = layout.box()
        box.label(text="Dev")
        box.operator("ysm.dev_reload", text="Reload")

        # 文件导入
        box = layout.box()
        box.label(text="文件导入")
        box.operator("ysm.file_import", text="导入文件")

        # 原点偏移
        box = layout.box()
        box.label(text="原点偏移")

        row = box.row(align=True)
        row.prop(scene, "ysm_origin_mode", expand=True)
        mode = scene.ysm_origin_mode

        # 前向 / 上向（同一排）
        row = box.row(align=True)
        row.prop(scene, "ysm_origin_front_axis", text="前")
        row.prop(scene, "ysm_origin_up_axis", text="上")

        def btn(r, label, direction):
            op = r.operator("ysm.origin_offset", text=label)
            op.direction = direction
            op.offset_mode = mode
            op.front_axis = scene.ysm_origin_front_axis
            op.up_axis = scene.ysm_origin_up_axis

        # 左上 / 上 / 右上（角点：只动 R/U，F 固定中心）
        row = box.row(align=True)
        btn(row, "↖", "UL")
        btn(row, "↑", "UP")
        btn(row, "↗", "UR")

        # 左 / 中 / 右
        row = box.row(align=True)
        btn(row, "←", "LEFT")
        btn(row, "•", "CENTER")
        btn(row, "→", "RIGHT")

        # 左下 / 下 / 右下
        row = box.row(align=True)
        btn(row, "↙", "DL")
        btn(row, "↓", "DOWN")
        btn(row, "↘", "DR")

        # 前 / 后（沿 front_axis）
        row = box.row(align=True)
        btn(row, "前", "FRONT")
        btn(row, "后", "BACK")

        # 坐标归零
        box = layout.box()
        box.label(text="坐标归零")

        row = box.row(align=True)
        row.operator("ysm.zero_location", text="整体").axis = "ALL"

        row = box.row(align=True)
        row.operator("ysm.zero_location", text="X").axis = "X"
        row.operator("ysm.zero_location", text="Y").axis = "Y"
        row.operator("ysm.zero_location", text="Z").axis = "Z"

        # 排列物体
        box = layout.box()
        box.label(text="排列物体")

        row = box.row(align=True)
        row.prop(scene, "ysm_arrange_spacing", text="间距")
        row.operator("ysm.arrange_objects", text="排列")


def register():
    try:
        bpy.utils.unregister_class(YSM_PT_tools)
    except Exception:
        pass
    bpy.utils.register_class(YSM_PT_tools)

    if not hasattr(bpy.types.Scene, "ysm_origin_mode"):
        bpy.types.Scene.ysm_origin_mode = EnumProperty(
            items=[("FULL", "整体", ""), ("SINGLE", "单轴", "")],
            default="FULL",
        )

    if not hasattr(bpy.types.Scene, "ysm_origin_front_axis"):
        bpy.types.Scene.ysm_origin_front_axis = EnumProperty(
            name="前向",
            items=_AXIS_ITEMS,
            default="X+",
        )

    if not hasattr(bpy.types.Scene, "ysm_origin_up_axis"):
        bpy.types.Scene.ysm_origin_up_axis = EnumProperty(
            name="上向",
            items=_AXIS_ITEMS,
            default="Z+",
        )

    if not hasattr(bpy.types.Scene, "ysm_arrange_spacing"):
        bpy.types.Scene.ysm_arrange_spacing = FloatProperty(
            name="间距",
            default=10.0,
            min=0.0,
        )


def unregister():
    for p in (
        "ysm_origin_mode",
        "ysm_origin_front_axis",
        "ysm_origin_up_axis",
        "ysm_arrange_spacing",
    ):
        if hasattr(bpy.types.Scene, p):
            try:
                delattr(bpy.types.Scene, p)
            except Exception:
                pass

    try:
        bpy.utils.unregister_class(YSM_PT_tools)
    except Exception:
        pass
