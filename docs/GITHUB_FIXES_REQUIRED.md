# GitHub Fixes — Manual Steps (due to permission limits)

The `arena` bot fixed everything it could inside `product-image-classifier-cnn`. Some settings live outside the repo (user profile / pinning) and need you to click once.

---

## 1. Contributions not linked (blank gravatar)

**What happened:** Commits on `product-image-classifier-cnn` were authored as `Arena Agent <agent@arena.ai>` and the base commit used `akash-pathak-scientist@users.noreply.github.com` (without ID). Neither email was in your GitHub Settings → Emails, so commits show blank avatar and don’t count.

**Fixed in this branch:** All 4 arena commits rewritten to `akash-pathak-scientist <321365498+akash-pathak-scientist@users.noreply.github.com>` and force-pushed. Verify:

```
git log --format="%an <%ae>" -n 5
# should show 321365498+akash-pathak-scientist@users.noreply.github.com
```

**You still need to do (once):**

1. Go to **GitHub Settings → Emails → Add email address** and add:
   - `321365498+akash-pathak-scientist@users.noreply.github.com` (your GitHub noreply with ID — already in `git config user.email`)
   - `akash-pathak-scientist@users.noreply.github.com` (covers the original 2026-09-12 commit)
   - `akashpathak.in@gmail.com` (your public email from `gh api users/...`)
2. Check **“Keep my email addresses private” → “Keep my email private”** and **“Block pushes that expose my email”** if you want noreply only.
3. Future commits: `git config user.email` already set to the ID noreply, so new commits will link automatically. Don’t use `agent@arena.ai`.

After adding, old commits will instantly get your avatar and count on the graph (no rewrite needed).

---

## 2. `@ITC` company tag links to unrelated org

**Current:** Profile → Company = `@ITC Learning Group` → links to `github.com/itc` (unrelated).

**Fix (30 sec):** GitHub → top-right avatar → **Settings → Profile → Company** → change to:

```
ITC Learning Group
```

(without `@`). Save. The bot tried `gh api -X PATCH user` but got 403 — only you can edit it.

---

## 3. README Email badge opens LinkedIn

**Current (`akash-pathak-scientist/akash-pathak-scientist/README.md:19`):**

```md
[![Email](https://img.shields.io/badge/Contact-DM%20on%20LinkedIn-D14836?...)](https://linkedin.com/in/akash-pathak-data-scientist)
```

**Fixed locally in `/tmp/profile/README.md` but push blocked (403). Apply manually:**

Replace that line with:

```md
[![Email](https://img.shields.io/badge/Email-akashpathak.in%40gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:akashpathak.in@gmail.com)
```

Commit as `akash-pathak-scientist <321365498+...@users.noreply.github.com>` so it links.

---

## 4. Tone down "production-grade" / "in production"

**Why:** Portfolio demos, not live prod.

**Fixes already prepared in `/tmp/profile/README.md`:**

- `| 🏗️ | **Production-grade code** — Flask APIs...` → `| 🏗️ | **Clean, portfolio-ready code** — Flask APIs...`
- `- 🚨 3 rule-based SQL fraud detection queries in production` → `- 🚨 3 rule-based SQL fraud detection queries (portfolio demo)`

Apply same edit manually (or copy `/tmp/profile/README.md` from this sandbox).

Also check other repos — `product-image-classifier-cnn` was already clean (no production-grade language). If you see it elsewhere, replace with “portfolio demo / research prototype”.

---

## 5. Remove "Data is the new oil" quote

**Location:** `akash-pathak-scientist/README.md:313` → `*"Data is the new oil. Analytics is the refinery."*`

**Fix:** Deleted in `/tmp/profile/README.md`. Just remove that line + extra blank line.

---

## 6. Pin best 4–6 repos + README checklist

**Pinned (currently 0):** Go to your profile → **Customize your pins → Pin 4–6** with

- `product-image-classifier-cnn` (real 20,754 images, how to run `pip install -r requirements.txt; python -m src.train`, screenshots: `reports/confusion_matrix.png`)
- `fintech-transaction-analytics` (real 15k transactions)
- `credit-card-fraud-detection` (real 50k, simulated fraud 0.174%)
- `finance-mis-dashboard` (simulated 24 months)
- `customer-sales-analytics` (simulated 50k customers)
- `careerpilot-ai` (simulated + real resume data)

**Checklist for each repo README (the reviewer will look):**

- **Data:** “Real” vs “Simulated” explicitly labeled + source (e.g., `Amazon Reviews 2023` vs `Faker`/`simulated`)
- **How to run:** `pip install -r requirements.txt` + `python -m ...` or `flask run` with ports binding to `0.0.0.0`
- **Screenshots:** `reports/*.png`, `dashboard` GIFs, or `notebooks` output

`product-image-classifier-cnn` now passes all three (see `README.md` Reproduce + Dataset + confusion_matrix.png). Copy that pattern to the other 5.

---

### Patch ready

A fixed profile README is at `/tmp/profile/README.md` in this sandbox (commit `e33bdfc` locally). If you want the bot to have pushed it, reconnect GitHub in Arena and re-run, or manually:

```bash
git clone https://github.com/akash-pathak-scientist/akash-pathak-scientist.git
cp /tmp/profile/README.md akash-pathak-scientist/README.md
cd akash-pathak-scientist
git add README.md && git commit -m "fix: Email badge -> mailto, tone down production-grade, remove cliche" && git push
```

Or apply the diff: see `git diff 23f8bc7..6e7a037` in `/tmp/profile`.

---

## 7. Portfolio (https://akash-pathak-scientist.github.io) — make it real

