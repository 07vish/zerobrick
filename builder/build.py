import json
import sys

import bmesh
import bpy

SLAB = 0.15
EPS = 1e-4


def r4(v):
    return round(v, 4)


src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
with open(src, encoding="utf-8") as f:
    house = json.load(f)
T = house.get("wall_thickness", 0.15)
HALF = T / 2

bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name, color, alpha=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value = 0.9
    if alpha is not None:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.blend_method = "BLEND"
        except AttributeError:
            pass
    return m


M_WALL = material("wall", (0.93, 0.91, 0.87, 1))
M_FLOOR = material("floor", (0.60, 0.55, 0.50, 1))
M_ROOF = material("roof", (0.25, 0.25, 0.28, 1))
M_GLASS = material("glass", (0.60, 0.80, 0.95, 1), alpha=0.3)


def box(name, x0, y0, z0, x1, y1, z1, mat=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    pts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
           (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    v = [bm.verts.new(p) for p in pts]
    for f in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
        bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj


def merge(intervals):
    intervals.sort()
    out = []
    for a, b in intervals:
        if out and a <= out[-1][1] + EPS:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def cut(wall, cutters):
    if not cutters:
        return
    for i, c in enumerate(cutters):
        m = wall.modifiers.new(f"cut{i}", "BOOLEAN")
        m.operation = "DIFFERENCE"
        m.object = c
        m.solver = "EXACT"
    bpy.context.view_layer.objects.active = wall
    wall.select_set(True)
    for m in list(wall.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)
    for c in cutters:
        mesh = c.data
        bpy.data.objects.remove(c, do_unlink=True)
        bpy.data.meshes.remove(mesh)


def build_floor(fl, z0, is_top):
    rooms = {r["id"]: r for r in fl["rooms"]}
    h = fl["height"]
    zb = z0 - SLAB
    zt = z0 + h + (SLAB if is_top else 0)
    tag = f"f{fl['level']}"

    # floor slabs (+ roof on the top level)
    for r in fl["rooms"]:
        x0, y0 = r["x"], r["y"]
        x1, y1 = x0 + r["width"], y0 + r["length"]
        box(f"{tag}_floor_{r['id']}", x0, y0, zb, x1, y1, z0, M_FLOOR)
        if is_top:
            box(f"{tag}_roof_{r['id']}", x0, y0, z0 + h, x1, y1, zt, M_ROOF)

    # wall lines from room edges; shared edges merge into one wall
    lines = {"h": {}, "v": {}}
    for r in fl["rooms"]:
        x0, y0 = r["x"], r["y"]
        x1, y1 = x0 + r["width"], y0 + r["length"]
        for y in (y0, y1):
            lines["h"].setdefault(r4(y), []).append((x0, x1))
        for x in (x0, x1):
            lines["v"].setdefault(r4(x), []).append((y0, y1))

    # openings in absolute coordinates (de-duplicated)
    opens = {}
    for o in fl["openings"]:
        r = rooms[o["room_id"]]
        s = o["side"]
        if s in ("south", "north"):
            axis = "h"
            line = r["y"] if s == "south" else r["y"] + r["length"]
            a0 = r["x"] + o["offset"]
        else:
            axis = "v"
            line = r["x"] if s == "west" else r["x"] + r["width"]
            a0 = r["y"] + o["offset"]
        key = (axis, r4(line), r4(a0), r4(a0 + o["width"]),
               r4(o.get("sill", 0)), r4(o["height"]), o["type"])
        opens[key] = True

    for axis, group in lines.items():
        for line, ivs in group.items():
            for s, e in merge(ivs):
                name = f"{tag}_wall_{axis}_{line}_{r4(s)}"
                if axis == "h":
                    wall = box(name, s - HALF, line - HALF, zb, e + HALF, line + HALF, zt, M_WALL)
                else:
                    wall = box(name, line - HALF, s, zb, line + HALF, e, zt, M_WALL)
                cutters = []
                for (ax, ln, a0, a1, sill, oh, typ) in opens:
                    if ax != axis or ln != line or a0 < s - EPS or a1 > e + EPS:
                        continue
                    lo, hi = z0 + sill, z0 + sill + oh
                    m = HALF + 0.05
                    if axis == "h":
                        cutters.append(box("cut", a0, line - m, lo, a1, line + m, hi))
                        if typ == "window":
                            box(f"{tag}_glass", a0, line - 0.01, lo, a1, line + 0.01, hi, M_GLASS)
                    else:
                        cutters.append(box("cut", line - m, a0, lo, line + m, a1, hi))
                        if typ == "window":
                            box(f"{tag}_glass", line - 0.01, a0, lo, line + 0.01, a1, hi, M_GLASS)
                cut(wall, cutters)


floors = sorted(house["floors"], key=lambda f: f["level"])
z = 0.0
for i, fl in enumerate(floors):
    build_floor(fl, z, i == len(floors) - 1)
    z += fl["height"]

bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB")
print("DONE:", dst)