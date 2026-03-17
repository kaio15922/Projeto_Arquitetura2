import os

def processar_ula(A, B, f0, f1, ena, enb, inva, inc):

    # processamento dos enable's
    a_hab = A if ena == 1 else 0
    b_hab = B if enb == 1 else 0
    a_final = (a_hab ^ 0xFFFFFFFF) if inva == 1 else a_hab

    # selecionador das operações
    if f0 == 0 and f1 == 0:  # AND
        S = a_final & b_hab
        co = 0
    elif f0 == 0 and f1 == 1:  # OR
        S = a_final | b_hab
        co = 0
    elif f0 == 1 and f1 == 0:  # NOT B
        S = (b_hab ^ 0xFFFFFFFF) & 0xFFFFFFFF
        co = 0
    else:  # SOMA (F0=1, F1=1)
        res_soma = a_final + b_hab + inc
        S = res_soma & 0xFFFFFFFF
        co = 1 if res_soma > 0xFFFFFFFF else 0

    return S, co


def executar_tarefa1(sll8, sra1, f0, f1, ena, enb, inva, inc, A, B):
    # 1. Chama a função original
    # IMPORTANTE: Garanta que processar_ula retorne s_ula já com & 0xFFFFFFFF
    s_ula, vai_um = processar_ula(A, B, f0, f1, ena, enb, inva, inc)

    # Forçamos s_ula a ser interpretado como 32 bits antes do deslocamento
    s_ula &= 0xFFFFFFFF

    # 2. Lógica do Deslocador (Shifter)
    s_deslocada = s_ula

    if sll8 == 1:
        # Deslocamento lógico para esquerda 8 bits
        s_deslocada = (s_ula << 8) & 0xFFFFFFFF
    elif sra1 == 1:
        # Deslocamento aritmético para direita 1 bit
        # Se o bit 31 estiver ativo, o número é "negativo" no Mic-1
        if s_ula & 0x80000000:
            s_deslocada = (s_ula >> 1) | 0x80000000
        else:
            s_deslocada = s_ula >> 1

    # Garante que o resultado final seja 32 bits após qualquer deslocamento
    s_deslocada &= 0xFFFFFFFF

    # 3. Definição das novas flags N e Z (baseadas no valor deslocado)
    z = 1 if s_deslocada == 0 else 0
    # N é 1 se o bit mais significativo (31) for 1
    n = 1 if (s_deslocada & 0x80000000) else 0

    return s_deslocada, vai_um, n, z


# =====================================================================
# TAREFA 2: CONTROLE DE DATAPATH E BARRAMENTOS
# =====================================================================

def executar_tarefa2_registrador(escolhido, OPC, TOS, CPP, LV, SP, MBR, PC, MDR):
    """
    Decodificador do Multiplexador do Barramento B.
    Mapeia o sinal de controle de 4 bits para o registrador correspondente.
    Retorna uma tupla contendo o mnemônico do registrador e seu valor em 32 bits.
    """
    if escolhido == 0: return "mdr", MDR
    elif escolhido == 1: return "pc", PC
    elif escolhido == 2: 
        # Seletor 2 (0010): Registrador MBR com Extensão de Zero (Zero Extension).
        return "mbr", MBR 
    elif escolhido == 3: 
        # Seletor 3 (0011): Registrador MBR com Extensão de Sinal (Sign Extension).
        # Verifica o MSB (bit 7) do MBR via máscara 0x80. Aplica OR com 0xFFFFFF00 se negativo.
        if MBR & 0x80: return "mbru", (MBR | 0xFFFFFF00) 
        else: return "mbru", MBR
    elif escolhido == 4: return "sp", SP
    elif escolhido == 5: return "lv", LV
    elif escolhido == 6: return "cpp", CPP
    elif escolhido == 7: return "tos", TOS
    elif escolhido == 8: return "opc", OPC
    else: return "none", 0


def escrever_barramento_c(controle_c_str, s_d, H, OPC, TOS, CPP, LV, SP, PC, MDR, MAR):
    """
    Lógica de Write Enable (WE) guiada pelo Barramento C.
    Mapeia o sinal de controle de 9 bits para os registradores de destino.
    Múltiplos registradores podem ser acionados simultaneamente no mesmo ciclo.
    """
    escritos_log = [] 
    
    if controle_c_str[0] == '1': 
        H = s_d; escritos_log.append("h")
    if controle_c_str[1] == '1': 
        OPC = s_d; escritos_log.append("opc")
    if controle_c_str[2] == '1': 
        TOS = s_d; escritos_log.append("tos")
    if controle_c_str[3] == '1': 
        CPP = s_d; escritos_log.append("cpp")
    if controle_c_str[4] == '1': 
        LV = s_d; escritos_log.append("lv")
    if controle_c_str[5] == '1': 
        SP = s_d; escritos_log.append("sp")
    if controle_c_str[6] == '1': 
        PC = s_d; escritos_log.append("pc")
    if controle_c_str[7] == '1': 
        MDR = s_d; escritos_log.append("mdr")
    if controle_c_str[8] == '1': 
        MAR = s_d; escritos_log.append("mar")
    
    return escritos_log, H, OPC, TOS, CPP, LV, SP, PC, MDR, MAR


def carregar_estado_inicial(nome_arquivo):
    """
    Rotina de inicialização de estado da arquitetura.
    Realiza o parsing do arquivo de dump de registradores, convertendo strings binárias 
    para inteiros na base 2.
    """
    H = OPC = TOS = CPP = LV = SP = PC = MDR = MAR = MBR = 0
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, 'r') as f:
            for linha in f:
                if "=" in linha:
                    partes = linha.split("=")
                    nome = partes[0].strip().lower()
                    valor = int(partes[1].strip(), 2)
                    
                    if nome == "h": H = valor
                    elif nome == "opc": OPC = valor
                    elif nome == "tos": TOS = valor
                    elif nome == "cpp": CPP = valor
                    elif nome == "lv": LV = valor
                    elif nome == "sp": SP = valor
                    elif nome == "pc": PC = valor
                    elif nome == "mdr": MDR = valor
                    elif nome == "mar": MAR = valor
                    elif nome == "mbr": MBR = valor
    return H, OPC, TOS, CPP, LV, SP, PC, MDR, MAR, MBR


