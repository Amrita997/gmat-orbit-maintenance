# Public propulsion reference and assumptions

The public baseline uses CU Aerospace's July 2024 CHIPS-180 warm-gas specifications: thrust 15 mN, Isp 67 s, power while thrusting 20 W, loaded propellant 277 g, and maximum continuous firing 10 min.

Source: https://cuaerospace.com/Portals/0/SiteContent/assets/PDF/CHIPS-Data-Sheet-240726.pdf
Manufacturer: https://www.cuaerospace.com/products-services/space-propulsion-systems/cubesat-high-impulse-propulsion-chips

This is an independent educational model using selected public reference values. It is not a digital twin, product qualification, endorsement, or prediction of actual CHIPS hardware behavior. The datasheet describes its values as informational and subject to change.

The same datasheet lists 176 N s total impulse. Constant nominal Isp with all 277 g usable implies about 182 N s; this simplified simulation uses the latter mass-flow relationship and does not claim to reproduce the manufacturer's total-impulse rating. Thermal and calibration factors modify integrated performance further.

Study assumptions, not manufacturer specifications: 30 kg wet satellite including the allocated propellant; 300 km mean altitude; 45 deg inclination; 0.12 m2 area; Cd 2.2; 300 s minimum hot burn; 600 s coast; 240 s anticipated warmup; 500 K firing threshold; lumped heater dynamics; synthetic navigation noise, outages, and pointing errors; unlimited availability of the assumed 20 W bus allocation. Heater-only operation is assigned 20 W. Pressure/temperature-dependent feed physics, stock tank geometry, lifetime endurance, and spacecraft attitude dynamics are not validated.

The maximum 600 s burn length follows the published continuous-firing limit. The other duty-cycle assumptions are illustrative. Study metrics use a 200 km geodetic endpoint, not atmospheric reentry. A computed days/kg ratio describes that paired case; it does not imply linear scaling to arbitrary fuel loads.
