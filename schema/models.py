from enum import Enum
from pydantic import BaseModel, Field, model_validator

GRID = 0.05  # everything snaps to 5 cm


def on_grid(v: float) -> bool:
    return abs(v / GRID - round(v / GRID)) < 1e-6


class Side(str, Enum):
    north = "north"   # wall at y + length
    south = "south"   # wall at y
    east = "east"     # wall at x + width
    west = "west"     # wall at x


class OpeningType(str, Enum):
    door = "door"
    window = "window"


class Room(BaseModel):
    id: str
    name: str
    x: float = Field(ge=0)          # west edge, meters
    y: float = Field(ge=0)          # south edge, meters
    width: float = Field(gt=0)      # size along X
    length: float = Field(gt=0)     # size along Y

    @model_validator(mode="after")
    def check_grid(self):
        for f in ("x", "y", "width", "length"):
            if not on_grid(getattr(self, f)):
                raise ValueError(f"room '{self.id}': {f} must be a multiple of {GRID} m")
        return self


class Opening(BaseModel):
    type: OpeningType
    room_id: str
    side: Side
    offset: float = Field(ge=0)     # from the wall's west end (N/S walls) or south end (E/W walls)
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    sill: float = Field(default=0, ge=0)   # height above floor (0 for doors)


class Floor(BaseModel):
    level: int = 0
    height: float = Field(default=3.0, gt=0)
    rooms: list[Room] = Field(min_length=1)
    openings: list[Opening] = []

    @model_validator(mode="after")
    def check_floor(self):
        rooms = {}
        for r in self.rooms:
            if r.id in rooms:
                raise ValueError(f"duplicate room id '{r.id}'")
            rooms[r.id] = r

        # rooms must not overlap
        eps = 1e-6
        lst = self.rooms
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                a, b = lst[i], lst[j]
                if (a.x < b.x + b.width - eps and b.x < a.x + a.width - eps and
                        a.y < b.y + b.length - eps and b.y < a.y + a.length - eps):
                    raise ValueError(f"rooms '{a.id}' and '{b.id}' overlap")

        # openings must sit on a real wall and fit
        for o in self.openings:
            if o.room_id not in rooms:
                raise ValueError(f"opening refers to unknown room '{o.room_id}'")
            r = rooms[o.room_id]
            wall_len = r.width if o.side in (Side.north, Side.south) else r.length
            if o.offset + o.width > wall_len + eps:
                raise ValueError(f"{o.type.value} in '{o.room_id}' ({o.side.value}) does not fit on the wall")
            if o.sill + o.height > self.height + eps:
                raise ValueError(f"{o.type.value} in '{o.room_id}' is taller than the floor")
        return self


class House(BaseModel):
    name: str
    wall_thickness: float = Field(default=0.15, gt=0)
    floors: list[Floor] = Field(min_length=1)