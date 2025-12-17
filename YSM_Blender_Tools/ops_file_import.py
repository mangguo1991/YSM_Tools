import bpy


class YSM_OT_file_import(bpy.types.Operator):
    bl_idname = "ysm.file_import"
    bl_label = "File Import"
    bl_options = {"UNDO"}

    def execute(self, context):
        self.report({"INFO"}, "Not implemented")
        return {"FINISHED"}


def register():
    try:
        bpy.utils.unregister_class(YSM_OT_file_import)
    except Exception:
        pass
    bpy.utils.register_class(YSM_OT_file_import)


def unregister():
    try:
        bpy.utils.unregister_class(YSM_OT_file_import)
    except Exception:
        pass
