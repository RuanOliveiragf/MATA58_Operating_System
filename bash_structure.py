import os, sys
import commands

def exibir_prompt():
    #podemos usar a write https://docs.python.org/pt-br/3/library/os.html#os.write
    mensagem = "> ".encode('utf-8') #https://docs.python.org/pt-br/3/library/stdtypes.html#str.encode
    os.write(1, mensagem)

def main():
    while True:
        exibir_prompt()
        
        comandos = commands.ler_entrada()
        if comandos is None:
            break
            
        commands.executar_comando(comandos)

if __name__ == "__main__":
    main()