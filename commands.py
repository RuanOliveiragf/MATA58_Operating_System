import os,sys

def ler_entrada():
    try:
        entrada_bytes = os.read(0, 1024) #leio até 1024 bytes
    
        if not entrada_bytes:
            return None
            
        entrada_str = entrada_bytes.decode('utf-8') #tranformando a entrada em bytes para string

        #if not entrada_str:
            #return []
            
        argumentos = entrada_str.split() #faço a tokenização
        return argumentos
        
    except OSError as e:
        msg_erro = f"Erro ao ler entrada: {e}\n".encode('utf-8')
        os.write(2, msg_erro) # 2 é stderr
        return []
    
