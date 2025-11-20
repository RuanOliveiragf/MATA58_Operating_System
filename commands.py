import os
import sys

def ler_entrada():

    try:
        entrada_bytes = os.read(0, 1024) #leio ate 1024 bytes
        
        if not entrada_bytes:
            return None
            
        entrada_str = entrada_bytes.decode('utf-8').strip()#transformo a entrada de bytes para string
        
        #if not entrada_str:
            #return []
            
        argumentos = entrada_str.split() #transformo a entrada em token
        return argumentos
        
    except OSError as e:
        msg_erro = f"Erro ao ler entrada: {e}\n".encode('utf-8')
        os.write(2, msg_erro)
        return []

def executar_comando(args):

    if not args:
        return
    
    if args[0] == 'exit':
        os.write(1, "Saindo do shell...\n".encode('utf-8'))
        sys.exit(0)
    
    try:
        pid = os.fork() #cria o processo
        print(pid)

        if pid == 0:#processo filho
            try:
                os.execvp(args[0], args)
            except OSError:
                erro_msg = f"Erro: Comando '{args[0]}' não encontrado.\n".encode('utf-8')
                os.write(2, erro_msg)
                sys.exit(1)#mata o filho com erro
                
        elif pid > 0:
            os.wait()
            
        else:
            os.write(2, "Erro crítico: Falha no fork.\n".encode('utf-8'))

    except OSError as e:
        msg = f"Erro de sistema: {e}\n".encode('utf-8')
        os.write(2, msg)