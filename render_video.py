"""Render a synchronized replay of GMAT telemetry, not a screen recording.

Input columns: elapsed days, EarthMJ2000Eq XYZ km, geodetic altitude km,
BrouwerShort SMA km, BrouwerShort eccentricity, live thruster C1 N.
"""
from pathlib import Path
import argparse,os
import numpy as np
os.environ.setdefault('MPLCONFIGDIR',str(Path('.matplotlib').resolve()))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
import imageio_ffmpeg


def render(source,output,seconds=36,fps=24):
    data=np.genfromtxt(source,names=True)
    a=np.column_stack([data[n] for n in data.dtype.names])
    a=a[np.all(np.isfinite(a),axis=1)]
    # Forecast-only propagation can publish repeated or out-of-order truth epochs.
    # Retain monotonically increasing truth samples; never synthesize orbital states.
    keep=[];last=-1
    for i,t in enumerate(a[:,0]):
        if t>last+1e-10:keep.append(i);last=t
    a=a[keep];time=a[:,0]*24
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    matplotlib.rcParams['animation.ffmpeg_path']=imageio_ffmpeg.get_ffmpeg_exe()
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':'#e5edf7',
        'axes.labelcolor':'#c3cede','xtick.color':'#91a1b8','ytick.color':'#91a1b8',
        'axes.edgecolor':'#34445c','axes.facecolor':'#101e32','figure.facecolor':'#091322',
        'font.size':10,'axes.titleweight':'bold'})
    fig=plt.figure(figsize=(12.8,7.2),dpi=100)
    grid=fig.add_gridspec(3,2,left=.025,right=.955,bottom=.13,top=.80,width_ratios=[1.1,1],hspace=.45,wspace=.18)
    orbit=fig.add_subplot(grid[:,0],projection='3d');orbit.set_facecolor('#091322')
    u=np.linspace(0,2*np.pi,60);v=np.linspace(0,np.pi,30)
    orbit.plot_surface(6378.137*np.outer(np.cos(u),np.sin(v)),6378.137*np.outer(np.sin(u),np.sin(v)),6378.137*np.outer(np.ones_like(u),np.cos(v)),color='#174d74',alpha=.85,linewidth=0,shade=True)
    for axis in [orbit.xaxis,orbit.yaxis,orbit.zaxis]:
        axis.pane.fill=False;axis.pane.set_edgecolor('#091322')
    orbit.set_axis_off();orbit.set_box_aspect([1,1,1]);orbit.view_init(elev=25,azim=-60)
    for setter in [orbit.set_xlim,orbit.set_ylim,orbit.set_zlim]:setter(-7500,7500)
    trail,=orbit.plot([],[],[],color='#4ed9e9',lw=1.5)
    dot,=orbit.plot([],[],[],'o',color='#ffb35a',ms=6)
    orbit.set_title('Earth-centered inertial orbit',pad=0,fontsize=12)
    axes=[fig.add_subplot(grid[j,1]) for j in range(3)]
    values=[a[:,5]-6378.137,a[:,6],a[:,7]*1000]
    labels=['Mean altitude (km)','Mean eccentricity','Thrust (mN)']
    colors=['#4ed9e9','#a2a9ff','#ffb35a'];lines=[];cursors=[]
    for ax,y,label,color in zip(axes,values,labels,colors):
        ax.set_xlim(0,time[-1]);lo,hi=min(y),max(y);pad=max((hi-lo)*.18,1e-7)
        if label=='Thrust (mN)':lo=0;hi=max(16,hi);pad=1
        ax.set_ylim(lo-pad,hi+pad);ax.set_ylabel(label);ax.grid(alpha=.12)
        ax.spines[['top','right']].set_visible(False)
        if label=='Thrust (mN)':line,=ax.step([],[],where='post',color=color,lw=1.3)
        else:line,=ax.plot([],[],color=color,lw=1.5)
        lines.append(line);cursors.append(ax.axvline(0,color='#ffffff',alpha=.3,lw=.8))
    axes[-1].set_xlabel('Simulated time (hours)')
    fig.text(.045,.94,'Can a small resistojet maintain a 300 km orbit?',fontsize=22,weight='bold')
    fig.text(.045,.885,'GMAT propagation + native orbit-maintenance control',fontsize=14,color='#4ed9e9')
    fig.text(.045,.84,'30 kg satellite  |  45 deg inclination  |  public reference: 15 mN / 67 s / 20 W',fontsize=11,color='#bac8db')
    status=fig.text(.06,.16,'',fontsize=12,color='#ffb35a')
    clock=fig.text(.06,.12,'',fontsize=12)
    fig.text(.045,.065,'Independent educational study using selected public CHIPS-180 specifications; not manufacturer validated.',fontsize=9,color='#91a1b8')
    fig.text(.045,.035,'GMAT simulation replay (not GUI capture). Time accelerated; spacecraft marker enlarged. Thermal/navigation behavior assumed.',fontsize=8.5,color='#91a1b8')
    frames=int(seconds*fps);indices=np.searchsorted(time,np.linspace(time[0],time[-1],frames));indices=np.clip(indices,0,len(time)-1)
    writer=FFMpegWriter(fps=fps,codec='libx264',bitrate=3500,extra_args=['-pix_fmt','yuv420p','-movflags','+faststart'],metadata={'title':'GMAT CubeSat orbit maintenance — public reference case','comment':'Synchronized replay of native GMAT propagated states; illustrative thermal/navigation assumptions.'})
    with writer.saving(fig,str(output),100):
        for frame,i in enumerate(indices):
            begin=np.searchsorted(time,max(0,time[i]-1.6))
            xyz=a[begin:i+1,1:4];trail.set_data_3d(xyz[:,0],xyz[:,1],xyz[:,2])
            dot.set_data_3d([a[i,1]],[a[i,2]],[a[i,3]])
            firing=a[i,7]>1e-8;dot.set_color('#ffb35a' if firing else '#4ed9e9')
            for line,cursor,y in zip(lines,cursors,values):
                line.set_data(time[:i+1],y[:i+1]);cursor.set_xdata([time[i],time[i]])
            status.set_text('THRUSTER FIRING' if firing else 'COAST / HEATER-ONLY')
            status.set_color('#ffb35a' if firing else '#4ed9e9')
            clock.set_text(f'T + {time[i]:05.2f} hours  |  actual thrust {a[i,7]*1000:05.2f} mN')
            if frame==frames//2:fig.savefig(output.with_suffix('.png'),dpi=100)
            writer.grab_frame()
            if frame%120==0:print(f'Rendered {frame}/{frames}',flush=True)
    plt.close(fig)
    print(output.resolve(),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('telemetry',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--seconds',type=float,default=36)
    args=parser.parse_args();render(args.telemetry,args.output,args.seconds)
