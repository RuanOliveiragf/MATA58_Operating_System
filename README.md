# Mini Shell - Projeto Integrador

Este projeto consiste no desenvolvimento de um mini interpretador de comandos (shell) em Python, simulando a execução de comandos em um terminal Linux e explorando chamadas de sistema (syscalls).

Como o projeto utiliza chamadas nativas de sistemas Unix (como `os.fork()`, `os.execvp()`, `os.wait()`), ele **não roda nativamente no Windows**. Este guia explica como configurar e rodar o projeto utilizando Docker e VS Code para garantir compatibilidade total.

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
      * Escolha a versão **3.10** (ou 3.9).
      * Não precisa marcar funcionalidades adicionais, apenas dê **OK**.
4.  Uma notificação aparecerá no canto inferior direito. Clique em **Reopen in Container**.
      * *Alternativa:* Pressione `F1` e digite `Dev Containers: Reopen in Container`.

> **Nota:** Na primeira vez, isso pode levar alguns minutos enquanto o VS Code baixa e constrói o ambiente Linux.

-----

## 💻 Executando o Shell

Quando o terminal do VS Code abrir novamente, você já estará dentro do ambiente Linux.

1.  Abra o terminal integrado (`Ctrl + '`).
2.  Execute o shell com o comando:
    ```bash
    python bash_structure.py
    ```
3.  O prompt ` >  ` aparecerá. Você pode testar comandos como:
      * `ls -l`
      * `echo Ola Mundo`
      * `cat README.md`
      * `exit` (para sair)

-----

## 📋 Detalhes da Implementação

Conforme requisitos do projeto[cite: 36], abaixo estão os detalhes técnicos:

### Chamadas de Sistema Utilizadas

  * **`os.fork()`**: Utilizada para criar um processo filho (cópia do shell) para executar o comando[cite: 14].
  * **`os.execvp()`**: Utilizada no processo filho para substituir o programa atual pelo comando digitado pelo usuário[cite: 15].
  * **`os.wait()`**: Utilizada pelo processo pai para aguardar a conclusão da execução do filho[cite: 16].
  * **`os.read()` / `os.write()`**: Utilizadas para manipulação de entrada e saída padrão, substituindo `input` e `print`[cite: 29, 53].
