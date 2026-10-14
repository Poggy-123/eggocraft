# Eggocraft

A personal copy of [EaglercraftX 1.8](https://github.com/Eaglercraft-Archive/EaglercraftX-1_8-workspace) (Minecraft 1.8 in the browser), tuned for an Intel N100 mini PC and hosted on Cloudflare Pages.

**Play:** the Cloudflare Pages address, normally https://eggocraft.pages.dev

## How it works

This repo doesn't store the game's source. On every push to `main`, the [Build and publish](.github/workflows/publish.yml) workflow:

1. downloads the EaglercraftX workspace at a fixed commit (`u53`, set in [build.sh](build.sh)),
2. applies the changes in [optimize.py](optimize.py),
3. compiles the WASM-GC and JavaScript clients,
4. commits them, along with the pages in [site/](site), to the `site` branch.

Cloudflare Pages watches the `site` branch and puts each new version online. You can also start a rebuild by hand from the Actions tab ("Build and publish" → "Run workflow").

### One-time Cloudflare setup

Do this once the first workflow run has finished and the `site` branch exists:

1. Sign up or log in at https://dash.cloudflare.com (free plan).
2. Go to **Workers & Pages → Create → Pages → Connect to Git**, connect your GitHub account, and pick the `eggocraft` repo.
3. Set **Production branch** to `site`, **Framework preset** to "None", and leave **Build command** and **Build output directory** empty.
4. Click **Save and Deploy**. Cloudflare shows the site's `*.pages.dev` address when it's done.

## What's tuned for the N100

The N100 has four efficiency cores and a small integrated GPU, so the changes aim to save CPU time per frame and GPU fill rate:

- **WASM-GC client by default.** The start page opens the WebAssembly (WASM-GC) build when the browser supports it, because upstream measures it at around 50% more FPS and TPS than the JavaScript build. That needs Chrome or Edge 137 or newer. Other browsers get the JavaScript build. Add `?client=js` or `?client=wasm` to the URL to pick one yourself.
- **Release compiler settings for the JavaScript client.** TeaVM optimization is set to `AGGRESSIVE` instead of `BALANCED`, and source maps are turned off.
- **Lighter first-run video settings:** clouds off, particles on "Decreased", connected textures and custom skies off, and a 60 FPS cap for when VSync is off. VSync stays on, render distance stays at 4 chunks, and graphics stay on "Fast". These are only the defaults for a fresh install; anything you change in-game is saved and kept.

## Tips for playing on the N100

- Use Chrome or Edge with hardware acceleration on (Settings → System).
- Leave VSync on. Without it the game runs "too fast" for the browser and input starts to lag.
- If it runs smoothly, try render distance 6. Eaglercraft shows a performance warning above that.
- Shaders and dynamic lights are heavy for an integrated GPU; turn them on only if FPS allows.
- Worlds are saved in your browser's storage for this site. To keep a copy, select the world, click **Backup**, then **Export EPK File**.

## Building locally

Needs Java 17 and Python 3. Run `./build.sh`; the site ends up in `build/site`. Serve that folder over HTTP (for example `python3 -m http.server -d build/site`), since the game won't run from `file://`.
