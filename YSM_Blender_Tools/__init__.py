bl_info = {
    "name": "YSM Blender Tools",
    "author": "mango1991",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > N Panel > YSM",
    "description": "Origin Offset / Zero Location / Arrange Objects",
    "category": "Object",
}

from . import dev_reload
from . import ops_file_import
from . import ops_location_offset
from . import ops_origin_offset
from . import panel_main

_modules = (
    dev_reload,
    ops_file_import,
    ops_location_offset,
    ops_origin_offset,
    panel_main,
)


def register():
    for m in _modules:
        try:
            m.register()
        except Exception:
            # 不让单个模块的注册异常把整个 enable 卡死
            pass


def unregister():
    for m in reversed(_modules):
        try:
            m.unregister()
        except Exception:
            pass
