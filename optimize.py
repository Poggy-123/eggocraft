"""Apply reproducible N100-oriented changes to the pinned upstream workspace."""
from pathlib import Path
import sys

root = Path(sys.argv[1])

def change(relative, replacements):
    path = root / relative
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in replacements:
        if text.count(old) != 1:
            raise SystemExit(f"Unexpected upstream content in {relative}: {old}")
        text = text.replace(old, new)
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))

# First-run video settings. They only apply until you change them in-game,
# because the game saves your own choices over them.
change("src/game/java/net/minecraft/client/settings/GameSettings.java", [
    # Only used when VSync is off: cap at 60 instead of 260 so the 6 W N100
    # doesn't run hot drawing frames the monitor can't show.
    ("public int limitFramerate = 260;", "public int limitFramerate = 60;"),
    # Clouds are a large transparent pass the UHD iGPU pays for every frame.
    ("public int clouds = 1;", "public int clouds = 0;"),
    # "Decreased" particles.
    ("public int particleSetting;", "public int particleSetting = 1;"),
    # Connected textures and custom skies add work to chunk rebuilds and sky draws.
    ("public int connectedTexturesOF = 1;", "public int connectedTexturesOF = 0;"),
    ("public boolean customSkyOF = true;", "public boolean customSkyOF = false;"),
])

# JavaScript client (fallback for browsers without WASM-GC).
change("target_teavm_javascript/build.gradle.kts", [
    ("sourceMap = true", "sourceMap = false"),
    ('optimization = OptimizationLevel.BALANCED // Change to "AGGRESSIVE" for release',
     "optimization = OptimizationLevel.AGGRESSIVE"),
])

# WASM-GC client. The disassembly is a build-time listing that never ships,
# so skipping it only makes the build faster.
change("target_teavm_wasm_gc/build.gradle.kts", [
    ("disassembly = true", "disassembly = false"),
])

print("Applied N100 defaults and release compiler configuration.")
