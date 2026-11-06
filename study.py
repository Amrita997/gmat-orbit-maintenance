"""Generate/run/analyze paired GMAT lifetime or controller-comparison cases."""
from __future__ import annotations
import argparse
import concurrent.futures
import csv
import json
import math
from pathlib import Path
import numpy as np
from gmat_model import build, shifted_weather, CONTROLLERS
from run_gmat import run, DEFAULT_INSTALL


def residence(t,h,lo,hi):
    total=0.
    for i in range(len(t)-1):
        a,b=h[i],h[i+1]
        if a==b:f=float(lo<=a<=hi)
        else:
            x,y=sorted(((lo-a)/(b-a),(hi-a)/(b-a)))
            f=max(0,min(1,y)-max(0,x))
        total+=(t[i+1]-t[i])*f
    return total/(t[-1]-t[0]) if t[-1]>t[0] else 0.


def metrics(folder):
    p=json.loads((folder/'manifest.json').read_text())
    x=np.atleast_1d(np.genfromtxt(folder/'history.txt',names=True))
    t=x['TimeS'];elapsed=t[-1]/86400
    assert np.all(np.diff(t)>1e-8),'Time did not advance'
    assert np.min(x['FuelRemaining'])>=-1e-8,'Accepted state overspent tank'
    assert np.max(np.abs(x['MassClosure']))<1e-7,'Independent integrated fuel flow does not close'
    assert np.max(np.abs(x['EnergyWh']-20*(x['HotSeconds']+x['WarmSeconds'])/3600))<1e-6,'Electrical energy ledger does not close'
    assert np.max(x['ThermalAborts'])==0,'Thermal abort requires review'
    ended=x['GeoH'][-1]<=200001
    assert ended or abs(elapsed-p['days'])<1e-6,'Unexpected horizon'
    depletion=max(x['DepletionDay']);depletion=None if depletion<0 else float(depletion)
    cutoff=depletion*86400 if depletion is not None else t[-1]
    y=x[t<=cutoff+1e-4]
    # Truncation is at a recorded decision epoch in this implementation.
    tt=y['TimeS'];errors=y['MeanH']-300000;dt=np.diff(tt)
    rms=math.sqrt(float(np.sum(dt*(errors[:-1]**2+errors[:-1]*errors[1:]+errors[1:]**2)/3)/tt[-1]))
    result=dict(controller=p['controller'],scenario=p['scenario'],atmosphere=p['atmosphere'],
        seed=p['seed'],status='end_altitude_reached' if ended else 'time_limit',elapsed_days=elapsed,
        propellant_used_kg=float(x['FuelUsed'][-1]),fuel_depletion_day=depletion,
        fueled_duration_days=float(tt[-1]/86400),fueled_altitude_rms_m=rms,
        fueled_band_fraction=residence(tt,y['MeanH'],299000,301000),
        fueled_max_eccentricity=float(max(y['MeanE'])),fueled_min_mean_perigee_m=float(min(y['MeanPerigee'])),
        heater_starts=int(x['HeaterStarts'][-1]),burn_starts=int(x['BurnStarts'][-1]),
        energy_wh=float(x['EnergyWh'][-1]),hot_hours=float(x['HotSeconds'][-1]/3600),
        warm_hours=float(x['WarmSeconds'][-1]/3600),max_mass_closure_error_kg=float(max(abs(x['MassClosure']))),
        maximum_temperature_k=float(max(x['Temperature'])),minimum_temperature_k=float(min(x['Temperature'])),
        terminal_mean_altitude_m=float(x['MeanH'][-1]),thermal_abort_count=int(max(x['ThermalAborts'])),
        peak_drag_while_maintained_n=float(max(x['DragN'][abs(x['MeanH']-300000)<=1000])),
        nav_altitude_error_rms_m=float(np.sqrt(np.trapezoid(x['NavError']**2,t)/t[-1])))
    result['fueled_requirements_met']=bool(p['controller']!='none' and result['fueled_band_fraction']>=.95 and
        result['fueled_max_eccentricity']<=.0005 and result['fueled_min_mean_perigee_m']>=295000)
    (folder/'summary.json').write_text(json.dumps(result,indent=2))
    with (folder/'history.csv').open('w',newline='') as stream:
        w=csv.writer(stream);w.writerow(x.dtype.names);w.writerows(x.tolist())
    return result


