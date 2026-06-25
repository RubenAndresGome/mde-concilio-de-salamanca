import os
import sys


def main():
    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    )
    from concilio_salamanca.prompts import system_prompts

    prompts = []
    for var_name in dir(system_prompts):
        if var_name.isupper():
            content = getattr(system_prompts, var_name)
            if isinstance(content, str):
                prompts.append((var_name, content))

    output_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "PROMPTS_OPEN_SOURCE.md")
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Concilio de Salamanca - System Prompts Open Source\n\n")
        f.write(
            "Este documento contiene los 18 system prompts originales de los agentes del Concilio de Salamanca.\n\n"
        )

        for name, content in prompts:
            f.write(f"## {name}\n\n")
            f.write("```markdown\n")
            f.write(content.strip() + "\n")
            f.write("```\n\n")

    print(f"Exportados {len(prompts)} prompts a {output_path}")


if __name__ == "__main__":
    main()
