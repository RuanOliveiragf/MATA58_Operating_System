# Mini Shell - Projeto Integrador

Este projeto consiste no desenvolvimento de um mini interpretador de comandos (shell) em Python, simulando a execução de comandos em um terminal Linux e explorando chamadas de sistema (syscalls).

Como o projeto utiliza chamadas nativas de sistemas Unix (como `os.fork()`, `os.execvp()`, `os.wait()`), ele **não roda nativamente no Windows**. Uma alternativa para rodar o programa em Windows é utiliar a ferramente Dev Container do Visual Studio Code, que permite desenvolver dentro de um contêiner, que é um ambiente de desenvolvimento completo que roda em um sistema Unix. O guia abaixo explica como configurar e rodar o projeto utilizando Docker e VS Code para garantir compatibilidade total.

## 🚀 Pré-requisitos (Configuração Inicial)

Se você ainda não tem o ambiente configurado no Windows, siga os passos abaixo na ordem apresentada.

### 1\. Instalar o WSL2 (Subsistema do Windows para Linux)

O Docker precisa do kernel do Linux para funcionar no Windows.

1.  Abra o **PowerShell** como Administrador.
2.  Execute o comando:
    ```powershell
    wsl --install
    ```
3.  **Reinicie o computador**.
4.  Após reiniciar, uma janela pode abrir instalando o Ubuntu. Apenas crie um usuário/senha qualquer e feche a janela.

### 2\. Instalar o Docker Desktop

1.  Baixe e instale o [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/).
2.  Abra o aplicativo **Docker Desktop**.
3.  Aguarde até que a barra de status no canto inferior esquerdo fique **verde** ("Engine running").
4.  Talvez o instalador peça para reiniciar o computador.

### 3\. Preparar o VS Code

1.  Abra o Visual Studio Code.
2.  Vá na aba de Extensões (`Ctrl+Shift+X`).
3.  Pesquise e instale a extensão: **Dev Containers** (da Microsoft).

-----

## 🛠️ Como Rodar o Projeto

Com as ferramentas instaladas, siga estes passos para abrir o código dentro de um ambiente Linux isolado (Container):

1.  **Abra a pasta do projeto** no VS Code.
2.  Pressione `F1` (ou `Ctrl+Shift+P`) para abrir a paleta de comandos.
3.  Digite e selecione: `Dev Containers: Add Dev Container Configuration Files...`.
      * Selecione **Python 3**.
      * Escolha a versão mais recente.
      * Não precisa marcar funcionalidades adicionais, apenas dê **OK**.
4.  Uma notificação aparecerá no canto inferior direito. Clique em **Reopen in Container**.
      * *Alternativa:* Pressione `F1` e digite `Dev Containers: Reopen in Container`.

Quando o terminal do VS Code abrir novamente, você já estará dentro do ambiente Linux.

> **Nota:** Na primeira vez, isso pode levar alguns minutos enquanto o VS Code baixa e constrói o ambiente Linux.

-----

## Estrutura do projeto

O projeto adota uma estrutura modular para desacoplar o fluxo de controle das operações de sistema. O arquivo bash_structure.py implementa o REPL (Read-Eval-Print Loop), gerenciando a interface com o usuário e a persistência do shell. O núcleo funcional reside em commands.py, que encapsula as chamadas ao sistema (syscalls), sendo responsável pelo parsing da entrada via os.read e pelo gerenciamento do ciclo de vida dos processos através de os.fork, os.execvp e os.wait.

O projeto é estrurado  

```text
Mini-Shell/
├── .devcontainer/       # Configurações automáticas do VS Code (se usar Dev Containers)
├── .dockerignore        # Lista de arquivos que o Docker deve ignorar
├── .gitignore           # Lista de arquivos que o Git deve ignorar
├── Dockerfile           # Configuração da imagem Linux para o projeto
├── README.md            # Documentação, instruções e limitações
├── bash_structure.py    # Arquivo principal (Loop principal e Prompt)
├── commands.py          # Módulo com a lógica de fork, exec, wait, read/write
```

## Gerenciamento de Interface e Loop Principal

