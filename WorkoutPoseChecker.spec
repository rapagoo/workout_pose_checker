# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all


ultralytics_data, ultralytics_binaries, ultralytics_hidden_imports = collect_all(
    "ultralytics"
)

analysis = Analysis(
    ["src/workout_pose_checker/main_window.py"],
    pathex=["src"],
    binaries=ultralytics_binaries,
    datas=[
        (
            "src/workout_pose_checker/images",
            "workout_pose_checker/images",
        ),
        *ultralytics_data,
    ],
    hiddenimports=ultralytics_hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(analysis.pure)

executable = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="WorkoutPoseChecker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    upx=True,
    upx_exclude=[],
    name="WorkoutPoseChecker",
)
