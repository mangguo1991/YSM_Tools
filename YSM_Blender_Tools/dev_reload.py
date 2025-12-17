import bpy
import importlib
import sys


class YSM_OT_dev_reload(bpy.types.Operator):
    bl_idname = "ysm.dev_reload"
    bl_label = "Reload YSM Addon"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        pkg = __package__ or "YSM_Blender_Tools"
        if pkg not in sys.modules:
            self.report({"ERROR"}, f"'{pkg}' not in sys.modules")
            return {"CANCELLED"}

        names = [n for n in sys.modules.keys() if n == pkg or n.startswith(pkg + ".")]
        # 子模块先 reload，最后根包
        names.sort(key=lambda n: 1 if n == pkg else 0)

        for name in names:
            mod = sys.modules.get(name)
            if mod:
                importlib.reload(mod)

        self.report({"INFO"}, "Reloaded")
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
