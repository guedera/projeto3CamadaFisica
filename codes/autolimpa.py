import platform
import os
import time

def clear_terminal():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')


# print("Testando a função clear_terminal()")
# time.sleep(2)
# clear_terminal()
# print("Fim do teste")