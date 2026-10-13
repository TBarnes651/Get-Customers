"""Verify SENRAB phase-one safety settings against the EFFECTIVE configuration.

Run:  .venv/bin/python scripts/check_phase_one.py     (Windows: .venv\\Scripts\\python scripts\\check_phase_one.py)
Exit code 0 = all checks pass. Reads only; changes nothing.
"""
import asyncio
import sys
from pathlib import Path

from harvey.config import _find_config_file, load_config, load_env
from harvey.paths import PROJECT_ROOT
from harvey.state import StateManager

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'ok' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


path = Path(_find_config_file())
cfg = load_config()
env = load_env()
e, li, q = cfg.channels.email, cfg.channels.linkedin, cfg.usage.quiet_hours

print(f"\n  Effective config file: {path}")
check("loader uses harvey.yaml (no harvey.local.yaml override)", path.name == "harvey.yaml")
check("email channel disabled", e.enabled is False)
check("linkedin channel disabled", li.enabled is False)
check("email.require_approval is true", e.require_approval is True)
check("email.send_to_risky is false", e.send_to_risky is False)
check("max_daily_sends is 0", e.max_daily_sends == 0)
check("timezone is Europe/London", q.timezone == "Europe/London", q.timezone)
check("Claude usage budget is 20%", cfg.usage.max_daily_claude_percent == 20.0)
check("persona email blank (none supplied)", cfg.persona.email == "")
check("persona linkedin blank (none supplied)", cfg.persona.linkedin == "")

secrets = {k: v for k, v in env.model_dump().items()
           if v not in ("", 0) and not k.endswith("_port") and k != "dataforseo_sandbox"}
check("provider credentials all blank in .env", not secrets, ", ".join(secrets) if secrets else "")

# The dashboard's default bind address is defined by the CLI parser.
import harvey.cli as cli  # noqa: E402
src = Path(cli.__file__).read_text()
check("dashboard default host is 127.0.0.1", 'add_argument("--host", default="127.0.0.1"' in src)


async def paused() -> str:
    s = StateManager()
    await s.init_db()
    return await s.get_setting("sending_paused") or ""

p = asyncio.run(paused())
check("sending kill switch is PAUSED", bool(p), p)

print()
sys.exit(1 if failures else 0)
