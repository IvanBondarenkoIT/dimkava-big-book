"""
Verify KA coverage in onboarding YAML (optional).
Run: python tools/fill_onboarding_kb_ka.py
"""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ONB = ROOT / "input" / "hr docs" / "content" / "onboarding_training_plan.yaml"


def main():
    data = yaml.safe_load(ONB.read_text(encoding="utf-8"))
    missing = []
    for m in data.get("modules", []):
        slug = m.get("slug")
        for st in m.get("steps", []):
            o = st.get("order")
            if not st.get("title_ka") or not st.get("content_ka"):
                missing.append(f"{slug} step {o}")
    print("steps missing title_ka or content_ka:", len(missing))
    for x in missing[:40]:
        print(" -", x)
    if len(missing) > 40:
        print(" ...")


if __name__ == "__main__":
    main()
