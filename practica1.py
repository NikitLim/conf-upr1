import base64
import csv
import getpass
import socket
import argparse
import platform

vfs = {}
cwd = '/'

def load_vfs(path):
    global vfs
    vfs = {'/': {}}
    try:
        with open(path, newline='', encoding='utf8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                p = row['path'].strip('/')
                parts = [] if p == '' else p.split('/')
                d = vfs['/']
                for seg in parts[:-1]:
                    if seg not in d:
                        d[seg] = {}
                    d = d[seg]
                if parts == []:
                    continue
                name = parts[-1]
                if row['type'] == 'dir':
                    d[name] = {}
                else:
                    d[name] = base64.b64decode(row['content']) if row.get('content') else b''
    except Exception as e:
        print(f'Ошибка при загрузке VFS: {e}')

def norm_path(path):
    if not path:
        return cwd
    if path.startswith('/'):
        cur = '/'
        parts = path.strip('/').split('/')
    else:
        cur = cwd
        if cur == '/':
            parts = path.strip('/').split('/')
        else:
            parts = (cur.strip('/') + '/' + path.strip('/')).split('/')
    out = []
    for p in parts:
        if p == '' or p == '.':
            continue
        if p == '..':
            if out:
                out.pop()
            continue
        out.append(p)
    return '/' + '/'.join(out) if out else '/'

def get_dir(path):
    p = norm_path(path)
    if p == '/':
        return vfs['/']
    parts = p.strip('/').split('/')
    d = vfs['/']
    for seg in parts:
        if seg in d and isinstance(d[seg], dict):
            d = d[seg]
        else:
            return None
    return d

def get_node(path):
    p = norm_path(path)
    if p == '/':
        return vfs['/']
    parts = p.strip('/').split('/')
    d = vfs['/']
    for seg in parts:
        if seg in d:
            d = d[seg]
        else:
            return None
    return d

def prompt():
    u = getpass.getuser()
    h = socket.gethostname().split('.')[0]
    p = cwd if cwd != '/' else '~'
    return f'{u}@{h}:{p}$ '

def cmd_ls(args):
    path = args[0] if args else cwd
    node = get_node(path)
    if node is None:
        print(f'ls: нет такого каталога: {path}')
        return 1
    if isinstance(node, bytes):
        print(path)
        return 0
    names = sorted(node.keys())
    print(' '.join(names))
    return 0

def cmd_cd(args):
    global cwd
    target = args[0] if args else '/'
    p = norm_path(target)
    node = get_dir(p)
    if node is None:
        return 1
    cwd = p
    return 0

def cmd_cat(args):
    if not args:
        print('cat: отсутствует аргумент')
        return 1
    path = args[0]
    node = get_node(path)
    if node is None:
        print(f'cat: файл не найден: {path}')
        return 1
    if isinstance(node, dict):
        print(f'cat: {path}: это каталог')
        return 1
    try:
        print(node.decode('utf8'))
    except Exception:
        print(node)
    return 0

def cmd_uname(args):
    print(platform.system())
    return 0

def cmd_uniq(args):
    if not args:
        print('uniq: требуется файл')
        return 1
    path = args[0]
    node = get_node(path)
    if node is None or isinstance(node, dict):
        print(f'uniq: файл не найден: {path}')
        return 1
    try:
        s = node.decode('utf8').splitlines()
    except Exception:
        s = [line.decode('utf8', errors='replace') for line in node.splitlines()]
    out = []
    prev = None
    for line in s:
        if line != prev:
            out.append(line)
        prev = line
    for line in out:
        print(line)
    return 0

def cmd_clear(args):
    print("\033c", end='')
    return 0

def run_cmd(cmd, args):
    if cmd == 'exit':
        return 'exit', 0
    if cmd == 'ls':
        return None, cmd_ls(args)
    if cmd == 'cd':
        return None, cmd_cd(args)
    if cmd == 'cat':
        return None, cmd_cat(args)
    if cmd == 'uname':
        return None, cmd_uname(args)
    if cmd == 'uniq':
        return None, cmd_uniq(args)
    if cmd == 'clear':
        return None, cmd_clear(args)
    print(f'{cmd}: команда не найдена')
    return None, 1

def run_script(script_path):
    try:
        with open(script_path, encoding='utf8') as f:
            for line in f:
                s = line.rstrip('\n')
                if not s or s.strip().startswith('#'):
                    continue
                print(prompt() + s)
                parts = s.split()
                cmd = parts[0]
                args = parts[1:]
                res, code = run_cmd(cmd, args)
                if res == 'exit':
                    return 0
                if code != 0:
                    print(f'Ошибка: команда "{cmd}" завершилась с кодом {code}. Скрипт остановлен.')
                    return 1
    except Exception as e:
        print(f'Ошибка чтения скрипта: {e}')
        return 1
    return 0

def repl():
    while True:
        try:
            line = input(prompt())
        except (EOFError, KeyboardInterrupt):
            print()
            break
        s = line.strip()
        if not s:
            continue
        parts = s.split()
        cmd = parts[0]
        args = parts[1:]
        res, code = run_cmd(cmd, args)
        if res == 'exit':
            break

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vfs', default='vfs_min.csv', help='Путь к CSV с VFS')
    parser.add_argument('--script', help='Стартовый скрипт')
    args = parser.parse_args()

    print('=== DEBUG CONFIG ===')
    print('VFS path:', args.vfs)
    print('Script:', args.script)
    print('====================')

    load_vfs(args.vfs)

    if args.script:
        code = run_script(args.script)
        if code != 0:
            return

    repl()

if __name__ == '__main__':
    main()
