help
uname
ls

# mkdir
mkdir /new
ls /
mkdir /new
mkdir /new/docs
mkdir /notexist/docs

# chown
chown root /new
chown user /new/docs
chown admin /docs/readme.txt
chown boss /no_such_file

# проверка навигации
cd /new
ls
cd /new/docs
ls

# uniq + cat
uniq /docs/todo.txt
cat /docs/readme.txt

clear

exit

