# CONTRIBUTING

Thanks for your interest in AeonMosaic! This document covers the
contribution workflow, code style, and testing requirements.

## Code style

- Python 3.9+ (target versions: 3.9, 3.10, 3.11, 3.12)
- Line length: 100 chars (`black` default)
- Type hints: required on public APIs, optional on internals
- Docstrings: triple-quoted, Google-style, on every public class/method

Run the linters locally:

```bash
black aeon_embodiment tests scripts
flake8 aeon_embodiment tests scripts
mypy aeon_embodiment
```

## Testing

All PRs must keep the test suite green:

```bash
pytest tests/ -v
```

Coverage is not enforced, but new features should add tests. Aim for
≥80% line coverage on new code.

```bash
pytest tests/ --cov=aeon_embodiment --cov-report=term-missing
```

## Hardware-agnostic principle

Every class that touches hardware must accept an injected adapter —
**never import GPIO / I2C / SPI / CSI libraries directly in the core
classes**. This keeps the entire stack runnable on a developer laptop
and CI without any hardware attached.

✅ Good:

```python
class HybridMobilityController:
    def __init__(self, pwm_sink: Optional[PWMSink] = None, ...):
        self._pwm = pwm_sink or _noop_pwm
```

❌ Bad:

```python
import pigpio
class HybridMobilityController:
    def __init__(self):
        self._pi = pigpio.pi()  # breaks on dev machines without pigpio
```

## Config discipline

- **No hard-coded numerics** in runtime code paths. Every tunable
  value lives in `configs/*.json`.
- The `Config` class is the single source of truth — never read JSON
  directly in feature code.
- New config keys must be added to the corresponding manifest with a
  sensible default.

## Adding a new enhancement

1. Add a row to `_BLUEPRINT_REGISTRY` in
   `aeon_embodiment/enhancements/__init__.py` with the canonical
   composite score, tier, target subsystem, and priority.
2. Add the corresponding test in `tests/test_enhancements.py` (or just
   bump the count assertions if adding in bulk).
3. Update `docs/ENHANCEMENTS.md` with the new row.

## Adding a new Sophia equation

1. Add the equation tuple to `_build_registry()` in
   `aeon_embodiment/sophia/__init__.py`.
2. Write a numeric evaluator function `_eqN_xxx(**kwargs) -> float`.
3. Add a test in `tests/test_sophia.py` that checks the evaluator's
   basic behaviour (returns a float, no NaN, monotonicity where applicable).
4. Update `docs/EQUATIONS.md` with the LaTeX form and operational meaning.

## Adding a new alignment formula

1. Add the formula to `_build_registry()` in
   `aeon_embodiment/alignment/__init__.py` with a SymPy expression
   and a numeric evaluator.
2. Add a test in `tests/test_alignment.py`.
3. Update `docs/USAGE.md` if the formula's evaluator accepts new kwargs.

## Pull request workflow

1. Fork the repo and create a feature branch.
2. Write tests for your changes.
3. Run `pytest tests/ -v` and ensure all tests pass.
4. Run `black`, `flake8`, `mypy` on your changes.
5. Open a PR with a clear description and link to any related issues.

## Release process

1. Bump `__version__` in `aeon_embodiment/__init__.py` (semver).
2. Update `pyproject.toml` version to match.
3. Update `CHANGELOG.md` (TODO — not yet present in v0.2).
4. Tag the release: `git tag v0.X.Y && git push --tags`.
5. Build the wheel: `python -m build`.
6. Upload to PyPI: `twine upload dist/*` (only for stable releases).

## Code of conduct

Be excellent to each other. Disagreements about Gnostic metaphysics or
the Sophia Constant are welcome but must remain respectful and grounded
in the blueprint.

## License

By contributing, you agree that your contributions will be licensed
under the MIT License (see `LICENSE`).
