os.read(fd, n): Lê n bytes de um descritor de arquivo (fd)
os.write(fd, str): Escreve bytes em um descritor de arquivo

0: Entrada padrão do teclado
1: Saída padrao - tela 
2: Erro padrão - tela de erro

PID é process identifier, o CPF do processo
pid = os.fork(), a variável pid não guarda o seu próprio número. Ela guarda o resultado da operação de clonagem.
se PID > 0: pai
se PID = 0: filho
se PID < 0: erro

eu preciso criar com o fork. Usando o exec eu clono e com o wait eu faço a transição