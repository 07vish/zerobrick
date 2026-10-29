import copy
import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "schema"))
from models import House

GOOD = json.loads((ROOT / "schema" / "samples" / "1bhk.json").read_text(encoding="utf-8"))


def make(mutate):
    """copy the good house, apply one breaking change to floor 0"""
    data = copy.deepcopy(GOOD)
    mutate(data["floors"][0])
    return data


def room(floor, rid):
    return next(r for r in floor["rooms"] if r["id"] == rid)


def test_good_house_passes():
    House.model_validate(GOOD)


def test_overlapping_rooms_rejected():
    data = make(lambda f: room(f, "bath").update(x=3.0))
    with pytest.raises(ValidationError, match="overlap"):
        House.model_validate(data)


def test_off_grid_size_rejected():
    data = make(lambda f: room(f, "living").update(width=4.03))
    with pytest.raises(ValidationError, match="multiple of"):
        House.model_validate(data)


def test_opening_too_wide_rejected():
    data = make(lambda f: f["openings"][0].update(width=5.0))
    with pytest.raises(ValidationError, match="does not fit"):
        House.model_validate(data)


def test_unknown_room_rejected():
    data = make(lambda f: f["openings"][0].update(room_id="garage"))
    with pytest.raises(ValidationError, match="unknown room"):
        House.model_validate(data)


def test_duplicate_room_id_rejected():
    data = make(lambda f: room(f, "bath").update(id="kitchen"))
    with pytest.raises(ValidationError, match="duplicate"):
        House.model_validate(data)


def test_door_taller_than_floor_rejected():
    data = make(lambda f: f["openings"][0].update(height=3.5))
    with pytest.raises(ValidationError, match="taller"):
        House.model_validate(data)