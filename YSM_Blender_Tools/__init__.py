bl_info = {
    "name": "YSM Blender Tools",
    "author": "YSM",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > YSM",
    "category": "Object",
}

from . import dev_reload
from . import panel_main
from . import ops_file_import
from . import ops_origin_offset
from . import ops_location_offset
from . import ops_arrange_objects


_MODULES = (
    dev_reload,
    ops_file_import,
    ops_origin_offset,
    ops_location_offset,
    ops_arrange_objects,
    panel_main,
)


def register():
    for m in _MODULES:
        if hasattr(m, "register"):
            m.register()


def unregister():
    for m in reversed(_MODULES):
        if hasattr(m, "unregister"):
            m.unregister()
