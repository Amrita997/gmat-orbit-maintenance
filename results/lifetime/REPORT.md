# GMAT mission results

Native GMAT truth propagation and native GMAT controller/actuator logic. Mean elements use GMAT BrouwerShort. This is an independent educational example, not a validated model of a commercial propulsion product.

| Controller | Atmosphere | End day | Fuel (kg) | Fuel-out day | Fueled altitude RMS (m) | Fueled max e | Fueled min perigee (km) | Fueled criteria pass |
|---|---|---:|---:|---:|---:|---:|---:|---|
| none | MSISE90 | 34.76 | 0.000000 | — | 41346.0 | 0.000553 | 198.477 | no |
| eccentricity | MSISE90 | 43.33 | 0.277000 | 8.31 | 81.7 | 0.000070 | 299.439 | yes |

## Paired lifetime estimate

* eccentricity: 8.564 additional days to the common 200 km geodetic endpoint; 30.916 days per kg consumed.

The endpoint is a study boundary, not reentry. Maintenance accuracy is assessed separately while fuel is available. The uncontrolled spacecraft starts at the same 30 kg wet mass and retains its unused fuel. Criteria: ≥95% time in mean 300±1 km, e≤0.0005 and mean perigee≥295 km. Thermal/navigation assumptions require hardware calibration.

Mass flow is integrated independently of the GMAT tank; accepted tank states and electrical energy are audited. AllowNegativeFuelMass permits internal integrator trial stages only; commanded hot duration is limited by actual remaining fuel.
