# Mini Shell - Projeto Integrador

Este projeto consiste no desenvolvimento de um mini interpretador de comandos (shell) em Python, simulando a execução de comandos em um terminal Linux e explorando chamadas de sistema (syscalls).

Como o projeto utiliza chamadas nativas de sistemas Unix (como `os.fork()`, `os.execvp()`, `os.wait()`), ele **não roda nativamente no Windows**. Uma alternativa para rodar o programa em Windows é utiliar a ferramente Dev Container do Visual Studio Code, que permite desenvolver dentro de um contêiner, que é um ambiente de desenvolvimento completo que roda em um sistema Unix. O guia abaixo explica como configurar e rodar o projeto utilizando Docker e VS Code para garantir compatibilidade total.

## 🚀 Pré-requisitos (Configuração Inicial)

Se você ainda não tem o ambiente configurado no Windows, siga os passos abaixo na ordem apresentada.

### 1. Instalar o WSL2 (Subsistema do Windows para Linux)

O Docker precisa do kernel do Linux para funcionar no Windows.

1.  Abra o **PowerShell** como Administrador.
2.  Execute o comando:
    ```powershell
    wsl --install
    ```
3.  **Reinicie o computador**.
4.  Após reiniciar, uma janela pode abrir instalando o Ubuntu. Apenas crie um usuário/senha qualquer e feche a janela.

### 2. Instalar o Docker Desktop

1.  Baixe e instale o [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/).
2.  Abra o aplicativo **Docker Desktop**.
3.  Aguarde até que a barra de status no canto inferior esquerdo fique **verde** ("Engine running").
4.  Talvez o instalador peça para reiniciar o computador.

### 3. Preparar o VS Code

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

## ⚙️ Estrutura do Projeto

O projeto adota uma estrutura modular para desacoplar a interface (Frontend) da lógica de sistema operacional (Backend).

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

1. Arquivo `bash_structure.py`

Este código é responsável por manter o shell rodando e implementando as funções definidas no arquivo `commands.py`

`exibir_prompt`: Exibe o usuário e o diretório atual utilizando a syscall `os.getcwd()` para obter o caminho e códigos de escape ANSI para as cores.

`main`: Mantém o shell ativo indefinidamente. A cada iteração, chama `commands.ler_entrada()` para obter o input e `commands.executar_comando()` para processá-lo. O loop só é quebrado quando um sinal de término (como `None` vindo do `ler_entrada`) é recebido.

2. `commands.py`

Contém a lógica e as chamadas de sistema. Possui a lógica para a função de ler entrada, e exercutar o comando, sendo que, dentro de cada função (como o caso da função `ler_entrada()` que será mais bem especificada posteriormente) há lógicas próprias como as metodologias usadas para fazer o autocompetar, comuns a shells como power shell e git bash.

`ler_entrada()`: Lê os comandos do usuário. Esta função lê byte a byte para permitir recursos como Autocomplete.

`executar_comando(args)`: Decide se o comando é interno (built-in) ou externo e realiza as chamadas de sistema apropriadas (`fork`, `exec`, `chdir`, etc.).

### Detalhamento Técnico e Funcionalidades Avançadas

1. Comandos Internos

Certos comandos precisam ser executados pelo próprio processo do shell, e não por um processo filho, para que suas alterações persistam, para este trabalho foram implementados dois, sendo um para a navegação entre diretórios (`cd`), e a saida que é o `exit`.

Navegação de Diretórios (`cd`):

Implementação: Utiliza a syscall `os.chdir(path)`.

Detalhe: Se o `cd` fosse executado em um processo filho (com `fork`), apenas o filho mudaria de pasta. Quando o filho morresse, o shell (pai) continuaria na pasta antiga. Por isso, o `cd` é interceptado e executado diretamente no processo pai.

`exit`:

Implementação: Utiliza `sys.exit(0)`.

Detalhe: Encerra o interpretador Python de forma limpa, retornando o código de status 0 (sucesso) para o sistema operacional.

2. Leitura em Modo Raw e Autocomplete utilizando a tecla `TAB`

Para implementar o Autocomplete, não é possível utiliazr o modo canonico, sendo assim necessario mudar para o modo raw uma vez que precisamos capturar aquilo que é digitado logo após o usuário pressionar a tecla, ao invés de capturar todo o conjunto de caracteres no final após pressionar a tecla enter.

Manipulação de TTY (`termios` e `tty`): Utilizamos `tty.setraw(0)` para colocar o terminal em modo raw. Isso permite ler cada tecla (`os.read(0, 1)`) no instante em que é pressionada.

Lógica do `TAB`: Ao detectar o byte `\x09` (`TAB`), o shell analisa o buffer atual, varre o diretório com `os.listdir()` e completa automaticamente o nome do arquivo ou pasta correspondente.

Edição Manual: Como o modo Raw desativa o processamento padrão, reimplementamos manualmente a lógica do Backspace (`\x7f` e `\x08`) para apagar caracteres do buffer e atualizar a tela visualmente.

3. Redirecionamento de Saída (`dup2`)

