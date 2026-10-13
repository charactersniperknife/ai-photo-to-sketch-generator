# Contributing to ai-photo-to-sketch-generator

Thanks for wanting to help sharpen the pipeline. This project turns ordinary
photos into clean pencil / ink / charcoal sketches using a stack of classical
edge-detection passes plus a learned line-refinement model. Contributions are
welcome from photographers, illustrators, and anyone who likes staring at
Laplacian kernels at 2 a.m.

## Ground rules

1. **One feature per PR.** A new sketch style, a new pre-processing step, or a
   new export target — not all three in one branch.
2. **Every new style ships with a golden image test.** Drop the source photo
   into `tests/fixtures/photos/` and the expected output into
   `tests/fixtures/sketches/`. CI diffs against a PSNR threshold, not pixel
   equality.
3. **No model weights in git.** Weights live on the release page or the model
   hub. `models/checkpoints/` is gitignored on purpose.
4. **Type hints everywhere.** This repo runs `mypy --strict` on
   `sketchforge/`. If your contribution doesn't type-check, it doesn't merge.
5. **Formatting is `black` + `isort`.** Pre-commit hooks are configured; run
   `pre-commit install` once after cloning.

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
pre-commit install
pytest -q
```

## Adding a new sketch style

1. Create `sketchforge/styles/<your_style>.py` subclassing `BaseSketchStyle`.
2. Register it in `sketchforge/styles/__init__.py` inside `STYLE_REGISTRY`.
3. Add a config block in `config/default.yaml` under `styles:`.
4. Add CLI exposure in `sketchforge/cli/convert.py` if it needs new flags.
5. Wire a golden test in `tests/test_style_rendering.py`.

## Commit style

Conventional Commits. `feat(styles): add crosshatch pencil pass`,
`fix(io): handle CMYK JPEGs without crashing`, `docs: clarify GPU fallback`.

## Reporting bugs

Open an issue with: OS + Python version, the style used, the input photo
resolution, and the exact command you ran. Attach the input if you can — it
makes reproduction ten minutes instead of two days.