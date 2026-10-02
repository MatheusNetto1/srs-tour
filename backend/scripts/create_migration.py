import re
import subprocess
import sys
from pathlib import Path

VERSIONS_DIR = Path("alembic/versions")
MIGRATION_PATTERN = re.compile(r"^(\d{4})_")


def get_next_number() -> int:
    numbers = []

    for path in VERSIONS_DIR.glob("*.py"):
        match = MIGRATION_PATTERN.match(path.name)

        if match:
            numbers.append(int(match.group(1)))

    return max(numbers, default=0) + 1


def slugify(message: str) -> str:
    slug = message.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)

    return slug.strip("_")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            'Usage: python scripts/create_migration.py "migration message"'
        )

    message = " ".join(sys.argv[1:])
    number = get_next_number()

    subprocess.run(
        [
            "alembic",
            "revision",
            "--autogenerate",
            "-m",
            message,
        ],
        check=True,
    )

    migrations = sorted(
        VERSIONS_DIR.glob("*.py"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not migrations:
        raise RuntimeError("Alembic did not generate a migration.")

    generated = migrations[0]

    new_name = f"{number:04d}_{slugify(message)}.py"

    destination = VERSIONS_DIR / new_name

    generated.rename(destination)

    print(f"Migration created: {destination}")


if __name__ == "__main__":
    main()
