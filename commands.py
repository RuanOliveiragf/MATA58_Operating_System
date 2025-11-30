import os
import sys
import termios
import tty

# Definição de Cores
COR_VERMELHO = "\033[91m"
COR_RESET = "\033[0m"

def _obter_caractere():
    fd = 0
    try:
        old_settings = termios.tcgetattr(fd)
        tty.setraw(fd)
        ch = os.read(fd, 1)
    except termios.error:
        return os.read(fd, 1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def _listar_opcoes_autocomplete(prefixo):
    try:
        arquivos = os.listdir('.')
        opcoes = []
        
        for f in arquivos:
            if f.startswith(prefixo):
                opcoes.append(f)
                
        return opcoes
    except OSError:
        return []

def ler_entrada():
    buffer = "" 
    
    while True:
        try:
            char = _obter_caractere()
            
            if char == b'\r' or char == b'\n':
                os.write(1, b'\r\n') 
                break
            
            elif char == b'\x03':
                return None
            
            elif char == b'\x04':
                if not buffer:
                    return None
            

            elif char == b'\x09': 
                if not buffer: continue 
                
                partes = buffer.split(' ')
                prefixo = partes[-1]
                
                if not prefixo: continue

                opcoes = _listar_opcoes_autocomplete(prefixo)
                
                if len(opcoes) == 1:
                    match = opcoes[0]
                    restante = match[len(prefixo):]
                    if os.path.isdir(match):
                        restante += "/"
                    else:
                        restante += " "
                    
                    buffer += restante
                    os.write(1, restante.encode('utf-8'))

            elif char == b'\x7f' or char == b'\x08':
                if len(buffer) > 0:
                    buffer = buffer[:-1]
                    os.write(1, b'\b \b')
            else:
                texto = char.decode('utf-8', errors='ignore')
                buffer += texto
                os.write(1, char)
                
        except OSError:
            pass

    if not buffer:
        return []
        
    return buffer.strip().split()

def executar_comando(args):
    if not args:
        return
    
    if args[0] == 'exit':
        os.write(1, "Saindo do shell...\n".encode('utf-8'))
        sys.exit(0)

    if args[0] == 'cd':
        try:
            path = args[1] if len(args) > 1 else os.environ.get('HOME', '.')
            os.chdir(path)
        except OSError as e:
            msg = f"{COR_VERMELHO}cd: erro ao mudar para '{path}': {e}{COR_RESET}\n".encode('utf-8')
            os.write(2, msg)
        return
    
    try:
        pid = os.fork()

        if pid == 0:
            try:
                if '>' in args:
                    try:
                        idx = args.index('>')
                        nome_arquivo = args[idx+1]
                        args = args[:idx] 
                        fd_arquivo = os.open(nome_arquivo, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
                        
                        os.dup2(fd_arquivo, 1)
                        os.close(fd_arquivo)
                    except (ValueError, IndexError, OSError):
                         msg = f"{COR_VERMELHO}Erro de sintaxe no redirecionamento.{COR_RESET}\n".encode('utf-8')
                         os.write(2, msg)
                         sys.exit(1)

                os.execvp(args[0], args)
                
            except OSError:
                erro_msg = f"{COR_VERMELHO}Erro: Comando '{args[0]}' não encontrado.{COR_RESET}\n".encode('utf-8')
                os.write(2, erro_msg)
                sys.exit(1)
                
        elif pid > 0:
            # === PROCESSO PAI ===
            os.wait()
            
        else:
            os.write(2, f"{COR_VERMELHO}Erro crítico: Falha no fork.{COR_RESET}\n".encode('utf-8'))

    except OSError as e:
        msg = f"{COR_VERMELHO}Erro de sistema: {e}{COR_RESET}\n".encode('utf-8')
        os.write(2, msg)