O arquivo bash_structure.py atua como o ponto de entrada do programa e é responsável pela interface com o usuário. Sua principal função é implementar o ciclo de vida do shell, conhecido como REPL (Read-Eval-Print Loop), garantindo que o prompt seja exibido continuamente e que os comandos sejam processados em sequência.

Abaixo, detalhamos as duas estruturas fundamentais deste módulo: a exibição do prompt via chamadas de sistema e o loop de execução.

### 1. Exibição do Prompt com os.write
Diferente de scripts Python comuns que utilizam print(), este projeto utiliza a syscall os.write para manipular a saída padrão (descritor de arquivo 1). Isso garante um controle de baixo nível sobre o buffer de saída.

```python
def exibir_prompt():
    # Define a mensagem do prompt. O método .encode('utf-8') é essencial
    # pois os.write opera com bytes brutos, não strings.
    mensagem = "> ".encode('utf-8') 
    
    # syscall write(fd, buffer)
    # fd=1 representa o STDOUT (Saída Padrão/Tela)
    os.write(1, mensagem)
```
Neste trecho, a função converte a string "> " para bytes antes de invocar a escrita direta no descritor de arquivo 1 (tela), cumprindo o requisito de manipulação direta de I/O.

### 2. O Loop Principal (REPL)
A função main() orquestra o funcionamento do shell. Ela mantém um laço infinito (while True) que só é interrompido quando um sinal de término é recebido. 

```python
def main():
    while True:
        # 1. Exibe o sinal de pronto para o usuário
        exibir_prompt()

        # 2. Delega a leitura e o parsing da entrada para o módulo commands
        # Retorna uma lista de tokens (ex: ['ls', '-l']) ou None
        comando_tokens = commands.ler_entrada()
        
        # 3. Critério de Parada: Se ler_entrada retornar None (ex: EOF ou erro grave),
        # o loop é quebrado e o shell encerrado.
        if comando_tokens is None:
            break
            
        # 4. Delega a execução do processo (fork/exec/wait)
        commands.executar_comando(comando_tokens)

if __name__ == "__main__":
    main()
```

-----

## Comandos

O arquivo `commands.py` é responsável por interpretar e executar as ações solicitadas. A função `executar_comando(args)` decide se o comando deve ser tratado internamente pelo Python (built-in) ou se deve ser executado como um processo do sistema operacional.

### 1. Comandos Internos (Built-ins)
Certos comandos precisam alterar o estado do próprio processo do shell (como mudar de diretório ou encerrar a execução). Eles são interceptados antes da criação de novos processos.

**Encerrando o Shell (`exit`)**
Quando o usuário digita `exit`, utilizamos `sys.exit(0)` para fechar o loop principal e encerrar o programa suavemente.

```python
if args[0] == 'exit':
    # Escreve mensagem de saída no descritor 1 (stdout)
    os.write(1, "Saindo do shell...\n".encode('utf-8'))
    sys.exit(0) # Encerra o interpretador Python
```

**Navegação de Diretórios** (`cd`) O comando `cd` não pode ser um binário externo, pois ele precisa mudar o diretório de trabalho do processo atual (o shell). Utilizamos `os.chdir` para isso.

```python
if args[0] == 'cd':
    try:
        # Se o usuário não passar argumentos (apenas 'cd'), vai para a HOME
        # Se passar argumentos (ex: 'cd /tmp'), usa args[1]
        path = args[1] if len(args) > 1 else os.environ.get('HOME', '.')
        
        # Syscall que altera o diretório de trabalho do processo atual
        os.chdir(path)
    except OSError as e:
        # Em caso de erro, como diretório inexistente
        msg = f"cd: erro ao mudar para '{path}': {e}\n".encode('utf-8')
        os.write(2, msg)
    return
```

### 2. Execução de Comandos Externos (Fork, Exec, Wait)
Para comandos do sistema (como ls, cat, echo), utilizamos o modelo clássico do Unix de criação de processos. Isso envolve três chamadas de sistema principais coordenadas dentro da função executar_comando:

1. `os.fork()`: Clona o processo atual.

2. `os.execvp()`: Substitui o processo clonado pelo comando desejado.

3. `os.wait()`: Faz o processo original esperar o término do clonado.

