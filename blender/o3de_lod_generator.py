# Copyright (c) 2022-present Sparky Studios. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This script is used to generate a LOD (Level Of Detail) object from the currently selected
object in the Blender scene. Despite the fact that it has been optimized for O3DE, this
script can be used for any other purposes.

This script mainly use the Decimate modifier to generate the LOD object. The user can define
the LOD index and the decimate ratio to customize the generation between objects.
"""

import bpy
from bpy.props import IntProperty, FloatProperty


def generate(context, level, ratio):
    """
    Generates a lod level with a given ratio
    @param context The Blender context.
    @param level The lod level.
    @param ratio The decimate ratio.
    """

    if context.active_object is None:
        return

    object_name = context.object.name

    bpy.ops.object.duplicate()

    context.object.name = object_name + "_lod" + str(level)

    bpy.ops.object.modifier_add(type='DECIMATE')
    context.object.modifiers["Decimate"].ratio = ratio
    context.object.modifiers["Decimate"].use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier="Decimate")

    context.object["o3de.default.lod"] = level


class LodGenerator(bpy.types.Operator):
    """Generate a LOD (Level Of Detail) object from the selected object"""

    bl_idname = "object.lod_generator"
    bl_label = "Generate LOD"

    level: IntProperty(
        name="LOD",
        description="The level of detail index in the range [1..4]. Defaults to 1",
        default=1,
        min=1,
        max=4,
    )

    ratio: FloatProperty(
        name="Decimate Ratio",
        description="The ratio to use on the applied Decimate modifier. Defaults to 0.8",
        default=0.8,
        min=0,
        max=1,
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        generate(context, self.level, self.ratio)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


def menu_func(self, context):
    """Adds the LodGenerator operator in the object menu."""
    self.layout.operator(LodGenerator.bl_idname, text=LodGenerator.bl_label)


def register():
    """Registers the LodGenerator operator in Blender."""
    bpy.utils.register_class(LodGenerator)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    """Unregisters the LodGenerator operator from Blender."""
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(LodGenerator)


if __name__ == "__main__":
    register()
