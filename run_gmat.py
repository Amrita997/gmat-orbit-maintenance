"""Run a GMAT script without changing the installed GMAT configuration."""
from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
from pathlib import Path


DEFAULT_INSTALL=Path(os.environ.get('GMAT_HOME', 'GMAT'))


def run(script:Path,install:Path=DEFAULT_INSTALL,timeout=1800):
    script=script.resolve();install=install.resolve();folder=script.parent
    if not (install/'bin/gmat_startup_file.txt').exists():
        raise FileNotFoundError('Pass --install /path/to/GMAT or set GMAT_HOME to the GMAT installation root')
    text=(install/'bin/gmat_startup_file.txt').read_text()
    text=re.sub(r'^ROOT_PATH\s*=.*$',f'ROOT_PATH = {install.as_posix()}/',text,flags=re.M)
    text=re.sub(r'^OUTPUT_PATH\s*=.*$',f'OUTPUT_PATH = {folder.as_posix()}/',text,flags=re.M)
    # These optional interfaces are not needed by a native mission script.
    # Avoid Python/Matlab dependency dialogs and loading 3-D UI plugins in batch.
    lines=[s for s in text.splitlines() if not(s.startswith('PLUGIN') and any(x in s for x in
          ('PythonInterface','MatlabInterface','Fmincon','OpenFrames','OVtoOFI')))]
    startup=folder/'startup.txt'
    startup.write_text('\n'.join(lines)+'\nWRITE_PERSONALIZATION_FILE = OFF\n')
    executable=install/'bin/GmatConsole.exe'
    if not executable.exists():executable=install/'bin/GMAT.exe'
    gui_flags=['-ns','-m'] if executable.name.lower()=='gmat.exe' else []
    command=[str(executable),*gui_flags,'-x','-s',str(startup),'-r',str(script)]
    kwargs={}
    if os.name=='nt':
        info=subprocess.STARTUPINFO();info.dwFlags|=subprocess.STARTF_USESHOWWINDOW;info.wShowWindow=0
        kwargs['startupinfo']=info
        kwargs['creationflags']=subprocess.CREATE_NO_WINDOW
    print('Running',script,'with',executable,flush=True)
    with (folder/'console.log').open('w') as stream:
        child=subprocess.Popen(command,cwd=install/'bin',stdout=stream,stderr=subprocess.STDOUT,**kwargs)
        try:code=child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            child.kill();child.wait();raise RuntimeError('GMAT timed out; inspect console.log and GmatLog.txt')
    log=(folder/'GmatLog.txt').read_text(errors='replace') if (folder/'GmatLog.txt').exists() else ''
    success=code==0 and 'Mission run completed.' in log and not re.search(r'\*\*\*\* ERROR|Exception Thrown',log)
    result=dict(executable=str(executable),exit_code=code,success=success,command=command)
    (folder/'execution.json').write_text(json.dumps(result,indent=2))
    if not success:raise RuntimeError(f'GMAT failed: exit={code}\n{log[-10000:]}')
    print('GMAT completed',flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('script',type=Path)
    p.add_argument('--install',type=Path,default=DEFAULT_INSTALL)
    p.add_argument('--timeout',type=float,default=1800)
    args=p.parse_args();run(args.script,args.install,args.timeout)
