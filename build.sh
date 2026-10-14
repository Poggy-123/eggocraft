#!/usr/bin/env bash
# Builds the Eggocraft website into build/site.
#
# Downloads the pinned EaglercraftX workspace, applies optimize.py, compiles
# the clients and copies them next to the pages in site/.
#
# TARGETS="js wasm" (the default) builds both clients. TARGETS=js skips the
# WASM-GC client; use it only for local testing, then open /js/ directly.
set -euo pipefail

UPSTREAM_REPO=https://github.com/Eaglercraft-Archive/EaglercraftX-1_8-workspace.git
UPSTREAM_COMMIT=746793a11eb67608b4e60660a4dfe205f5f68970 # u53

here=$(cd "$(dirname "$0")" && pwd)
work=$here/build/workspace
out=$here/build/site
targets=" ${TARGETS:-js wasm} "

if [ ! -d "$work/.git" ]; then
	git init -q "$work"
	git -C "$work" fetch -q --depth 1 "$UPSTREAM_REPO" "$UPSTREAM_COMMIT"
fi
# Start from pristine upstream files so optimize.py applies cleanly on re-runs.
git -C "$work" -c advice.detachedHead=false checkout -q -f "$UPSTREAM_COMMIT"

python3 "$here/optimize.py" "$work"

tasks=()
if [[ $targets == *" js "* ]]; then
	tasks+=(target_teavm_javascript:makeMainOfflineDownload)
fi
if [[ $targets == *" wasm "* ]]; then
	tasks+=(target_teavm_wasm_gc:makeMainWasmClientBundle)
else
	# Not configuring the WASM-GC project avoids downloading its TeaVM fork.
	sed -i '/include("target_teavm_wasm_gc")/d' "$work/settings.gradle.kts"
fi
(cd "$work" && chmod +x gradlew && ./gradlew --no-daemon "${tasks[@]}")

rm -rf "$out"
cp -r "$here/site" "$out"

if [[ $targets == *" js "* ]]; then
	js=$work/target_teavm_javascript/javascript
	cp "$js/classes.js" "$js/assets.epk" "$js/favicon.png" "$out/js/"
	cp -r "$js/lang" "$out/js/lang"
fi
if [[ $targets == *" wasm "* ]]; then
	wasm=$work/target_teavm_wasm_gc/javascript_dist
	cp "$wasm/bootstrap.js" "$wasm/assets.epw" "$wasm/favicon.png" "$out/wasm/"
fi
cp "$work/target_teavm_javascript/javascript/favicon.png" "$out/favicon.png"

du -ah "$out" | sort -h | tail -n 8

# Cloudflare Pages refuses to deploy any single file over 25 MiB.
too_big=$(find "$out" -type f -size +25M)
if [ -n "$too_big" ]; then
	echo "These files are over Cloudflare Pages' 25 MiB limit:" >&2
	echo "$too_big" >&2
	exit 1
fi
