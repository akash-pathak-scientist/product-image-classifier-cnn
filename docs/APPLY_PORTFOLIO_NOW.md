# 🚀 Apply Data Scientist Planet to Live Portfolio — 30 seconds

Your immersive planet is **100% ready** in this branch. Bot built it locally (`/tmp/portfolio` commits `9b92e61` + `ce14389`) and saved it here, but GitHub blocks the bot from pushing to `akash-pathak-scientist.github.io` (push:false — `git push` → 403, `gh api PATCH` → 403, `fork` → 403). **You** (owner) can push with 1 copy.

All settings already inside the file:
- ✅ Real email `akashpathak.in@gmail.com` ×3 (no fake `akash.pathak@email.com`)
- ✅ `Clean, Portfolio-Ready Code` (not "Production-Grade")
- ✅ Data honesty labels per project: P01 simulated FinTech 15k, P02 real fraud 50k, P03 simulated retail 50k/200k, P04 simulated finance 24mo, P05 simulated crypto 500k/$2.33B, P07 20,754 real images
- ✅ P07 CNN flagship linked in footer + hero Planet Status card `91.71% test n=3,114`
- ✅ Virtual world: cosmos dual-canvas (220 stars + nebula), planet sphere + 2 rings + 3 orbiting data nodes, glass HUD nav, holographic planet-cards with 3D tilt + parallax

---

## Option A — No CLI · GitHub Web (fastest, 30 sec)

1. Download this file: `docs/portfolio_index_planet.html` from this branch (or open it in viewer → Select All → Copy)
2. Go to **https://github.com/akash-pathak-scientist/akash-pathak-scientist.github.io**
3. Click `index.html` → ✏️ **Edit** (pencil) → `Ctrl+A` → `Ctrl+V` (paste the 63KB) → **Commit changes** → **Commit directly to main**
4. Wait 45 sec → verify https://akash-pathak-scientist.github.io

## Option B — One CLI command (if you have git)

```bash
git clone https://github.com/akash-pathak-scientist/akash-pathak-scientist.github.io.git /tmp/live-portfolio
cp product-image-classifier-cnn/docs/portfolio_index_planet.html /tmp/live-portfolio/index.html
cd /tmp/live-portfolio && git add index.html && git commit -m "feat: Data Scientist Planet — immersive virtual-world portfolio" && git push
# will prompt for your GitHub token — bot cannot reuse its token here
```

Or patch variant:
```bash
git clone https://github.com/akash-pathak-scientist/akash-pathak-scientist.github.io.git
cd akash-pathak-scientist.github.io
git apply ../product-image-classifier-cnn/docs/portfolio_planet_redesign.patch
git add index.html && git commit -m "feat: Data Scientist Planet — immersive virtual-world portfolio" && git push
```

## Option C — After you push portfolio, also fix Profile → Website

Bot cannot PATCH `user.blog`/`repo.homepage` (403). Do manually (10 sec):

GitHub → avatar → **Settings → Profile → Website** → set to `https://akash-pathak-scientist.github.io` → Save

And (if not done) **Settings → Repositories → Customize your pins** → pin 6: `product-image-classifier-cnn`, `fintech-transaction-analytics`, `credit-card-fraud-detection`, `customer-sales-analytics`, `finance-mis-dashboard`, `careerpilot-ai`

---

## Verify live

- `curl -s https://akash-pathak-scientist.github.io | grep -c "Data Scientist Planet"` should be 5+
- Search page for `akashpathak.in@gmail.com` → 3 hits, no `akash.pathak@email.com`
