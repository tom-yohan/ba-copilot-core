from pathlib import Path
import sys

REQUIRED_SECTIONS = [
    "Purpose:",
    "Inputs:",
    "Output:",
    "Rules:",
    "Quality Bar:",
]

prompts_dir = Path("prompts")
failed = []

for file in sorted(prompts_dir.glob("*.md")):
    text = file.read_text(encoding="utf-8")
    missing = [section for section in REQUIRED_SECTIONS if section not in text]

    if missing:
        failed.append((file, missing))

if failed:
    print("Prompt validation failed.\n")
    for file, missing in failed:
        print(f"{file}:")
        for section in missing:
            print(f"  Missing: {section}")
        print()
    sys.exit(1)

print("All prompt files passed validation.")
