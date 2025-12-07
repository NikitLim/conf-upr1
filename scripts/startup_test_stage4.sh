# проверка uname и clear
uname
clear

# проверка базовых операций
ls
cd /
ls

# проверка работы с docs (средний VFS)
cd /docs
ls
cat readme.txt

# проверка uniq (если в VFS есть дубляжи)
cat todo.txt
uniq /docs/todo.txt

# глубокая навигация
cd /
cd /level1
cd level2
cd level3
ls
cat file.txt

# ошибки
cd /nonexistent
cat /docs

exit
