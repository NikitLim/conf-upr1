import base64
import csv
import getpass
import socket
import argparse

vfs = {}
cwd = '/'

def load_vfs(path):
    global vfs
    vfs = {'/': {}}
    try:
        with open(path, newline='', encoding='utf8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                parts = row['path'].strip('/').split('/')
                d = vfs['/']
                if parts == ['']:
                    continue
                for p in parts[:-1]:
                    if p not in d:
                        d[p] = {}
                    d = d[p]
                name = parts[-1]
                if row['type'] == 'dir':
                    d[name] = {}
                else:
                    d[name] = base64.b64decode(row['content']) if row['content'] else b''
    except Exception as e:
        print(f'Ошибка при загрузке VFS: {e}')

def prompt():
    u = getpass.getuser()
    h = socket.gethostname().split('.')[0]
    p = cwd if cwd != '/' else '~'
    return f'{u}@{h}:{p}$ '

def get_dir(path):
    parts = path.strip('/').split('/')
    d = vfs['/']
    if path == '/':
        return d
    for p in parts:
        if p in d and isinstance(d[p], dict):
            d = d[p]
        else:
            return None
    return d

def run_cmd(cmd, args):
    global cwd
    if cmd == 'exit':
        return 'exit', 0
    if cmd == 'ls':
        path = args[0] if args else cwd
        d = get_dir(path)
        if d is None:
            print(f'ls: нет такого каталога: {path}')
            return None, 1
        print(' '.join(d.keys()))
        return None, 0
    if cmd == 'cd':
        path = args[0] if args else '/'
        if path == '~':
            cwd = '/'
            return None, 0
        d = get_dir(path)
        if d is None:
            print(f'cd: нет такого каталога: {path}')
            return None, 1
        cwd = path if path.startswith('/') else '/' + path
        return None, 0
    if cmd == 'cat':
        if not args:
            print('cat: отсутствует аргумент')
            return None, 1
        path = args[0]
        parts = path.strip('/').split('/')
        d = vfs['/']
        for p in parts[:-1]:
            if p in d and isinstance(d[p], dict):
                d = d[p]
            else:
                print(f'cat: файл не найден: {path}')
                return None, 1
        name = parts[-1]
        if name in d and isinstance(d[name], bytes):
            print(d[name].decode('utf8'))
            return None, 0
        else:
            print(f'cat: файл не найден: {path}')
            return None, 1
    print(f'{cmd}: команда не найдена')
    return None, 1

def run_script(script_path):
    try:
        with open(script_path, encoding='utf8') as f:
            for line in f:
                s = line.strip()
                if not s:
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
