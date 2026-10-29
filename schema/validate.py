import json
import sys
from pathlib import Path

from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parent))
from models import House


def main(paths):
    ok = True
    for p in paths:
        try:
            House.model_validate(json.loads(Path(p).read_text(encoding="utf-8")))
            print("OK  ", p)
        except (ValidationError, json.JSONDecodeError) as e:
            ok = False
            print("FAIL", p)
            print(e)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    default = sorted(str(p) for p in (Path(__file__).parent / "samples").glob("*.json"))
    main(sys.argv[1:] or default)