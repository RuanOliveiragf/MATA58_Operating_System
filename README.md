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
├── commands.py          # Módulo com a lógica de fork, exec, wait, read/write e cd
```

## Gerenciamento de Interface e Loop Principal

O arquivo bash_structure.py atua como o ponto de entrada do programa e é responsável pela interface com o usuário. Sua principal função é implementar o ciclo de vida do shell, conhecido como REPL (Read-Eval-Print Loop), garantindo que o prompt seja exibido continuamente e que os comandos sejam processados em sequência.

Abaixo, detalhamos as duas estruturas fundamentais deste módulo: a exibição do prompt via chamadas de sistema e o loop de execução.

1. Exibição do Prompt com os.write
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

2. O Loop Principal (REPL)
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


## Dificuldades enfrentadas e aprendizados


## Video demonstração


