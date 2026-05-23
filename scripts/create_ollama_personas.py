from pathlib import Path
import subprocess
import re

BASE_MODEL = "llama3.2:3b"
PERSONAS_DIR = Path("personas")
MODELFILES_DIR = Path("modelfiles")


def slugify(filename: str) -> str:
    name = filename.replace(".md", "")
    name = re.sub(r"[^a-zA-Z0-9-]+", "-", name)
    return name.lower()


def main() -> None:
    MODELFILES_DIR.mkdir(exist_ok=True)

    persona_files = sorted(PERSONAS_DIR.glob("*.md"))

    if not persona_files:
        print("No persona files found.")
        return

    for persona_file in persona_files:
        model_name = slugify(persona_file.name)
        system_prompt = persona_file.read_text(encoding="utf-8")

        modelfile = MODELFILES_DIR / f"Modelfile.{model_name}"

        modelfile.write_text(
            f'''FROM {BASE_MODEL}

PARAMETER temperature 0.2
PARAMETER num_ctx 4096

SYSTEM """
{system_prompt}
"""
''',
            encoding="utf-8",
        )

        print(f"Creating Ollama model: {model_name}")

        subprocess.run(
            ["ollama", "create", model_name, "-f", str(modelfile)],
            check=True,
        )

    print("All persona models created.")


if __name__ == "__main__":
    main()
