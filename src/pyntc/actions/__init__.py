"""Actions: definizione delle azioni sulle costruzioni (NTC18 Cap. 2-3).

Moduli a monte del solutore FEM.
"""

from pyntc.actions.loads import (
    area_reduction_factor,
    floor_reduction_factor,
    partition_equivalent_load,
    unit_weight,
    variable_load,
)
from pyntc.actions.wind import (
    wind_base_velocity,
    wind_exposure_coefficient,
    wind_friction_action,
    wind_kinetic_pressure,
    wind_pressure,
    wind_reference_velocity,
    wind_return_coefficient,
)
from pyntc.actions.snow import (
    snow_exposure_coefficient,
    snow_ground_load,
    snow_roof_load,
    snow_shape_coefficient,
)
from pyntc.actions.seismic import (
    elastic_response_spectrum,
    seismic_damping_factor,
    seismic_return_period,
    seismic_soil_amplification,
    seismic_topographic_amplification,
)
from pyntc.actions.temperature import (
    temperature_extremes,
    temperature_solar_increment,
    temperature_uniform_variation,
)
from pyntc.actions.fire import (
    explosion_equivalent_pressure,
    fire_design_load,
    fire_external_curve,
    fire_hydrocarbon_curve,
    fire_standard_curve,
    impact_forklift_force,
    impact_vehicle_force,
)
from pyntc.actions.combinations import (
    combination_coefficients,
    exceptional_combination,
    partial_safety_factors,
    seismic_combination,
    seismic_masses,
    sle_characteristic_combination,
    sle_frequent_combination,
    sle_quasi_permanent_combination,
    slu_combination,
)
