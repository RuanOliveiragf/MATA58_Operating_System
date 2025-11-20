import os,sys

def ler_entrada():
    try:
        entrada_bytes = os.read(0, 1024) #leio até 1024 bytes
    
        if not entrada_bytes:
            return None
            
        entrada_str = entrada_bytes.decode('utf-8').strip() #tranformando a entrada em bytes para string
        print(entrada_str)

        #if not entrada_str:
            #return []
            
        argumentos = entrada_str.split() #faço a tokenização
        return argumentos
        
    except OSError as e:
        msg_erro = f"Erro ao ler entrada: {e}\n".encode('utf-8')
        os.write(2, msg_erro) # 2 é stderr
        return []
    
def executar_comando(args):
    if not args:
        return

    if args[0] == 'exit':
        os.write(1, "Saindo do shell...\n".encode('utf-8'))
        sys.exit(0)

    elif args[0] == 'echo':
        saida = args,"teste"
        os.write(1, (args,))

    pass 