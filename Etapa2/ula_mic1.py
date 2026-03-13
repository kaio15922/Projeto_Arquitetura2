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


def executar_simulador():
    arq_etapa1 = input("Arquivo Etapa 1: ").strip()
    arq_etapa2 = input("Arquivo Etapa 2: ").strip()

    # Valores iniciais do exemplo
    A_val = 0xFFFFFFFF
    B_val = 0x00000001

    # --- ETAPA 1 ---
    if os.path.exists(arq_etapa1):
        with open(arq_etapa1, "r") as ent, open("log_etapa1.txt", "w") as log:
            log.write(f"b = {B_val:032b}\na = {A_val:032b}\n\nStart of Program\n")
            cycle: int = 0
            for pc, linha in enumerate(ent, 1):
                ir = linha.strip()
                if not ir:
                    continue
                # Passando os 6 bits da etapa 1
                s, co = processar_ula(
                    A_val,
                    B_val,
                    int(ir[0]),
                    int(ir[1]),
                    int(ir[2]),
                    int(ir[3]),
                    int(ir[4]),
                    int(ir[5]),
                )
                log.write("=" * 60 + f"\nCycle {pc}\n\nPC = {pc}\nIR = {ir}\n")
                log.write(
                    f"b = {B_val:032b}\na = {A_val:032b}\ns = {s:032b}\nco = {co}\n"
                )
                cycle = pc
            cycle += 1
            log.write("=" * 60 + f"\nCycle {cycle}\n> Line is empty, EOP.\n")

    # --- ETAPA 2 ---
    if os.path.exists(arq_etapa2):
        with open(arq_etapa2, "r") as ent, open("log_etapa2.txt", "w") as log:
            log.write(f"b = {B_val:032b}\na = {A_val:032b}\n\nStart of Program\n")
            for pc, linha in enumerate(ent, 1):
                ir = linha.strip()
                if not ir:
                    continue
                # Passando os 8 bits para a tarefa 1
                s_d, co, n, z = executar_tarefa1(
                    int(ir[0]),
                    int(ir[1]),
                    int(ir[2]),
                    int(ir[3]),
                    int(ir[4]),
                    int(ir[5]),
                    int(ir[6]),
                    int(ir[7]),
                    A_val,
                    B_val,
                )
                log.write("=" * 60 + f"\nCycle {pc}\n\nPC = {pc}\nIR = {ir}\n")
                log.write(
                    f"b = {B_val:032b}\na = {A_val:032b}\ns = {s_d:032b}\nco = {co}\n"
                )
                log.write(f"N = {n} | Z = {z}\n")
            log.write("=" * 60 + "\n")


if __name__ == "__main__":
    executar_simulador()
