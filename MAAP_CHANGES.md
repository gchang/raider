# Changes from upstream

Upstream: https://github.com/dbekaert/RAiDER, tag `v0.6.0` at commit 64b57ac79953de968e887cf0f26690f1bc44ce6b (2025-09-09, also `main`), by David Bekaert, Jeremy Maurer, Piyush Agram, Simran Sangha, Brett Buzzanga and the other RAiDER contributors (JPL). Apache License 2.0 (`LICENSE`), with the Caltech copyright notice in `LICENSE2.md`. Both are kept unchanged.

This copy starts from upstream's file tree at 64b57ac without its git history. It is unchanged except for the items below. `.github/` was left out (GitHub workflows, issue and pull request templates, dependabot config); `.circleci/` is kept.

## 2026-10-25: full-level pressure in calcgeoh (results change for ERA5, ERA5T and HRES)

`tools/RAiDER/utilFcns.py`, `calcgeoh`: ECMWF hybrid coordinates define pressure on half levels, and the pressure of a full level is the mean of the two half levels around it. The function returned only the half level above (`p[idx_level] = ph_lev`, with the averaging commented out) but paired it with the full-level geopotential height. Every level got a pressure from about half a model layer higher, so the hydrostatic delay from model-level weather models was too low.

Changed to `p[idx_level] = (ph_lev + ph_levplusone) / 2`, backported from upstream commit d1d13ed0fb398d0b39c7ac638eb2c4193c49af19 (code change only; it is on upstream's development branch and not yet in a release).

**Results change** for the weather models that load ECMWF model levels through `calcgeoh`: ERA5, ERA5T and HRES (model levels are their default; their pressure-level option does not change). On an HRES case (2024-02-15 12 UTC, 26-34N 81-89E, Ganges plain to Tibet) the zenith hydrostatic delay at 0 m goes up by 28.4 mm on average (20.5 to 42.7 mm per cell) and by 24.7 mm at 4.9 km. Against the Saastamoinen closed form at each model column's surface it was 31.6 mm low and is now 1.4 mm high (RMS 1.5 mm), with no ramp against terrain height. The wet delay goes up by 0.3 mm on average. HRRR, HRRR-AK, GMAO, MERRA2, NCMR and WRF do not use `calcgeoh` and give the same results as before; so does the ARIA GUNW path with HRRR.

## 2026-10-25: calcDelays.py and calcDelaysGUNW.py exit 0 after a successful run

The two console scripts pointed straight at `calcDelays` and `calcDelaysGUNW` in `tools/RAiDER/cli/raider.py`. Those functions return their outputs (the list of delay files, and the GUNW delay dataset) for use from Python. A console script passes the return value to `sys.exit()`, which treats anything other than `None` or an integer as an error message, so after a correct run the scripts printed the file list or the whole dataset to stderr and exited with status 1. A batch system then marks a good run as failed. `raider.py` (including `raider.py ++process calcDelaysGUNW`) was not affected, because it discards the return value.

`pyproject.toml` now points `calcDelays.py` and `calcDelaysGUNW.py` at two small wrappers, `calcDelays_cli` and `calcDelaysGUNW_cli`, which call the same functions and return `None`. The Python functions and what they return are unchanged, and errors still raise and exit non-zero. Results do not change. An existing editable install needs `python -m pip install -e .` again to regenerate the scripts.

## Check

On 2026-10-25, Linux x86-64, in a fresh conda env built from the linux-64 packages of `conda-lock.yml` (the same set `conda-lock install` gives: Python 3.13.5, numpy 2.3.2, pandas 2.2.3, xarray 2025.8.0, isce3 0.24.4), then `python -m pip install -e .`:

- `pytest -m "not long" test/`: 405 passed, 2 failed, 11 skipped, 20 deselected, the same as v0.6.0. Both failures are downloads from the UNR GNSS archive, whose URL now returns 404.
- `calcDelaysGUNW.py -f <copy of S1-GUNW-D-R-071-tops-20250918_20250226-135250-00119W_00032N-PP-d799-v3_0_1.nc> -m HRRR -o .` rewrote the four HRRR troposphere layers. They match the layers in the official ARIA product (RAiDER 0.5.5) in all 52,000 cells of each layer, within 0.0003 mm. About 8.5 minutes and 4.0 GB peak memory, most of it downloading HRRR from AWS.
- The HRES case above, run from a staged HRES model-level file, gave the numbers in the section above. Running HRES at all also needed local changes that are not part of this copy (the time-zone comparison in `models/hres.py` and the surface geopotential level in `models/ecmwf.py`).

Check for the exit status, 2026-10-25, same environment from a fresh clone:

- `calcDelaysGUNW.py -f <copy of the GUNW> -m HRRR -o .` and `raider.py ++process calcDelaysGUNW -f <another copy> -m HRRR -o .` both exit 0 (about 8.3 minutes and 4.0 GB peak each), and both sets of layers match the official product as above (within 0.0003 mm in every cell).
- `calcDelays.py test/scenario_1/raider_example_1.yaml` exits 0 and gives the test's expected values (hydrostatic 2.2622863 m, wet 0.0361021 m at -91.84, 36.84, 0 m).
- Failures still exit 1: a missing GUNW file (`calcDelaysGUNW.py` and `raider.py ++process calcDelaysGUNW`), a missing run config (`calcDelays.py` and `raider.py`), and the scenario_1 example with no network ("Weather model processing failed for all times").
- `pytest -m "not long" test/`: 405 passed, 2 failed (the UNR downloads), 11 skipped, 20 deselected, as before.
