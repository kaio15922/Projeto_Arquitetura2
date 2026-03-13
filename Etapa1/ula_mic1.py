import os

def processar_ula(A, B, f0, f1, ena, enb, inva, inc):
  
    #processamento dos enable's
    a_hab = A if ena == 1 else 0
    b_hab = B if enb == 1 else 0
    a_final = a_hab ^ inva
    
    #definindo todas as operações possíveis
    res_and = a_final & b_hab
    res_or  = a_final | b_hab
    res_not_b = 1 - b_hab
    soma_bit = a_final ^ b_hab ^ inc
    vai_um = (a_final & b_hab) | (inc & (a_final ^ b_hab))
    
    #selecionador das operações
    if f0 == 0 and f1 == 0: S = res_and
    elif f0 == 0 and f1 == 1: S = res_or
    elif f0 == 1 and f1 == 0: S = res_not_b
    else: S = soma_bit
        
    return S, vai_um

def executar_simulador():
    
    arq_in = input("Nome do arquivo de entrada: ").strip()
    arq_log = input("Nome do arquivo de log: ").strip()
    
    #definindo valores iniciais para A, B e PC
    A, B, pc = 1, 0, 1


    if not os.path.exists(arq_in):
        print(f"\nO arquivo '{arq_in}' não foi encontrado na pasta atual.")
        return 

    try:
        with open(arq_in, 'r') as arq_entrada, open(arq_log, 'w') as log_saida:
            log_saida.write("PC \t| IR \t\t| A \t| B \t| S \t| Vai-um\n")
            log_saida.write("-" * 60 + "\n")
            
            for linha in arq_entrada:
                ir = linha.strip()

                #copiando cada bit como instrução
                f0   = int(ir[0])
                f1   = int(ir[1])
                ena  = int(ir[2])
                enb  = int(ir[3])
                inva = int(ir[4])
                inc  = int(ir[5])
                
                s, v_um = processar_ula(A, B, f0, f1, ena, enb, inva, inc)
                
                log_saida.write(f"{pc:02d} \t| {ir} \t| {A} \t| {B} \t| {s} \t| {v_um}\n")
                pc += 1

    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    executar_simulador()