def formatar_regs(MAR, MDR, PC, MBR, SP, LV, CPP, TOS, OPC, H):
    """
    Formatação do dump de registradores para o log de execução.
    Define o padding binário adequado para palavras de 32 bits e 8 bits (MBR).
    """
    return (f"mar = {MAR:032b}\nmdr = {MDR:032b}\npc = {PC:032b}\nmbr = {MBR:08b}\n"
            f"sp = {SP:032b}\nlv = {LV:032b}\ncpp = {CPP:032b}\ntos = {TOS:032b}\n"
            f"opc = {OPC:032b}\nh = {H:032b}\n")

def formatar_memoria(memoria):
    texto = "=====================================================\n"
    for valor in memoria:
        texto += f"{valor:032b}\n"
    texto += "=====================================================\n"
    return texto

def executar_simulador():
    arq_regs = input("Arquivo de Registradores Iniciais (Etapa 3): ").strip()
    arq_etapa3 = input("Arquivo de Instruções 23 bits (Etapa 3): ").strip()
    arq_dados3 = input("Arquivo de memória (Etapa 3): ").strip()

    if os.path.exists(arq_etapa3) and os.path.exists(arq_regs):
        with open(arq_etapa3, "r") as ent, open("log_etapa3.txt", "w") as log:
            
            # Inicialização do Datapath
            H, OPC, TOS, CPP, LV, SP, PC, MDR, MAR, MBR = carregar_estado_inicial(arq_regs)
            
            # Abrindo o arquivo dos dados
            memoria = []
            with open(arq_dados3, "r") as f:
                for linha in f:
                    memoria.append(int(linha.strip(), 2))

            # Header do arquivo de Log
            log.write("============================================================\n")
            log.write("Initial memory state\n")
            log.write(formatar_memoria(memoria))
            log.write("=====================================================\n")
            log.write("> Initial register states\n")
            log.write(formatar_regs(MAR, MDR, PC, MBR, SP, LV, CPP, TOS, OPC, H))
            log.write("\n=====================================================\n")
            log.write("Start of program\n")
            log.write("=====================================================\n")

            pc_count = 1

            # Ciclo de Instrução (Fetch, Decode, Execute)
            for linha in ent:
                ir = linha.strip()
                if not ir or len(ir) != 23: 
                    continue

                # Decodificação do Instruction Register (IR) em sinais de controle
                controle_ula = ir[0:8]
                controle_c = ir[8:17]
                controle_memoria = ir[17:19]
                controle_b_str = ir[19:23]

                log.write(f"Cycle {pc_count}\n")
                log.write(f"ir = {controle_ula} {controle_c} {controle_memoria} {controle_b_str}\n\n")

                # Roteamento de Entradas da ULA
                # A_val é hardcoded para o registrador H. B_val é roteado pelo Barramento B.
                A_val = H
                nome_b, B_val = executar_tarefa2_registrador(
                    int(controle_b_str, 2), OPC, TOS, CPP, LV, SP, MBR, PC, MDR
                )

                # Parsing prévio dos destinos do Barramento C para registro de Log
                nomes_escritos_c = []
                ordem_bits = ["h", "opc", "tos", "cpp", "lv", "sp", "pc", "mdr", "mar"]
                for i, bit in enumerate(controle_c):
                    if bit == '1': nomes_escritos_c.append(ordem_bits[i])

                log.write(f"b_bus = {nome_b}\n")
                log.write(f"c_bus = {', '.join(nomes_escritos_c) if nomes_escritos_c else 'none'}\n\n")

                # Dump de estado pré-execução
                log.write("> Registers before instruction\n")
                regs_antes = formatar_regs(MAR, MDR, PC, MBR, SP, LV, CPP, TOS, OPC, H)
                log.write(regs_antes)

                # Estágio de Execução (ULA + Shifter)
                s_d, co, n, z = executar_tarefa1(
                    int(controle_ula[0]), int(controle_ula[1]), int(controle_ula[2]),
                    int(controle_ula[3]), int(controle_ula[4]), int(controle_ula[5]),
                    int(controle_ula[6]), int(controle_ula[7]),
                    A_val, B_val
                )

                # Estágio de Write-Back (Atualização de registradores via Barramento C)
                _, H, OPC, TOS, CPP, LV, SP, PC, MDR, MAR = escrever_barramento_c(
                    controle_c, s_d, H, OPC, TOS, CPP, LV, SP, PC, MDR, MAR
                )

                # Aqui os dois if. Eh so isso ai
                write = int(controle_memoria[0])
                read = int(controle_memoria[1])

                if write == 1:
                    if 0 <= MAR < len(memoria):
                        memoria[MAR] = MDR

                elif read == 1:
                    if 0 <= MAR < len(memoria):
                        MDR = memoria[MAR]

                # Dump de estado pós-execução
                log.write("\n> Registers after instruction\n")
                log.write(formatar_regs(MAR, MDR, PC, MBR, SP, LV, CPP, TOS, OPC, H))
                log.write("\n> Memory after instruction\n")
                log.write(formatar_memoria(memoria))
                log.write("=====================================================\n")
                
                pc_count += 1
            
            log.write(f"Cycle {pc_count}\nNo more lines, EOP.\n")

if __name__ == "__main__":
    executar_simulador()