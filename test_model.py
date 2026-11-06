from pathlib import Path
import pytest
from gmat_model import build


def test_public_propulsion_and_actuator_budget(tmp_path):
    # The compiler only embeds paths; this unit test requires no external data.
    weather=tmp_path/'weather.txt'
    script=build(tmp_path/'case',weather,weather).read_text()
    assert 'GMAT Fuel.FuelMass = 0.277;' in script
    assert 'GMAT Sat.DryMass = 29.723;' in script
    assert 'NominalIsp = 67;' in script
    assert 'MaxHot = 600;' in script
    assert 'Sat.Jet.C1 = ActualThrust;' in script
    assert script.count('BeginFiniteBurn Burn(Sat);') == 1
    assert script.count('EndFiniteBurn Burn(Sat);') == 1


def test_native_displays_use_live_satellite_parameters(tmp_path):
    weather=tmp_path/'weather.txt'
    script=build(tmp_path/'case',weather,weather,displays=True).read_text()
    assert 'Create XYPlot AltitudeVsTime;' in script
    assert 'Create XYPlot EccentricityVsTime;' in script
    assert 'ThrustFiringVsTime.YVariables = {Sat.Jet.C1};' in script
    assert 'Create OrbitView MissionOrbitView;' in script
    assert 'Sat.ElapsedSecs = StepS' in script


@pytest.mark.parametrize('days,sample,fuel',[(0,120,.277),(1,301,.277),(1,120,30)])
def test_invalid_simulation_limits(tmp_path,days,sample,fuel):
    with pytest.raises(ValueError):
        build(tmp_path,tmp_path/'weather',tmp_path/'weather',days=days,sample=sample,fuel_kg=fuel)
