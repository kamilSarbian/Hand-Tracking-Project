# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_dynamic_libs

project_root = Path(SPECPATH).resolve()
build_mode = os.environ.get("HAND_TRACKING_BUILD_MODE", "onedir").lower()
if build_mode not in {"onedir", "onefile"}:
    raise ValueError("HAND_TRACKING_BUILD_MODE must be either 'onedir' or 'onefile'")

is_onefile = build_mode == "onefile"
application_name = "GestureDrawingApp" if is_onefile else "GestureDrawingApp-debug"

datas = [
    (str(project_root / "settings.json"), "."),
    (
        str(project_root / "models_assets" / "hand_landmarker.task"),
        "models_assets",
    ),
]
local_settings_path = project_root / "settings.local.json"
if local_settings_path.is_file():
    datas.append((str(local_settings_path), "."))

binaries = []
hidden_imports = []

# MediaPipe loads its task runtime DLL dynamically, so static analysis cannot
# reliably discover it. PyInstaller's built-in hooks handle sounddevice and
# imageio-ffmpeg without collecting their unrelated modules.
binaries.extend(collect_dynamic_libs("mediapipe"))

analysis = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={"matplotlib": {"backends": "Agg"}},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
    optimize=0,
)
python_archive = PYZ(analysis.pure)

if is_onefile:
    executable = EXE(
        python_archive,
        analysis.scripts,
        analysis.binaries,
        analysis.datas,
        [],
        name=application_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
else:
    executable = EXE(
        python_archive,
        analysis.scripts,
        [],
        exclude_binaries=True,
        name=application_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=True,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    bundle = COLLECT(
        executable,
        analysis.binaries,
        analysis.datas,
        strip=False,
        upx=False,
        upx_exclude=[],
        name=application_name,
    )
