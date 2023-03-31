import os
import bpy
import numpy as np
import sys
import json
import argparse

def remove_all_collections() -> None:
    # avoid holding references to any objects, which might cause memory error
    # the list conversion is required to prevent crashing
    for collection in list(bpy.data.collections):
        for obj in list(collection.all_objects):
            bpy.data.objects.remove(obj)
        bpy.data.collections.remove(collection)

def require_collection(name: str) -> bpy.types.Collection:
    """
    Return colleciton with name, create if not exist.
    """
    if name not in bpy.data.collections:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return bpy.data.collections[name]

def link_to_collection(obj, col):
    if obj.name not in col.objects:
        col.objects.link(obj)

def main(args):
    bone_idx = args.bone_idx
    raw_mesh_root = 'data/bone_generation/raw'
    if args.bone_idx < 50:
        raw_mesh_root = 'data/bone_generation_ood/raw'
    bone_scale = np.array([0.15, 0.15, 0.1])
    bone_thickness = 0.04
    bone_pos = np.array([0.5, 0.1, 0.5])
    bone_offset = np.array([0.01, -0.04, -0.03])

    qr_bottom_scale = np.array([2, 2, 2])
    qr_bottom_pos = np.array([0.4, 0.0, 0.45])
    qr_bottom_thickness = 0.015

    support_scale = np.array([0.02, 0.025, 0.02])
    support_pos = np.array([0.43, 0.035, 0.47])

    base_scale = np.array([0.2-qr_bottom_thickness, 0.015, 0.1]) / 2
    base_pos = np.array([0.5 + qr_bottom_thickness / 2, base_scale[1], 0.5])

    text_depth = 0.02
    text_scale = np.array([0.02, 0.02, 0.02])
    text_pos = np.array([0.46, 0.03, 0.45 + bone_thickness])

    global_scale = 0.5 * 1000
    print_scale = 0.992

    # save config
    config = {
        'bone_offset': list(bone_offset),
        'base_scale': list(base_scale),
        'base_pos': list(base_pos),
        'global_scale': global_scale
    }
    # Serializing json
    config_json = json.dumps(config, indent=4)
    
    # Writing to sample.json
    with open('roboninja/asset/bone_printing_config.json', 'w') as outfile:
        outfile.write(config_json)


    # preprocess
    remove_all_collections()
    target_col = require_collection('target')
    source_col =require_collection('source')

    # load bone
    bone_mesh_path = os.path.join(raw_mesh_root, f'bone_{bone_idx}.obj')
    bpy.ops.import_scene.obj(filepath=str(bone_mesh_path), axis_up='Z', axis_forward='Y')
    bone_obj = bpy.context.selected_objects[0]
    link_to_collection(bone_obj, target_col)
    bone_obj.select_set(False)
    print("Loaded: " + bone_obj.name)

    # transform bone
    bone_obj.select_set(True)
    bpy.ops.transform.resize(value=bone_scale)
    thick_scale = bone_thickness / bone_obj.dimensions[2]
    bpy.ops.transform.resize(value=(1, 1, thick_scale))
    bpy.ops.transform.translate(value=bone_pos)
    bpy.ops.transform.translate(value=bone_offset)
    bone_obj.select_set(False)

    # create base
    bpy.ops.mesh.primitive_cube_add()
    base_obj = bpy.context.selected_objects[0]
    link_to_collection(base_obj, source_col)
    base_obj.select_set(False)

    # transform base
    base_obj.select_set(True)
    bpy.ops.transform.resize(value=base_scale)
    bpy.ops.transform.translate(value=base_pos)
    base_obj.select_set(False)


    # create support
    bpy.ops.mesh.primitive_cube_add()
    support_obj = bpy.context.selected_objects[0]
    link_to_collection(support_obj, source_col)
    support_obj.select_set(False)

    # transform support
    support_obj.select_set(True)
    bpy.ops.transform.resize(value=support_scale)
    bpy.ops.transform.translate(value=support_pos)
    support_obj.select_set(False)


    # create support2
    bpy.ops.mesh.primitive_cube_add()
    support2_obj = bpy.context.selected_objects[0]
    link_to_collection(support2_obj, source_col)
    support2_obj.select_set(False)

    # transform support2
    support2_obj.select_set(True)
    bpy.ops.transform.resize(value=[0.04, 0.005, 0.02])
    bpy.ops.transform.translate(value=[0.51, 0.05, 0.5])
    support2_obj.select_set(False)


    if bone_idx >= 20 and bone_idx < 50:
        # create support-ood
        bpy.ops.mesh.primitive_cube_add()
        support_ood_obj = bpy.context.selected_objects[0]
        link_to_collection(support_ood_obj, source_col)
        support_ood_obj.select_set(False)

        # transform support-ood
        support_ood_obj.select_set(True)
        bpy.ops.transform.resize(value=[0.06, 0.025, 0.02])
        bpy.ops.transform.translate(value=[0.51, 0.035, 0.47])
        support_ood_obj.select_set(False)

    # create qr_bottom
    bpy.ops.import_mesh.stl(filepath='roboninja/asset/qr-bottom.stl')
    qr_bottom_obj = bpy.context.selected_objects[0]
    link_to_collection(qr_bottom_obj, source_col)
    qr_bottom_obj.select_set(False)
    
    # transform qr_bottom
    qr_bottom_obj.select_set(True)
    bpy.ops.transform.rotate(value=-90/180*np.pi, orient_axis='X')
    bpy.ops.transform.rotate(value=-90/180*np.pi, orient_axis='Z')
    bpy.ops.transform.resize(value=qr_bottom_scale)
    bpy.ops.transform.translate(value=qr_bottom_pos)
    bpy.ops.transform.translate(value=[qr_bottom_obj.dimensions[2], 0, 0])
    qr_bottom_obj.select_set(False)

    print('dimensions: ', qr_bottom_obj.dimensions)

    # create text
    bpy.ops.object.text_add()
    text_obj = bpy.context.selected_objects[0]
    text_obj.data.body = f'{int(round(global_scale / 50))}cm-{bone_idx}'
    link_to_collection(text_obj, source_col)
    text_obj.select_set(False)

    # transform text
    text_obj.select_set(True)
    # bpy.ops.transform.rotate(value=90/180*np.pi, orient_axis='X')
    bpy.ops.transform.resize(value=text_scale)
    bpy.ops.transform.translate(value=text_pos)
    text_obj.select_set(False)

    # extrude
    solid_mod = text_obj.modifiers.new(
            name='solid_' + text_obj.name, type='SOLIDIFY')
    solid_mod.thickness = -text_depth
    solid_mod.offset = -1

    # convert to mesh
    text_obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    text_obj.select_set(False)

    # union
    bool_mod = bone_obj.modifiers.new(
        name='union_' + bone_obj.name, type='BOOLEAN')
    bool_mod.operation = 'UNION'
    bool_mod.operand_type = 'COLLECTION'
    bool_mod.collection = source_col
    bool_mod.solver = 'EXACT'
    print("Applying boolean modifier")
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)

    # export
    out_path = f'data/bone_printing/print_bone_blender-{args.bone_idx}.{args.format}'
    bpy.context.view_layer.objects.active = bone_obj
    bone_obj.select_set(True)
    if out_path.endswith('obj'):
        bpy.ops.wm.obj_export(
            filepath=str(out_path), 
            export_selected_objects=True,
            export_uv=False,
            export_normals=False,
            export_materials=False,
            # scaling_factor=global_scale * print_scale
        )
    elif out_path.endswith('stl'):
        bpy.ops.export_mesh.stl(
            filepath=str(out_path),
            check_existing=False,
            use_selection=True,
            global_scale=global_scale * print_scale
        )
    else:
        raise NotImplementedError(f'{out_path[-3:]} is not supported')

    
    # bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('bone_print.blend'))

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bone_idx', default=0, type=int, help='bone idx')
    parser.add_argument('--format', default='stl', type=str, choices=['stl', 'obj'], help='file format')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    main(args)
