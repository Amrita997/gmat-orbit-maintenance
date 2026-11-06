# Executed public-case validation

Native GMAT R2022a/MSISE90, historical replay from 2024-04-15, seed 731. Both lifetime trajectories reached the same 200 km geodetic altitude endpoint. Reports and numerical summaries in lifetime/ are from the public propulsion reference case.

* Compiler checks: five checks passed.
* Independent accepted tank/mass-flow closure: less than 1e-7 kg.
* Electrical energy ledger and thermal-abort assertions passed.
* No manufacturer hardware validation is implied.
* A one-day native telemetry run supplies examples/telemetry.txt for the replay.
* The six-controller two-day functional comparison is provided separately; it is not a long-duration ranking of controllers.

The weather-file hash is documented in data/README.md. Generated machine-specific paths and native execution logs are excluded. Lifetime total includes coast after fuel exhaustion; orbit tracking is assessed separately during the fueled interval.