```python
try:
    # 1. FORK: Cria uma cópia idêntica do processo atual.
    # A partir daqui, temos dois processos rodando o mesmo código simultaneamente.
    # pid retorna 0 para o processo novo (Filho) e > 0 para o processo original (Pai).
    pid = os.fork() 

    if pid == 0: # Processo Filho
        try:
            # 2. EXEC: Substitui a código do filho pelo código/programa 'args[0]'
            # args é a lista de argumentos (ex: ['ls', '-la'])
            os.execvp(args[0], args)
        except OSError:
            # Se o exec falhar, imprime erro e mata o filho
            erro_msg = f"Erro: Comando '{args[0]}' não encontrado.\n".encode('utf-8')
            os.write(2, erro_msg)
            sys.exit(1) # Encerra o filho com erro
            
    elif pid > 0: # Processo Pai 
        # 3. WAIT: O Shell dorme e aguarda o filho (pid > 0) terminar sua execução.
        os.wait()
        
    else:
        # Caso onde o sistema operacional falha ao criar um processo
        os.write(2, "Erro crítico: Falha no fork.\n".encode('utf-8'))

except OSError as e:
    msg = f"Erro de sistema: {e}\n".encode('utf-8')
    os.write(2, msg)
```

-----

## 💻 Executando o Shell
1.  Abra o terminal integrado (`Ctrl + J`).
2.  Execute o shell com o comando
    ```bash
    python3 bash_structure.py
    ```
3.  O prompt ` >  ` aparecerá. Você pode testar comandos como:
      * `ls -l`
      * `echo Ola Mundo`
      * `cat README.md`
      * `exit` (para sair)
-----

## Exemplos

Abaixo apresentamos um log real de uso do shell, demonstrando a execução de comandos externos, manipulação de arquivos, navegação de diretórios e tratamento de erros. Note que os números exibidos antes da saída (ex: `9534`, `0`) correspondem aos PIDs dos processos criados via `fork()`.

```text
> echo Ola Mundo
9534
0
Ola Mundo

> ls -la
9588
0
total 24
drwxrwxrwx 1 root   root   4096 Nov 29 18:32 .
drwxr-xr-x 3 root   root   4096 Nov 21 19:20 ..
drwxrwxrwx 1 root   root   4096 Nov 21 19:37 .devcontainer
drwxrwxrwx 1 root   root   4096 Nov 29 18:32 .git
-rw-r--r-- 1 vscode vscode   18 Nov 21 19:37 .gitignore
-rw-r--r-- 1 vscode vscode 9624 Nov 29 19:21 README.md
-rwxrwxrwx 1 root   root    576 Nov 21 15:33 README.txt
drwxrwxrwx 1 root   root   4096 Nov 29 18:33 __pycache__
-rw-r--r-- 1 vscode vscode  695 Nov 21 22:31 bash_structure.py
-rwxrwxrwx 1 root   root   1822 Nov 29 18:32 commands.py
-rwxrwxrwx 1 root   root    128 Nov 21 15:33 test_token.py

> cat bash_structure.py
9934
0
import os, sys
import commands

def exibir_prompt():
    #podemos usar a write [https://docs.python.org/pt-br/3/library/os.html#os.write](https://docs.python.org/pt-br/3/library/os.html#os.write)
    mensagem = "> ".encode('utf-8') #write só escreve em bytes, então precisa pegar em string e transformar para bytes [https://docs.python.org/pt-br/3/library/stdtypes.html#str.encode](https://docs.python.org/pt-br/3/library/stdtypes.html#str.encode)
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

> pwd
10040
0
/workspaces/MATA58_Operating_System

> cd ..
> pwd
10125
0
/workspaces

> teste_erro
10196
0
Erro: Comando 'teste_erro' não encontrado.

> mkdir teste  
11332
0

> ls
11363
0
README.md  README.txt  __pycache__  bash_structure.py  commands.py  test_token.py  teste

> rm -d teste
0
11550

> ls -a
0
11561
.  ..  .devcontainer  .git  .gitignore  README.md  README.txt  __pycache__  bash_structure.py  commands.py  test_token.py

> exit
Saindo do shell...
```

## Dificuldades enfrentadas e aprendizados


## Video demonstração


