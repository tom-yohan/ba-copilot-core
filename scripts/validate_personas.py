from pathlib import Path
import sys

REQUIRED_SECTIONS = [
    "Primary perspective:",
    "Focus on:",
    "Always identify:",
    "Output style:",
    "Guardrails:",
]

personas_dir = Path("personas")
failed = []

for file in sorted(personas_dir.glob("*.md")):
    text = file.read_text(encoding="utf-8")

    missing = [section for section in REQUIRED_SECTIONS if section not in text]

    if missing:
        failed.append((file, missing))

if failed:
    print("Persona validation failed.\n")
    for file, missing in failed:
        print(f"{file}:")
        for section in missing:
            print(f"  Missing: {section}")
        print()
    sys.exit(1)

print("All persona files passed validation.")
