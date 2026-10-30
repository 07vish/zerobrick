import json
from pathlib import Path

OUT = Path(__file__).parent / "samples"


def R(id, name, x, y, w, l):
    return dict(id=id, name=name, x=x, y=y, width=w, length=l)


def D(room, side, off, w=0.9, h=2.1):
    return dict(type="door", room_id=room, side=side, offset=off, width=w, height=h, sill=0)


def W(room, side, off, w=1.2, h=1.2, sill=0.9):
    return dict(type="window", room_id=room, side=side, offset=off, width=w, height=h, sill=sill)


def floor(level, rooms, openings, height=3.0):
    return dict(level=level, height=height, rooms=rooms, openings=openings)


def save(fname, name, floors, t=0.15):
    data = dict(name=name, wall_thickness=t, floors=floors)
    (OUT / fname).write_text(json.dumps(data, indent=2), encoding="utf-8")


save("2bhk.json", "2BHK Family", [floor(0,
    [R("living", "Living Room", 0, 0, 5, 4), R("kitchen", "Kitchen", 5, 0, 4, 4),
     R("hall", "Hall", 0, 4, 9, 1.5), R("bed1", "Master Bedroom", 0, 5.5, 4, 4),
     R("bath", "Bathroom", 4, 5.5, 2.5, 4), R("bed2", "Bedroom 2", 6.5, 5.5, 2.5, 4)],
    [D("living", "south", 2.0, 1.0), W("living", "south", 3.5), W("living", "west", 1.5, 1.5),
     D("living", "north", 2.0, 1.0), D("living", "east", 1.5, 1.0),
     D("kitchen", "north", 1.0), W("kitchen", "south", 1.5), W("kitchen", "east", 1.5),
     D("hall", "north", 1.5), D("hall", "north", 4.2, 0.8), D("hall", "north", 7.2),
     W("hall", "west", 0.3, 0.9),
     W("bed1", "west", 1.2, 1.5), W("bed1", "north", 1.0, 1.5),
     W("bath", "north", 0.9, 0.7, 0.6, 1.5),
     W("bed2", "north", 0.5), W("bed2", "east", 1.2, 1.5)])])

save("lshape.json", "L-Shape House", [floor(0,
    [R("living", "Living Room", 0, 0, 6, 4), R("kitchen", "Kitchen", 6, 0, 3, 4),
     R("bed1", "Master Bedroom", 0, 4, 3, 3.5), R("bath", "Bathroom", 0, 7.5, 3, 2.5)],
    [D("living", "south", 2.5, 1.0), W("living", "south", 0.8), W("living", "south", 4.2),
     W("living", "west", 1.5, 1.5), W("living", "north", 3.5, 1.5),
     D("living", "east", 1.5, 1.2), D("living", "north", 1.0),
     W("kitchen", "south", 0.8, 1.2, 1.0, 1.0), W("kitchen", "east", 1.5),
     W("kitchen", "north", 1.0, 1.0, 1.0, 1.0),
     W("bed1", "west", 1.2), W("bed1", "east", 1.2), D("bed1", "north", 1.0, 0.8),
     W("bath", "west", 0.6, 0.6, 0.6, 1.5)])])

save("twofloor.json", "Two-Floor House", [
    floor(0, [R("living", "Living Room", 0, 0, 5, 5), R("kitchen", "Kitchen", 5, 0, 3, 5)],
          [D("living", "south", 2.0, 1.0), W("living", "south", 0.5), W("living", "south", 3.5),
           W("living", "west", 1.5, 1.5), W("living", "north", 1.5, 2.0), D("living", "east", 2.0, 1.2),
           W("kitchen", "south", 0.8, 1.2, 1.0, 1.0), W("kitchen", "east", 1.5),
           W("kitchen", "north", 1.0, 1.0, 1.0, 1.0)]),
    floor(1, [R("bed1", "Master Bedroom", 0, 0, 5, 5), R("bed2", "Bedroom 2", 5, 0, 3, 3),
              R("bath", "Bathroom", 5, 3, 3, 2)],
          [W("bed1", "west", 1.5, 1.5), W("bed1", "south", 1.0, 1.5), W("bed1", "south", 3.0),
           W("bed1", "north", 1.5, 1.5), D("bed1", "east", 0.8), D("bed1", "east", 3.4, 0.8),
           W("bed2", "south", 0.8), W("bed2", "east", 0.8),
           W("bath", "east", 0.6, 0.6, 0.6, 1.5)])])

save("villa.json", "Villa", [floor(0,
    [R("lounge", "Lounge", 0, 0, 7, 6), R("dining", "Dining", 7, 0, 5, 6),
     R("kitchen", "Kitchen", 12, 0, 4, 6), R("hall", "Hall", 0, 6, 16, 2),
     R("bed1", "Bedroom 1", 0, 8, 5, 6), R("bed2", "Bedroom 2", 5, 8, 4, 6),
     R("bed3", "Bedroom 3", 9, 8, 4, 6), R("bath1", "Bathroom 1", 13, 8, 3, 3),
     R("bath2", "Bathroom 2", 13, 11, 3, 3)],
    [D("lounge", "south", 2.5, 1.4, 2.4), W("lounge", "south", 0.5, 1.5, 1.8, 0.6),
     W("lounge", "south", 4.5, 1.8, 1.8, 0.6), W("lounge", "west", 1.0, 2.0, 1.8, 0.6),
     D("lounge", "east", 1.0, 2.5, 2.4), D("lounge", "north", 3.0, 1.0),
     W("dining", "south", 1.0, 2.5, 1.8, 0.6), D("dining", "east", 1.5, 1.2),
     W("kitchen", "south", 1.0, 2.0, 1.2, 1.0), W("kitchen", "east", 2.0, 1.5, 1.2, 1.0),
     D("kitchen", "north", 1.5),
     W("hall", "west", 0.5, 1.0), W("hall", "east", 0.5, 1.0),
     D("hall", "north", 2.0), D("hall", "north", 6.5), D("hall", "north", 10.5),
     D("hall", "north", 13.8, 0.8),
     W("bed1", "west", 1.5, 1.8, 1.5, 0.8), W("bed1", "north", 1.5, 1.8, 1.5, 0.8),
     W("bed2", "north", 1.0, 1.8, 1.5, 0.8), W("bed3", "north", 1.0, 1.8, 1.5, 0.8),
     D("bed3", "east", 3.5, 0.8),
     W("bath1", "east", 0.8, 0.6, 0.6, 1.6), W("bath2", "east", 1.2, 0.6, 0.6, 1.6),
     W("bath2", "north", 1.0, 0.6, 0.6, 1.6)], 3.6)], t=0.2)

print("samples written")