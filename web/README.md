# VentureLens web app

The browser front end for VentureLens. It turns a founder's domain preferences and a fixed budget into an explainable angel-investment plan, using named YC companies, transparent proxy scores and explicit capital limits.

## Run locally

It's a static site with no build step. From the repo root:

```
python -m http.server 8000 --directory web
```

Then open http://localhost:8000.

## Files

- `index.html`: page shell
- `app.mjs`: the app (views, state, rendering)
- `engine.mjs`: scoring and filtering logic
- `pages.mjs`, `icons.mjs`: copy and icons
- `styles.css`: styles
- `data/model.json`: the YC model snapshot the app loads

The optional live research refresh (`/api/research`, `/api/status`) needs a Python backend that isn't in this folder. Without it the app runs on the bundled snapshot.
