# Empire City 1924 — a Prohibition-era game sandbox

The playable, web-based build of a 1920s GTA-style game. Everything runs in the
browser with **no install and no build step** — each game is a single self-contained
HTML file using Three.js (WebGL). Stylized noir, not photoreal (that path needs a real
engine like Unreal); this is the version you can actually open and play anywhere.

## Play

Open **`index.html`** in a modern browser and pick a game — or open either file directly.
(For best results run a tiny local server so everything loads cleanly:
`python -m http.server` then visit `http://localhost:8000`.)

### `empire-city.html` — open world
A two-borough city split by a river and a bridge. On foot or in a car.
- **WASD / arrows** move / drive · **Shift** run
- **E** steal / exit a car · **V** first-person cockpit (steering wheel) / chase cam
- **B** buy a Tommy gun at the gun shop · **click / Space** fire
- Live traffic, pedestrians, a wanted system, pursuing cops, and a BUSTED loop.

### `speakeasy-shootout.html` — first-person slice
The tight, polished vertical slice: breach a speakeasy and clear the room.
- **WASD** move · **mouse** aim · **click / Space** fire · **R** reload
- Five rival gangsters who shoot back, a health bar, win/lose states.

### `early-versions/`
The build history — the first 3D scene and the first playable prototype — kept for reference.

## Tech

- **Three.js r128** (loaded from CDN), pure WebGL, no framework, no bundler.
- Procedural geometry (no external 3D assets), custom controllers, custom camera rigs,
  raycast shooting, simple NPC/vehicle AI, a minimap, and a HUD — all in one file each.

## Roadmap

- Smarter enemy AI + cover; reload/hit animations; more weight to the gunplay.
- Missions (bootleg deliveries), roadblocks, meaner cops.
- The photoreal version lives in Unreal Engine — this repo is the design/gameplay blueprint it gets rebuilt from.

## License

MIT.
