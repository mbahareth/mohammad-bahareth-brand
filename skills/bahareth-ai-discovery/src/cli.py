"""CLI: isolated public audit and authentic sampled AI answer visibility."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from .audit import audit, HOSTS
from .visibility import measure

def load(path):
    p = json.loads(Path(path).read_text(encoding="utf-8"))
    if p.get("host") not in HOSTS or p.get("person") != "Mohammad Bahareth" or p.get("arabic_name") != "محمد باحارث":
        raise ValueError("Invalid host or canonical identity")
    return p

def main():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="operation", required=True)
    a = subs.add_parser("audit")
    a.add_argument("profile")
    a.add_argument("--out")
    a.add_argument("--timeout", type=float, default=12)
    v = subs.add_parser("visibility")
    v.add_argument("profile")
    v.add_argument("observations")
    v.add_argument("--out")
    args = parser.parse_args()
    p = load(args.profile)
    if args.operation == "audit":
        if args.timeout <= 0 or args.timeout > 60: raise ValueError("Invalid timeout")
        result = audit(p, args.timeout)
        result["observed_at"] = datetime.now(timezone.utc).isoformat()
    else:
        result = measure(p, json.loads(Path(args.observations).read_text(encoding="utf-8")))
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload+"\n", encoding="utf-8")
    print(payload)

if __name__ == "__main__":
    main()