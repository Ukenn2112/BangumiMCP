from __future__ import annotations

import io
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON_MODULES_DIR = PROJECT_ROOT / "python_modules"
SYNC_TOKEN = PYTHON_MODULES_DIR / ".synced"

PURE_REQUIREMENTS = [
    "annotated-types==0.7.0",
    "anyio==4.9.0",
    "attrs==26.1.0",
    "certifi==2025.1.31",
    "click==8.1.8",
    "h11==0.14.0",
    "httpcore==1.0.8",
    "httpx==0.28.1",
    "httpx-sse==0.4.0",
    "idna==3.10",
    "jsonschema==4.26.0",
    "jsonschema-specifications==2025.9.1",
    "markdown-it-py==3.0.0",
    "mcp==1.12.0",
    "mdurl==0.1.2",
    "pydantic==2.10.6",
    "pydantic-settings==2.5.2",
    "pygments==2.19.1",
    "pyjson5==2.0.0",
    "python-dotenv==1.1.0",
    "python-multipart==0.0.26",
    "referencing==0.37.0",
    "rich==14.0.0",
    "sniffio==1.3.1",
    "sse-starlette==2.2.1",
    "starlette==0.46.2",
    "typing-extensions==4.15.0",
    "typing-inspection==0.4.2",
    "uvicorn==0.34.1",
]

PYODIDE_WHEELS = {
    "pydantic-core": {
        "url": "https://cdn.jsdelivr.net/pyodide/v0.28.3/full/"
        "pydantic_core-2.27.2-cp313-cp313-pyodide_2025_0_wasm32.whl",
    },
    "rpds-py": {
        "url": "https://cdn.jsdelivr.net/pyodide/v0.28.3/full/"
        "rpds_py-0.23.1-cp313-cp313-pyodide_2025_0_wasm32.whl",
    },
}


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def extract_wheel(url: str, destination: Path) -> None:
    with urllib.request.urlopen(url) as response:
        data = response.read()

    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        archive.extractall(destination)


def sync_python_modules() -> None:
    if PYTHON_MODULES_DIR.exists():
        shutil.rmtree(PYTHON_MODULES_DIR)

    PYTHON_MODULES_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as handle:
        requirements_file = Path(handle.name)
        handle.write("\n".join(PURE_REQUIREMENTS))

    try:
        run(
            [
                "uv",
                "pip",
                "install",
                "--target",
                str(PYTHON_MODULES_DIR),
                "--no-deps",
                "--link-mode",
                "copy",
                "--index-url",
                "https://pypi.org/simple",
                "-r",
                str(requirements_file),
            ]
        )
    finally:
        requirements_file.unlink(missing_ok=True)

    for package in PYODIDE_WHEELS.values():
        extract_wheel(package["url"], PYTHON_MODULES_DIR)

    (PYTHON_MODULES_DIR / "pyvenv.cfg").touch()
    SYNC_TOKEN.touch()


if __name__ == "__main__":
    sync_python_modules()
