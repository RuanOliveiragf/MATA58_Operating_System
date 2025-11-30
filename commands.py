import os
import sys
#biblioteca termios: https://docs.python.org/3/library/termios.html consigo controlar comprotamento de baixo nivel
#biblioteca tty: https://docs.python.org/3/library/tty.html
import termios #a termios vai me permitir que eu consiga usar as teclas especiais como tab, backspace sem precisar dar um enter antes
               #o caractere vai ser enviado ao python assim que pressionado, ou seja, nao vai para o buffer temporario
import tty #com o tty eu envio toda tecla imediatamente


#cores de erro para o shell
cor_vermelho = "\033[91m"
cor_reset = "\033[0m"

#defino as teclas 
tecla_enter_r = b'\r'
tecla_enter_n = b'\n'
tecla_ctrl_c = b'\x03'
tecla_ctrl_d = b'\x04'
tecla_tab = b'\x09' #HT na tabela ascii
tecla_backspace_del = b'\x7f' #forma como o linux lÊ
tecla_backspace_bs = b'\x08' #padra asc que o windowes tambem lÊ

def obter_caractere():
#eu entro no modo raw do terminal para ler tecla por tecla, depois devolvo ao modo canonico
#0 = stdin
#1 = stdout
#2 = stderr
    try:
        old_settings = termios.tcgetattr(0) #salvo as configurações atuais do terminal no modo canonico
        tty.setraw(0) #envio a tecla imediatamente sem intermedio do terminal, entro no modo raw, ou seja, preciso fazer as funcoes manualmente (entrada de dados, teclas especiais, etc)
        ch = os.read(0, 1) #leio apenas 1 byte
    except termios.error: #tratamento por conta do docker
        return os.read(0, 1)
    finally:
        termios.tcsetattr(0, termios.TCSADRAIN, old_settings) #retorno as configurações antigas do terminal
    return ch #retorno o byte lido

def listar_opcoes_autocomplete(prefixo):

    try:
        arquivos = os.listdir('.') #listo todos os arquivos e pastas do diretorio atual
        opcoes = []
        
        #filtro os arquivos que começam com o prefixo
        for f in arquivos: #itero sobre todos os arquivos e pastas
            if f.startswith(prefixo): #o que comecar com o prefixo eu seleciono para adicionar na lista de opcoes
                opcoes.append(f) #adicoino o arquivo ou pasta na lista de opcoes
        return opcoes
    
    except OSError:
        return []

def ler_entrada():
    buffer = "" #buffer para armazenar a entrada do usuario
    
    while True:
        try:
            char = obter_caractere() #leio tecla por tecla
            
            #se eu pressionar enter
            if char == tecla_enter_r or char == tecla_enter_n:
                os.write(1, b'\r\n') # Pula linha visualmente
                break
    
            #se eu pressionar ctrl+c 
            elif char == tecla_ctrl_c:
                return None
            
            #se eu pressionar ctrl+d
            elif char == tecla_ctrl_d:
                if not buffer:
                    return None
            
            #se eu pressionar tab
            elif char == tecla_tab:
                if not buffer: #se o buffer estiver vazio, eu ignoro
                    continue 
                
                # Pega a última palavra (ex: "cat RE" -> "RE")
                partes = buffer.split(' ')
                prefixo = partes[-1]
                
                if not prefixo: continue

                opcoes = listar_opcoes_autocomplete(prefixo)
                
                #se achar apoenas uma arquivo compativel, ele autocompleta
                if len(opcoes) == 1:
                    match = opcoes[0]
                    #calcula o pedaço que falta digitar
                    restante = match[len(prefixo):]
                    
                    #adiciono barra se for diretorio, ou espaço se for arquivo
                    if os.path.isdir(match):
                        restante += "/"
                    else:
                        restante += " "
                    
                    buffer = buffer + restante
                    os.write(1, restante.encode('utf-8'))
            
            #se eu pressionar backspace
            elif char == tecla_backspace_del or char == tecla_backspace_bs:
                if len(buffer) > 0:
                    buffer = buffer[:-1] #removo o ultimo caractere do buffer
                    # Truque visual: Volta cursor, imprime espaço, volta cursor
                    os.write(1, b'\b \b')
            #se eu pressionar qualquer tecla que não seja tecla especial
            else:
                texto = char.decode('utf-8', errors='ignore')
                buffer = buffer + texto
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
            msg = f"{cor_vermelho}cd: erro ao mudar para '{path}': {e}{cor_reset}\n".encode('utf-8')
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
                         msg = f"{cor_vermelho}Erro de sintaxe no redirecionamento.{cor_reset}\n".encode('utf-8')
                         os.write(2, msg)
                         sys.exit(1)

                os.execvp(args[0], args)
                
            except OSError:
                erro_msg = f"{cor_vermelho}Erro: Comando '{args[0]}' não encontrado.{cor_reset}\n".encode('utf-8')
                os.write(2, erro_msg)
                sys.exit(1)
                
        elif pid > 0:
            os.wait()
            
        else:
            os.write(2, f"{cor_vermelho}Erro crítico: Falha no fork.{cor_reset}\n".encode('utf-8'))

    except OSError as e:
        msg = f"{cor_vermelho}Erro de sistema: {e}{cor_reset}\n".encode('utf-8')
        os.write(2, msg)