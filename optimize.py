"""Apply reproducible first-run settings to the pinned upstream workspace."""
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

change("src/game/java/net/minecraft/client/settings/GameSettings.java", [
    ("public int limitFramerate = 260;", "public int limitFramerate = 60;"),
    ("public int clouds = 1;", "public int clouds = 0;"),
    ("public int particleSetting;", "public int particleSetting = 1;"),
    ("public int connectedTexturesOF = 1;", "public int connectedTexturesOF = 0;"),
    ("public boolean customSkyOF = true;", "public boolean customSkyOF = false;"),
])
change("target_teavm_javascript/build.gradle.kts", [
    ("sourceMap = true", "sourceMap = false"),
    ('optimization = OptimizationLevel.BALANCED // Change to "AGGRESSIVE" for release',
     "optimization = OptimizationLevel.AGGRESSIVE"),
])
change("target_teavm_javascript/javascript/index.html", [
    ("EaglercraftX 1.8 test directory HTML page", "Eggocraft browser client with N100-oriented defaults"),
    ("<title>EaglercraftX 1.8</title>", "<title>Eggocraft</title>"),
    ('{ addr: "ws://localhost:8081/", name: "Local test server" }', ""),
])
print("Applied N100 defaults and release compiler configuration.")
