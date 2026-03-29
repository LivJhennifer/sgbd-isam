# Importa a classe principal do arquivo isam.py
from isam import ISAM

# 1. Inicializa a estrutura ISAM
meu_indice = ISAM()

# 2. Executa as Inserções Obrigatórias
# Lista das inserções exigidas no trabalho
insercoes_exigidas = [
    (18, "R18"), (22, "R22"), (27, "R27"), (35, "R35"),
    (41, "R41"), (44, "R44"), (63, "R63"), (67, "R67"),
    (83, "R83"), (86, "R86"), (121, "R121"), (145, "R145")
]

for chave, valor in insercoes_exigidas:
    meu_indice.insert(chave, valor)

# 3. Buscas por Igualdade exigidas
print("\n Busca por Igualdade")
chaves_igualdade = [22, 35, 44, 90]

for chave in chaves_igualdade:
    reg, custo, caminho = meu_indice.search_equality(chave)
    print(f"\nbuscar({chave}):")
    print(f"  Resultado: {reg if reg else 'Registro não encontrado'}")
    print(f"  Custo: {custo} nós visitados")
    print(f"  Caminho percorrido: {' -> '.join(caminho)}")

# 4. Buscas por Intervalo exigidas
print("\n Busca por intervalo")
intervalos = [(20, 50), (60, 90), (120, 150)]

for v_min, v_max in intervalos:
    regs, custo, caminho = meu_indice.search_interval(v_min, v_max)
    print(f"\nbuscar_intervalo({v_min}, {v_max}):")
    print(f"  Registros coletados: {regs}")
    print(f"  Custo: {custo} nós visitados")
    print(f"  Caminho percorrido: {' -> '.join(caminho)}")