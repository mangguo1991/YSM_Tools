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


def _world_bbox_stats(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)

    mid_x = (min_x + max_x) * 0.5
    mid_y = (min_y + max_y) * 0.5
    mid_z = (min_z + max_z) * 0.5

    return min_x, max_x, mid_x, min_y, max_y, mid_y, min_z, max_z, mid_z


def _set_origin_world(context, obj, world_point):
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


class YSM_OT_origin_offset(bpy.types.Operator):
    bl_idname = "ysm.origin_offset"
    bl_label = "原点偏移"
    bl_options = {"UNDO"}

    direction: EnumProperty(
        name="Direction",
        items=[
            ("CENTER", "中心 (C)", ""),
            ("Z_PLUS", "上 (Z+)", ""),
            ("Z_MINUS", "下 (Z-)", ""),
            ("X_MINUS", "前 (X-)", ""),
            ("X_PLUS", "后 (X+)", ""),
            ("Y_MINUS", "左 (Y-)", ""),
            ("Y_PLUS", "右 (Y+)", ""),
        ],
        default="CENTER",
    )

    offset_mode: EnumProperty(
        name="Mode",
        items=[
            ("FULL", "整体", ""),
            ("SINGLE", "单轴", ""),
        ],
        default="FULL",
    )

    def execute(self, context):
        objs = _selected_mesh_objects(context)
        if not objs:
            self.report({"ERROR"}, "No mesh selected")
            return {"CANCELLED"}

        for obj in objs:
            min_x, max_x, mid_x, min_y, max_y, mid_y, min_z, max_z, mid_z = _world_bbox_stats(obj)
            origin = obj.matrix_world.translation.copy()

            if self.offset_mode == "FULL":
                if self.direction == "CENTER":
                    target = Vector((mid_x, mid_y, mid_z))
                elif self.direction == "Z_PLUS":
                    target = Vector((mid_x, mid_y, max_z))
                elif self.direction == "Z_MINUS":
                    target = Vector((mid_x, mid_y, min_z))
                elif self.direction == "X_MINUS":
                    target = Vector((min_x, mid_y, mid_z))
                elif self.direction == "X_PLUS":
                    target = Vector((max_x, mid_y, mid_z))
                elif self.direction == "Y_MINUS":
                    target = Vector((mid_x, min_y, mid_z))
                else:  # Y_PLUS
                    target = Vector((mid_x, max_y, mid_z))
            else:
                if self.direction == "CENTER":
                    target = Vector((mid_x, mid_y, mid_z))
                elif self.direction == "Z_PLUS":
                    target = Vector((origin.x, origin.y, max_z))
                elif self.direction == "Z_MINUS":
                    target = Vector((origin.x, origin.y, min_z))
                elif self.direction == "X_MINUS":
                    target = Vector((min_x, origin.y, origin.z))
                elif self.direction == "X_PLUS":
                    target = Vector((max_x, origin.y, origin.z))
                elif self.direction == "Y_MINUS":
                    target = Vector((origin.x, min_y, origin.z))
                else:  # Y_PLUS
                    target = Vector((origin.x, max_y, origin.z))

            _set_origin_world(context, obj, target)

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
