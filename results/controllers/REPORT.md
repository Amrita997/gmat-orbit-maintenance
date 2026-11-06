# GMAT mission results

Native GMAT truth propagation and native GMAT controller/actuator logic. Mean elements use GMAT BrouwerShort. This is an independent educational example, not a validated model of a commercial propulsion product.

| Controller | Atmosphere | End day | Fuel (kg) | Fuel-out day | Fueled altitude RMS (m) | Fueled max e | Fueled min perigee (km) | Fueled criteria pass |
|---|---|---:|---:|---:|---:|---:|---:|---|
| none | MSISE90 | 2.00 | 0.000000 | — | 1355.8 | 0.000044 | 297.302 | no |
| deadband | MSISE90 | 2.00 | 0.057867 | — | 618.9 | 0.000109 | 298.897 | no |
| periodic | MSISE90 | 2.00 | 0.039017 | — | 573.7 | 0.000188 | 297.833 | yes |
| feedforward_pi | MSISE90 | 2.00 | 0.060708 | — | 103.6 | 0.000060 | 299.525 | yes |
| adaptive_deadband | MSISE90 | 2.00 | 0.057549 | — | 621.1 | 0.000101 | 298.897 | no |
| eccentricity | MSISE90 | 2.00 | 0.064982 | — | 88.7 | 0.000061 | 299.439 | yes |

## Paired lifetime estimate

* Baseline lifetime is censored; extend the horizon to estimate total extension.
* Baseline lifetime is censored; extend the horizon to estimate total extension.
* Baseline lifetime is censored; extend the horizon to estimate total extension.
* Baseline lifetime is censored; extend the horizon to estimate total extension.
* Baseline lifetime is censored; extend the horizon to estimate total extension.

The endpoint is a study boundary, not reentry. Maintenance accuracy is assessed separately while fuel is available. The uncontrolled spacecraft starts at the same 30 kg wet mass and retains its unused fuel. Criteria: ≥95% time in mean 300±1 km, e≤0.0005 and mean perigee≥295 km. Thermal/navigation assumptions require hardware calibration.

Mass flow is integrated independently of the GMAT tank; accepted tank states and electrical energy are audited. AllowNegativeFuelMass permits internal integrator trial stages only; commanded hot duration is limited by actual remaining fuel.