def report(out,results):
    out=Path(out)
    (out/'results.json').write_text(json.dumps(results,indent=2))
    lines=['# GMAT mission results','',
           'Native GMAT truth propagation and native GMAT controller/actuator logic. Mean elements use GMAT BrouwerShort. This is an independent educational example, not a validated model of a commercial propulsion product.','',
           '| Controller | Atmosphere | End day | Fuel (kg) | Fuel-out day | Fueled altitude RMS (m) | Fueled max e | Fueled min perigee (km) | Fueled criteria pass |',
           '|---|---|---:|---:|---:|---:|---:|---:|---|']
    for r in results:
        depleted='—' if r['fuel_depletion_day'] is None else f"{r['fuel_depletion_day']:.2f}"
        lines.append(f"| {r['controller']} | {r['atmosphere']} | {r['elapsed_days']:.2f} | {r['propellant_used_kg']:.6f} | {depleted} | {r['fueled_altitude_rms_m']:.1f} | {r['fueled_max_eccentricity']:.6f} | {r['fueled_min_mean_perigee_m']/1000:.3f} | {'yes' if r['fueled_requirements_met'] else 'no'} |")
    base=next((r for r in results if r['controller']=='none'),None)
    extensions=[]
    if base:
        lines+=['','## Paired lifetime estimate','']
        for r in results:
            if r['controller']=='none':continue
            exact=base['status']=='end_altitude_reached' and r['status']=='end_altitude_reached'
            if exact:
                delta=r['elapsed_days']-base['elapsed_days']
                ratio=delta/r['propellant_used_kg'] if r['propellant_used_kg'] else None
                lines.append(f"* {r['controller']}: {delta:.3f} additional days to the common 200 km geodetic endpoint; {ratio:.3f} days per kg consumed." if ratio is not None else '* No propellant consumed; per-kg metric is undefined.')
                extensions.append(dict(controller=r['controller'],exact=True,extension_days=delta,days_per_kg_consumed=ratio))
            elif base['status']=='end_altitude_reached':
                delta=r['elapsed_days']-base['elapsed_days']
                lines.append(f"* {r['controller']}: at least {delta:.3f} additional days with the loaded allocation. The controlled lifetime is right-censored; do not normalize this as a completed per-kg lifetime estimate.")
                extensions.append(dict(controller=r['controller'],exact=False,extension_lower_bound_days=delta))
            else:lines.append('* Baseline lifetime is censored; extend the horizon to estimate total extension.')
    lines+=['','The endpoint is a study boundary, not reentry. Maintenance accuracy is assessed separately while fuel is available. The uncontrolled spacecraft starts at the same 30 kg wet mass and retains its unused fuel. Criteria: ≥95% time in mean 300±1 km, e≤0.0005 and mean perigee≥295 km. Thermal/navigation assumptions require hardware calibration.','',
            'Mass flow is integrated independently of the GMAT tank; accepted tank states and electrical energy are audited. AllowNegativeFuelMass permits internal integrator trial stages only; commanded hot duration is limited by actual remaining fuel.','']
    (out/'lifetime-extension.json').write_text(json.dumps(extensions,indent=2))
    (out/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    import os
    os.environ['MPLCONFIGDIR']=str((out/'.matplotlib').resolve())
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(3,1,figsize=(11,10),sharex=True,layout='constrained')
    for r in results:
        x=np.genfromtxt(out/r['controller']/'history.txt',names=True)[::5]
        axes[0].plot(x['Day'],(x['MeanH']-300000)/1000,label=r['controller'])
        axes[1].plot(x['Day'],x['FuelUsed']*1000)
        axes[2].plot(x['Day'],x['MeanE'])
    axes[0].axhspan(-1,1,alpha=.15,color='green');axes[0].set_yscale('symlog',linthresh=1)
    axes[0].set_ylabel('Mean altitude error (km)');axes[0].legend()
    axes[1].set_ylabel('Fuel used (g)');axes[2].set_ylabel('Mean eccentricity')
    axes[2].axhline(.0005,ls=':',color='gray');axes[2].set_xlabel('Elapsed days')
    for ax in axes:ax.grid(alpha=.2)
    fig.savefig(out/'comparison.png',dpi=150);plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--install',type=Path,default=DEFAULT_INSTALL)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--weather',type=Path,default=Path(__file__).parent/'data/SpaceWeather-All-v1.2.txt')
    p.add_argument('--scenario',choices=['quiet','storm','stress'],default='storm')
    p.add_argument('--controllers',nargs='+',choices=CONTROLLERS,default=['none','eccentricity'])
    p.add_argument('--atmosphere',choices=['MSISE90','NRLMSISE00'],default='MSISE90')
    p.add_argument('--days',type=float,default=180)
    p.add_argument('--seed',type=int,default=731)
    p.add_argument('--sample',type=float,default=120)
    p.add_argument('--workers',type=int,default=2)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    forecast=args.out/'forecast-weather.txt';shifted_weather(args.weather,forecast)
    scripts=[build(args.out/c,args.weather,forecast,args.scenario,c,args.days,args.seed,args.atmosphere,args.sample) for c in args.controllers]
    def case(script):
        run(script,args.install);result=metrics(script.parent);print(json.dumps(result),flush=True);return result
    with concurrent.futures.ThreadPoolExecutor(args.workers) as pool:results=list(pool.map(case,scripts))
    report(args.out,results)


if __name__=='__main__':main()