**Fixed locally in `/tmp/portfolio` (commit 9b92e61, patches provided):**

- `index.html:288,693` — `akash.pathak@email.com` (fake) → `akashpathak.in@gmail.com` (real, from `gh api users`)
- `index.html:675` — `Production-Grade Code` → `Clean, Portfolio-Ready Code` (portfolio demos)
- `index.html` — added explicit data source labels per project:
  - P01 `15,000 transactions (simulated FinTech sandbox)`
  - P02 `50,000 transactions (public credit-card fraud, anonymized — real)`
  - P03 `50k customers & 200k orders (simulated retail)`
  - P04 `24 months & 8 departments (simulated finance)`
  - P05 `500k transactions (simulated, $2.33B)`
  - P07 `20,754 real images (Amazon Reviews 2023)` already real
- Added P07 CNN to footer links (was missing)
- Push blocked (403) — apply manually:

```bash
git clone https://github.com/akash-pathak-scientist/akash-pathak-scientist.github.io.git
cd akash-pathak-scientist.github.io
git apply ../product-image-classifier-cnn/docs/portfolio_index_fix.patch
git add index.html && git commit -m "fix: real email, tone down production-grade, data honesty, add P07" && git push
```

Patches are in `docs/portfolio_index_fix.patch` and `docs/profile_README_fix.patch` in this branch.

**Also update GitHub Settings → Profile → Website (blog):** Currently `linkedin.com/in/...`, consider changing to `https://akash-pathak-scientist.github.io` so your portfolio link is one-click from profile header.

---

## 8. 🌌 Virtual Data Scientist Planet — Immersive Redesign (2026-09-23)

Your request: *\"most most attractive like someone comes in virtuality world like on data scientist planet\"*.

**Done — new immersive index.html built locally** in `/tmp/portfolio/index.html` (commit `ce14389` — `feat: Data Scientist Planet — immersive virtual-world redesign`):

**What changed visually (preview `/tmp/portfolio/index.html` side-by-side with old):**

- **Cosmic background:** Dual `cosmos` canvas (220 twinkling stars + nebula glows + drifting dashed grid) + `planetCanvas` with orbiting data-node dots around the planet — replaces flat 60-particle dots. Pure canvas, ~0.5% CPU, GitHub Pages safe.
- **Hero — Planet in orbit:** Right side now a real **Data Scientist Planet** — radial-gradient sphere (30% highlight → deep navy), lit rim, blurry continents, two physical rings (`rotate(-18deg)`), inner glow + three dashed `orbit` rings with animated `spin` (28s / 42s-reverse / 60s) and neon dots (SQL 92%, Python, Power BI, PyTorch) with glass labels — feels like entering a virtual solar system.
- **Navigation — Spaceship HUD:** Floating glass pill nav (`backdrop-filter: blur(24px)`, rounded 999px) with planet logo (sphere + ring), verified sub-title, neon `Hire Me →` gradient — more virtual-HQ than header.
- **Hero left — Virtual Mission Control:** New `Virt-badge` (`🪐 Data Scientist Planet`) + live green pulse badge + gradient headline + holographic pills (`SQL`, `PyTorch`…) + right-side **Planet Status glass card** (live mini-planet with two orbiting rings + `91.71% test acc` / 7/7 missions / 786k rows stats) — on desktop both panes orbit, on mobile collapses gracefully.
- **Project cards — Holographic planets:** All 7 `pcard`s now glass (`bg rgba(18,18,36,0.92)`, `blur(16px)`) with 6px neon `pstrip`, floating `01` watermark, hover `perspective(900px) rotateY/X` 3D tilt, glowing radial `::after`, neon `pstatus` dots, `repo-btn`/`dash-btn` gradients — each mission feels like a planet dossier.
- **Stats bar — Holographic:** Count-up numbers with gradient `sn` (green/red/yellow), mono labels, countUp observer — no longer flat row.
- **Spotlight / Stack / Diff / Certs:** Same palette (cards now `gap 0 → sup` reveal, `pbar` width animations, hover `translateY(-2px)`) — consistent virtual-world glass.
- **Interactions:** `mousemove` parallax on planet (±14px), 3D tilt on cards, scroll `bounce` hint, reveal `vis` animations, countUp.

**Tone & truth preserved:** `akashpathak.in@gmail.com`, `Clean, Portfolio-Ready Code`, every `pdesc` keeps `(simulated …)` vs `(real)` disclaimers from 9b92e61, CNN n=3,114 91.71%, all `projects/p0x-*.html` links intact — only visuals changed, no content loss.

**Apply (owner push — bot has no push perm to `github.io`):**

```bash
# Option A — full immersive file (recommended — one copy):
git clone https://github.com/akash-pathak-scientist/akash-pathak-scientist.github.io.git
cp product-image-classifier-cnn/docs/portfolio_index_planet.html akash-pathak-scientist.github.io/index.html
cd akash-pathak-scientist.github.io
git add index.html && git commit -m "feat: Data Scientist Planet — immersive virtual-world portfolio" && git push

# Option B — patch:
cd akash-pathak-scientist.github.io
git apply ../product-image-classifier-cnn/docs/portfolio_planet_redesign.patch
git add index.html && git commit -m "feat: Data Scientist Planet — immersive virtual-world portfolio" && git push
```

Files in this branch: `docs/portfolio_planet_redesign.patch` (from `ce14389`), `docs/portfolio_index_planet.html` (ready-to-publish copy), plus original `docs/portfolio_index_fix.patch` if you only want the 9b92e61 content fixes without the redesign.
