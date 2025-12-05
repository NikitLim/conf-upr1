import os
import getpass
import socket
import pathlib
def prompt():
    u=getpass.getuser()
    h=socket.gethostname().split('.')[0]
    wd=os.getcwd()
    home=os.path.expanduser('~')
    if wd==home:
        p='~'
    else:
        p=str(pathlib.Path(wd).name)
    return f'{u}@{h}:{p}$ '
def run():
    while True:
        try:
            line=input(prompt())
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue
        s=line.strip()
        if not s:
            continue
        parts=s.split()
        cmd=parts[0]
        args=parts[1:]
        if cmd=='exit':
            break
        elif cmd=='ls':
            print('ls', *args)
        elif cmd=='cd':
            print('cd', *args)
            if len(args)==0:
                tgt=os.path.expanduser('~')
            else:
                tgt=args[0]
            try:
                os.chdir(os.path.expanduser(tgt))
            except Exception as e:
                print(f'cd: {e}')
        else:
            print(f'{cmd}: команда не найдена')
if __name__=='__main__':
    run()
