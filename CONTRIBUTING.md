# Contributing

Open an issue with a reproducible case before a substantial model change. State GMAT version, Python version, weather-file SHA-256, seed, controller and duration. Include numerical results and units. Keep generated local paths, logs, binaries and private hardware information out of commits. Document which parameters are measured, published or assumed. Avoid presenting synthetic navigation or thermal behavior as hardware validation.

Run `python -m pytest -q` for compiler/unit checks. GMAT integration studies run separately with a local installation and weather file; unit tests alone do not validate the physics.
