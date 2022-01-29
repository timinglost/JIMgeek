import subprocess
count = int(input('Введите количество: '))
for i in range(count):
    name = '' #input('Введите имя: ')
    if name == '':
        name = f'anonymous_{i}'
    subprocess.Popen(['python', 'client.py', '-rw', '0', '-name', f'{name}'], creationflags=subprocess.CREATE_NEW_CONSOLE)
    subprocess.Popen(['python', 'client.py', '-rw', '1', '-name', f'{name}'], creationflags=subprocess.CREATE_NEW_CONSOLE)