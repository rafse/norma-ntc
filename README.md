# pyntc

Python library for structural verification according to NTC 2018 (Italian Building Code, D.M. 17/01/2018).

> **Disclaimer**: This library does not replace the professional judgement of the structural engineer. Final verification is the responsibility of the designer.

## Installation

```bash
pip install norma-ntc
```

## Quick start

```python
from pyntc.actions.loads import unit_weight, variable_load, partition_equivalent_load
from pyntc.actions.wind import (
    wind_base_velocity,
    wind_reference_velocity,
    wind_kinetic_pressure,
    wind_exposure_coefficient,
    wind_pressure,
)

# --- Carichi (NTC18 §3.1) ---
gamma = unit_weight("calcestruzzo_armato")          # 25.0 kN/m³
qk, Qk, Hk = variable_load("A")                    # (2.0, 2.0, 1.0)
g2 = partition_equivalent_load(1.5)                  # 0.80 kN/m²

# --- Vento (NTC18 §3.3) ---
v_b = wind_base_velocity(zone=3, altitude=600)       # 29.00 m/s
v_r = wind_reference_velocity(3, 600, 50)            # 29.02 m/s
q_b = wind_kinetic_pressure(v_r)                     # 0.526 kN/m²
c_e = wind_exposure_coefficient(z=15, exposure_category=3)  # 2.407
p   = wind_pressure(q_b, c_e, c_p=0.8)              # 1.014 kN/m²
```

## Modules

### Actions (NTC18 Cap. 2-3) — input to the solver

| Module | Section | Description |
|--------|---------|-------------|
| `actions.loads` | §3.1 | Dead loads, partitions, variable loads, reduction factors |
| `actions.wind` | §3.3 | Base velocity, return coefficient, kinetic pressure, exposure, wind pressure |
| `actions.snow` | §3.4 | Ground load, shape/exposure coefficients, roof load |
| `actions.seismic` | §3.2 | Return period, damping, soil/topographic amplification, elastic response spectrum |
| `actions.temperature` | §3.5 | Temperature extremes, solar increment, uniform variation |
| `actions.fire` | §3.6 | Standard/hydrocarbon/external curves, design load, explosion, impact |
| `actions.combinations` | §2.5.3 | ψ coefficients, γ factors, SLU/SLE/seismic/exceptional combinations, seismic masses |

### Checks (NTC18 Cap. 4-8) — verification of solver output

| Module | Section | Description |
|--------|---------|-------------|
| `checks.concrete` | §4.1 | R.C. design strengths, strain limits, shear/torsion resistance, biaxial bending |
| `checks.steel` | §4.2 | Steel grade properties, section resistance (N/M/V), buckling, bolts, welds |
| `checks.composite` | §4.3 | Composite steel-concrete: effective width, studs, columns, beams |
| `checks.timber` | §4.4 | Timber: k_mod/k_def, design strength, bending/shear/torsion, beam/column stability |
| `checks.masonry` | §4.5 | Masonry: partial factors, slenderness, eccentricity, simplified check |
| `checks.bridges` | Cap. 5 | Bridge load schemes (road/rail), dynamic coefficients, braking/centrifugal forces |
| `checks.geotechnical` | Cap. 6 | Geotechnical: partial factors, piles, anchors, retaining walls, embankments |
| `checks.seismic_design` | Cap. 7 | Seismic design: behaviour factor, modal combination, capacity design |
| `checks.existing_buildings` | Cap. 8 | Existing buildings: confidence factors, safety ratios, adequacy checks |

## Design principles

- **External solver**: pyntc produces input (actions) and verifies output (checks) — it is NOT a FEM solver
- **Traceability**: every public function is decorated with `@ntc_ref(article=..., table=..., formula=...)` linking back to NTC18
- **SI units**: all quantities in SI, documented in docstrings between `[]`
- **Minimal dependencies**: only `numpy` (core) and `scipy` (optional)

## Development

```bash
pip install -e ".[dev]"
pytest -v
pytest --cov=pyntc
```

## License

MIT
