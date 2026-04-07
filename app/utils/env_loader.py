from __future__ import annotations

from pathlib import Path


def load_env_file(env_file: Path) -> dict[str, str]:
    """Load simple KEY=VALUE pairs from a .env file."""
    if not env_file.exists():
        return {}

    env_values: dict[str, str] = {}

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        env_values[key.strip()] = _strip_quotes(value.strip())

    return env_values


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value

