import bpy
import sys
import importlib


class YSM_OT_dev_reload(bpy.types.Operator):
    bl_idname = "ysm.dev_reload"
    bl_label = "Reload"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        pkg = __package__  # "YSM_Blender_Tools"
        if not pkg:
            return {"CANCELLED"}

        # 拿到插件主模块（__init__）
        addon = sys.modules.get(pkg)
        if addon is None:
            addon = importlib.import_module(pkg)

        # 1) 先 unregister（避免 class already registered）
        if hasattr(addon, "unregister"):
            try:
                addon.unregister()
            except Exception:
                pass

        # 2) reload 所有子模块（只 reload 你这个包下面的）
        names = [n for n in list(sys.modules.keys()) if n == pkg or n.startswith(pkg + ".")]
        # 子模块先 reload（避免 partially initialized）
        names.sort(key=lambda x: x.count("."), reverse=True)
        for n in names:
            m = sys.modules.get(n)
            if m:
                try:
                    importlib.reload(m)
                except Exception:
                    pass

        # 3) 再 register
        if hasattr(addon, "register"):
            try:
                addon.register()
            except Exception as e:
                self.report({"ERROR"}, str(e))
                return {"CANCELLED"}

        return {"FINISHED"}


def register():
    try:
        bpy.utils.unregister_class(YSM_OT_dev_reload)
    except Exception:
        pass
    bpy.utils.register_class(YSM_OT_dev_reload)


def unregister():
    try:
        bpy.utils.unregister_class(YSM_OT_dev_reload)
    except Exception:
        pass
