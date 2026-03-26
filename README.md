
---

# Simulador Mic-1 Modificada (UFPB)

Este projeto consiste na implementação de um simulador de 32 bits para a microarquitetura **Mic-1**, desenvolvido para a disciplina de Arquitetura de Computadores II. O sistema emula o funcionamento do hardware, processando instruções da ISA **IJVM** através de sequências de microinstruções.



## 🏗️ Visão Geral do Sistema

O simulador funciona como uma máquina virtual que interpreta o caminho de dados da Mic-1. Ele é capaz de realizar desde operações lógicas elementares na ULA até a gestão complexa de uma pilha de execução (Stack) na memória de dados.

### Processo de Tradução (Micro-Montador)
O arquivo `instrucoes.txt` contém mnemónicos da IJVM que são processados pela função `traduzir_instrucao`. Esta função atua como um tradutor que gera blocos de microinstruções de 23 bits, responsáveis por controlar os sinais de hardware em cada ciclo de clock.

## 🕹️ Instruções Suportadas

* **ILOAD x**: Recupera uma variável local da memória. O simulador utiliza o registrador `LV` como base e incrementa o registrador `H` através de um ciclo repetitivo até atingir o índice `x`.
* **DUP**: Duplica o valor presente no topo da pilha (`TOS`). O ponteiro de pilha (`SP`) é incrementado e o valor é escrito na nova posição de memória.
* **BIPUSH byte**: Coloca um valor constante de 8 bits no topo da pilha. Esta instrução utiliza um **caminho de bypass**: o byte é injetado diretamente no registrador `MBR` e depois no `H`, ignorando a lógica aritmética da ULA.

---

## 🔬 Detalhamento da Microinstrução (23 bits)

Cada linha de execução no núcleo do simulador é composta por 23 bits de controle, divididos da seguinte forma:

1.  **ULA (8 bits)**: Define a operação (AND, OR, NOT, SOMA) e ativa os sinais do **Shifter** (SLL8 para deslocar 8 bits à esquerda ou SRA1 para deslocar 1 bit à direita com preservação de sinal).
2.  **Barramento C (9 bits)**: Funciona como um seletor de escrita. Cada bit corresponde a um registrador (H, OPC, TOS, CPP, LV, SP, PC, MDR, MAR). Se o bit for `1`, o registrador recebe o dado da ULA.
3.  **Memória (2 bits)**: Controla os sinais de `READ` (Leitura) e `WRITE` (Escrita).
    * *Nota Especial*: Quando ambos os bits são `1`, o simulador ativa a lógica de carga direta para o `BIPUSH`.
4.  **Barramento B (4 bits)**: Seleciona qual registrador terá o seu conteúdo lido e enviado para a entrada da ULA.

---

## 🔄 Fluxo de Execução

O ciclo de vida de uma instrução no simulador segue quatro etapas principais:

1.  **Inicialização (LOAD)**: O sistema lê o estado inicial da memória (`dados.txt`) e dos registradores (`registradores.txt`).
2.  **Descodificação (DECODE)**: A microinstrução de 23 bits é lida e os sinais de controle são distribuídos para os componentes virtuais.
3.  **Execução (EXECUTE)**:
    * O dado sai do registrador escolhido pelo **Barramento B**.
    * A **ULA** e o **Shifter** processam a informação.
    * O **Barramento C** grava o resultado nos destinos selecionados.
    * Se houver sinal de memória, o `MDR` ou `MAR` interagem com a RAM virtual.
4.  **Registo (LOG)**: O simulador grava o estado de todos os componentes no ficheiro `log_entregavel.txt` para permitir a auditoria de cada ciclo.

## 📋 Como Executar

1.  Garanta que os ficheiros de entrada (`instrucoes.txt`, `dados_entregavel.txt` e `registradores_entregavel.txt`) estão na pasta raiz.
2.  Execute o script:
    ```bash
    python simulador.py
    ```
3.  Verifique o ficheiro `log_entregavel.txt` para validar a execução.

---