O shell suporta o operador `>` para salvar a saída de comandos em arquivos (ex: `ls > log.txt`).

Detecção: O parser identifica o símbolo `>` e o nome do arquivo de destino.

Manipulação dos `fd`'s:

Abre o arquivo alvo com `os.open`, obtendo um novo File Descriptor (ex: FD 3).

Utiliza a syscall `os.dup2(fd_arquivo, 1)` para substituir a Saída Padrão (FD 1 - Tela) pelo FD do arquivo.

Quando o comando (ex: `ls`) é executado, ele escreve no FD 1, mas os dados são desviados transparentemente para o arquivo.

4. Gerenciamento de Processos usando comandos externos

O ciclo de vida clássico do Unix é mantido para execução de comandos externos (como `ls`, `cat`, `echo`):

`os.fork()`: Cria um processo clone (Filho).

`os.execvp()`: O Filho substitui sua imagem de memória pelo programa desejado.

`os.wait()`: O Pai suspende a execução até que o Filho termine.

Chamadas de sistemas utilizadas:

Gerenciamento de Processos: `fork`, `execvp`, `wait`.

Sistema de Arquivos: `chdir` (`cd`), `getcwd` (prompt), `listdir` (autocomplete), `open` (redirecionamento).

Entrada/Saída (I/O): `read`, `write`, `dup2` (redirecionamento), `close`.

Exemplos de Comandos Testados e Saídas

Abaixo, um log demonstrando as capacidades do shell, incluindo cores, autocomplete e redirecionamento.

## Exemplos

Abaixo encontra-se o um exemplo de utilização do shell. É possível encontrar comandos como "`cd`" e "`exit`", os quais foram implementados manualmente, e também comandos como `ls`, e também `echo`. Também é demonstado a utilização da função `dup2()` atraves da linha "`> echo Texto da Silva > texto_da_silva.txt`" onde a saida de dados que seria exibida vinda do comando `echo`, é na verdade implementada no arquivo txt gerado (`texto_da_silva.txt`). Além disso, foram testados outros comandos padrão do Ubunto como `cat`, `pwd`, `mkidr`, `rm` e `rn -d`.

```text
> echo Ola Mundo
Ola Mundo

> ls -la
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
/workspaces/MATA58_Operating_System

> cd ..
> pwd
/workspaces

> teste_erro
Erro: Comando 'teste_erro' não encontrado.

> mkdir teste  

> ls
README.md  README.txt  __pycache__  bash_structure.py  commands.py  test_token.py  teste

> rm -d teste

> ls -a
.  ..  .devcontainer  .git  .gitignore  README.md  README.txt  __pycache__  bash_structure.py  commands.py  test_token.py

> ls
README.md  README.txt  __pycache__  bash_structure.py  commands.py  test_token.py  testeDemonstacao.txt

> echo Teste da Silva > texto_da_silva.txt

> ls
README.md  README.txt  __pycache__  bash_structure.py  commands.py  test_token.py  testeDemonstacao.txt  texto_da_silva.txt

> cat texto_da_silva.txt 
Teste da Silva

> rm texto_da_silva.txt 

> ls
README.md  README.txt  __pycache__  bash_structure.py  commands.py  test_token.py  testeDemonstacao.txt

> exit
Saindo do shell...
```

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

## 📌Dificuldades enfrentadas e aprendizados
O primeiro obstáculo se deu quando foi necessário criar a funcionalidade de autocomplete. De antemão foi o shell foi feito seguindo o modo canônico, ou seja, o terminal funcionava como uma inteface não acessando direto, assim, o programa. Para que fosse possível implementarmos a funcionalidade de autocomplete, o que é essencial para uma melhor interação com o shell, foi necessário alterar para o modo Raw (ou modo cru).

Ao alterarmos para esse modo, o processo de escrita dos caracteres comuns e o uso de teclas especiais como `Backspace`, e `tab` (fundamentais para a utilização do shell) se dá de forma diferente, sendo necessário assim implementarmos de forma direta no código. Assim, foi necessario a utilização da tabela ASCII para a identificação de tais teclas além de comandos e atalhos especiais como `Ctrl` + `c`.

Para que fosse possível capturarmos tecla a tecla, ao invés de capturar todo o conjunto de caracteres e envia-los após apertar a tecla `Enter`, foi necessário salvar as configurações do modo canônico, mudar as configurações para o modo raw capturar a tecla, e então devolver as configurações originais. Para isso foi criada a função `obterCaratere()`. O entendimento dessa dinâmica entre o modo canônico e o modo raw foi de fundamental de importância para a construção do trabalho.

Sob esse viés, outro ponto a destacar-se pela necessidade de um conhecimento relativamente mais profundo e especifico foi quanto a questão da utilização da função `dup2()`. Para que fosse possível implementar tal "técnica" no shell, foi necessário fazer uma manipulação com os caracteres digitados no terminal de modo a capturar exatamente as palavras necessarias para se pudesse passar o `fd` correto na função `dup2()`, de modo a permitir a troca entre o `fd` capturado, e o `fd 1` que é referente a `stdin`

## 🎥 Video demonstração

https://youtu.be/bebk-TWM6EA