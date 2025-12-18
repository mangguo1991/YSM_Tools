import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
import os


class YSM_OT_file_import(bpy.types.Operator, ImportHelper):
    bl_idname = "ysm.file_import"
    bl_label = "文件导入"
    bl_options = {"UNDO"}

    # 允许多选
    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    directory: StringProperty(subtype="DIR_PATH")

    filter_glob: StringProperty(
        default="*.fbx;*.glb;*.gltf;*.obj",
        options={"HIDDEN"},
    )

    def execute(self, context):
        imported_objects = []

        for f in self.files:
            path = os.path.join(self.directory, f.name)
            ext = os.path.splitext(f.name)[1].lower()

            before = set(bpy.data.objects)

            if ext == ".fbx":
                bpy.ops.import_scene.fbx(filepath=path)
            elif ext in {".glb", ".gltf"}:
                bpy.ops.import_scene.gltf(filepath=path)
            elif ext == ".obj":
                bpy.ops.import_scene.obj(filepath=path)
            else:
                self.report({"WARNING"}, f"不支持的格式: {f.name}")
                continue

            after = set(bpy.data.objects)
            imported_objects.extend(list(after - before))

        # 导入后选中
        for obj in context.selected_objects:
            obj.select_set(False)

        for obj in imported_objects:
            obj.select_set(True)

        if imported_objects:
            context.view_layer.objects.active = imported_objects[0]

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
