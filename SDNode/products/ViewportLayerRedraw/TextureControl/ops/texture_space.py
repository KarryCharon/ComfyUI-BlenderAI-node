import bpy
from mathutils import Vector

from ..utils import (
    get_image,
    scale_to_matrix
)


class TextureSpaceLocationRestore(bpy.types.Operator):
    bl_idname = "object.texture_space_location_restore"
    bl_label = "Texture Space Location Restore"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH"

    def execute(self, context):
        context.object.data.texspace_location = Vector((0, 0, 0))
        return {"FINISHED"}


class TextureSpaceScaleRestore(bpy.types.Operator):
    bl_idname = "object.texture_space_scale_restore"
    bl_label = "Texture Space Scale Restore"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH"

    def execute(self, context):
        obj = context.object
        self.restore_scale(obj)
        return {"FINISHED"}

    @classmethod
    def restore_scale(cls, obj):
        scale = scale_to_matrix(obj.matrix_world.to_scale())
        dx, dy, dz = scale.inverted() @ obj.dimensions  # 物理尺寸
        obj.data.texspace_size = Vector((dx / 2, dy / 2, dz / 2))


class TextureSpaceApply(bpy.types.Operator):
    bl_idname = "object.texture_space_apply"
    bl_label = "Texture Space Apply"
    bl_options = {'REGISTER'}  # 'UNDO',

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH"

    def invoke(self, context, event):
        bpy.ops.ed.undo_push(message="Push Undo")
        return self.execute(context)

    def execute(self, context):
        print(self.bl_idname)
        obj = context.object
        images = get_image(obj)
        if len(images) == 1:
            if apply_object_image_space_offset(obj):
                TextureSpaceScaleRestore.restore_scale(obj)
                with context.temp_override(object=obj, selected_objects=[obj, ], active_object=obj):
                    bpy.ops.object.origin_set("EXEC_DEFAULT", False, type='ORIGIN_GEOMETRY', center='MEDIAN')
                TextureSpaceScaleRestore.restore_scale(obj)
        else:
            self.report({"ERROR"}, "物体材质需要单张图像")
        return {"FINISHED"}


clss = [
    TextureSpaceLocationRestore,
    TextureSpaceScaleRestore,
    TextureSpaceApply,
]

reg, unreg = bpy.utils.register_classes_factory(clss)


def register():
    reg()


def unregister():
    unreg()
