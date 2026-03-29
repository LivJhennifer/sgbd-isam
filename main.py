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
    
# 5. Executa as Remoções Obrigatórias
print("\n Remoções")
# Conforme Tabela de Remoções
remocoes_exigidas = [27, 44, 67, 83, 145]

for chave in remocoes_exigidas:
    meu_indice.delete(chave)

# 6. Exibição de Métricas Finais (Conforme Tabela do Trabalho)
print("\nSÍNTESE DE MÉTRICAS EXPERIMENTAIS")

# 1 - Quantidade de páginas folha (Estático conforme build inicial)
qtd_folhas = len(meu_indice.leaves_in_order)
print(f"Quantidade de páginas folha: {qtd_folhas}")
print(f"  -> Objetivo: Avaliar a estrutura principal ocupada pelos registros primários.")

# 2 - Quantidade de páginas de overflow
print(f"\nQuantidade de páginas de overflow: {meu_indice.metrics['overflow_criadas']}")
print(f"  -> Objetivo: Medir o impacto das inserções após o preenchimento das folhas.")

# 3 - Tamanho médio das cadeias de overflow
total_ov = sum(leaf.count_overflow_pages() for leaf in meu_indice.leaves_in_order)
media_ov = total_ov / qtd_folhas
print(f"\nTamanho médio das cadeias de overflow: {media_ov:.2f}")
print(f"  -> Objetivo: Avaliar a degradação potencial da busca.")

# 4 - Quantidade de registros removidos
print(f"\nQuantidade de registros removidos: {meu_indice.metrics['remocoes']}")
print(f"  -> Objetivo: Observar a manutenção das páginas e a eventual liberação de overflow.")

# 5 - Menção ao Custo (já impresso durante as buscas)
print(f"\nCusto aproximado das buscas: Observado nos logs anteriores")
print(f"  -> Objetivo: Comparar o efeito do crescimento das cadeias de overflow.")
