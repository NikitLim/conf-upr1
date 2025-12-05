import os
import getpass
import socket
import pathlib
import argparse
import sys

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

def run_cmd(cmd, args):
    if cmd=='exit':
        return 'exit', 0

    if cmd=='ls':
        print('ls', *args)
        return None, 0

    if cmd=='cd':
        print('cd', *args)
        if len(args)==0:
            tgt=os.path.expanduser('~')
        else:
            tgt=args[0]
        try:
            os.chdir(os.path.expanduser(tgt))
            return None, 0
        except Exception as e:
            print(f'cd: {e}')
            return None, 1

    print(f'{cmd}: команда не найдена')
    return None, 1

def run_script(path):
    try:
        with open(path,'r',encoding='utf8') as f:
            for line in f:
                s=line.strip()
                if not s:
                    continue
                print(prompt() + s)
                parts=s.split()
                cmd=parts[0]
                args=parts[1:]
                res, code=run_cmd(cmd,args)
                if res=='exit':
                    return 0
                if code!=0:
                    print(f'Ошибка: команда "{cmd}" завершилась с кодом {code}. Скрипт остановлен.')
                    return 1
    except Exception as e:
        print(f'Ошибка чтения скрипта: {e}')
        return 1
    return 0

def repl():
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
        res, code=run_cmd(cmd,args)
        if res=='exit':
            break

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--vfs', default='.', help='Путь к VFS (необязательный)')
    p.add_argument('--script', help='Путь к стартовому скрипту')
    args=p.parse_args()

    print('=== DEBUG CONFIG ===')
    print('VFS path:', args.vfs)
    print('Script:', args.script)
    print('====================')

    if args.script:
        code=run_script(args.script)
        if code!=0:
            sys.exit(code)

    repl()


if __name__=='__main__':
    main()
