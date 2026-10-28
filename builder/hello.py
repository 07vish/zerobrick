import sys
import bpy

# args after "--" are ours (Blender eats everything before it)
out_path = sys.argv[sys.argv.index("--") + 1]

# 1. start from an empty scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# 2. make a 2m cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))

# 3. export as GLB
bpy.ops.export_scene.gltf(filepath=out_path, export_format="GLB")

print("DONE:", out_path)