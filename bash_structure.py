import os, sys
import commands

def exibir_prompt():
    #podemos usar a write https://docs.python.org/pt-br/3/library/os.html#os.write
    mensagem = "> ".encode('utf-8') #write só escreve em bytes, então precisa pegar em string e transformar para bytes https://docs.python.org/pt-br/3/library/stdtypes.html#str.encode
    #os.write(1, mensagem)
    os.write(1, mensagem)

def main():
    while True:
        exibir_prompt()

        comando_tokens = commands.ler_entrada()
        #comandos = commands.ler_entrada()
        if comando_tokens is None:
            break
            
        commands.executar_comando(comando_tokens)

if __name__ == "__main__":
    main()