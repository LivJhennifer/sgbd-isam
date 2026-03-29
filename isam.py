"""
ISAM - Indexed Sequential Access Method
Trabalho Prático de SGBD
 
Estrutura:
  - Índice estático com dois níveis intermediários acima das folhas
  - Folhas primárias com capacidade limitada (PAGE_SIZE registros)
  - Páginas de overflow encadeadas quando a folha primária está cheia
"""
 

# CONFIGURAÇÃO

 
PAGE_SIZE = 2   # Capacidade máxima de cada página (primária ou overflow)
 

# CLASSES DE ESTRUTURA

 
class OverflowPage:
    """
    Página de overflow: criada quando uma folha primária (ou overflow anterior)
    está cheia. Forma uma lista encadeada a partir da folha.
    """
    def __init__(self):
        self.records = []           # Lista de (chave, dado)
        self.next = None            # Ponteiro para a próxima página de overflow
 
    def is_full(self):
        return len(self.records) >= PAGE_SIZE
 
    def __repr__(self):
        return f"OV{self.records}" # Python chama esse método para saber o que exibir
 
 
class LeafPage:
    """
    Página folha primária: armazena registros ordenados.
    Quando cheia, cria ou usa páginas de overflow associadas.
    """
    def __init__(self, name):
        self.name = name            # Nome para identificação (ex: "Folha 1")
        self.records = []           # Lista de (chave, dado)
        self.overflow_head = None   # Primeira página de overflow desta folha
 
    def is_full(self):
        return len(self.records) >= PAGE_SIZE
 
    def get_all_records(self):
        """Retorna todos os registros: primários + overflow (em ordem de cadeia)."""
        result = list(self.records)
        ov = self.overflow_head
        while ov:
            result.extend(ov.records)
            ov = ov.next
        return result
 
    def count_overflow_pages(self):
        """Conta quantas páginas de overflow existem nesta cadeia."""
        count = 0
        ov = self.overflow_head
        while ov:
            count += 1
            ov = ov.next
        return count
 
    def __repr__(self):
        return f"{self.name}{self.records}"
 
 
class IndexNode:
    """
    Nó de índice intermediário (estático).
    Armazena chaves separadoras e ponteiros para os filhos.
    Nunca é modificado após a criação da estrutura.
    """
    def __init__(self, keys, children):
        """
        keys:     lista de chaves separadoras  ex: [20, 33]
        children: lista de filhos (IndexNode ou LeafPage)
                  len(children) == len(keys) + 1
        """
        self.keys = keys
        self.children = children
 
    def find_child(self, key):
        """
        Navega pelos separadores para encontrar o filho correto.
        Retorna também o caminho percorrido (para contagem de custo).
        """
        for i, separator in enumerate(self.keys):
            if key < separator:
                return self.children[i]
        return self.children[-1]   # Maior que todos os separadores → último filho
 
  
class ISAM:
    """
    O índice é construído uma vez e nunca é reorganizado.
    Inserções nas folhas cheias geram páginas de overflow.
    """
 
    def __init__(self):
        self._build_initial_structure()
        # Métricas acumuladas
        self.metrics = {
            "insercoes": 0,
            "remocoes": 0,
            "overflow_criadas": 0,
            "overflow_liberadas": 0,
        }
 
    def _build_initial_structure(self):
        """
 
        Raiz: 40
          Esquerda (< 40): nó com chaves [20, 33]
            < 20  → Folha A [10, 15]
            20-32 → Folha B [20, 27]
            >= 33 → Folha C [33, 37]
          Direita (>= 40): nó com chaves [51, 63]
            < 51  → Folha D [40, 46]
            51-62 → Folha E [51, 55]
            >= 63 → Folha F [63, 97]
        """
 
        # --- Folhas primárias com seus registros iniciais ---
        self.leaf_A = LeafPage("Folha A")
        self.leaf_A.records = [(10, "R10"), (15, "R15")]
 
        self.leaf_B = LeafPage("Folha B")
        self.leaf_B.records = [(20, "R20"), (27, "R27")]
 
        self.leaf_C = LeafPage("Folha C")
        self.leaf_C.records = [(33, "R33"), (37, "R37")]
 
        self.leaf_D = LeafPage("Folha D")
        self.leaf_D.records = [(40, "R40"), (46, "R46")]
 
        self.leaf_E = LeafPage("Folha E")
        self.leaf_E.records = [(51, "R51"), (55, "R55")]
 
        self.leaf_F = LeafPage("Folha F")
        self.leaf_F.records = [(63, "R63"), (97, "R97")]
 
        # Nível intermediário 2 (aponta para as folhas)
        # Nó esquerdo do nível 2: separadores 20 e 33
        self.node_left = IndexNode(
            keys=[20, 33],
            children=[self.leaf_A, self.leaf_B, self.leaf_C]
        )
 
        # Nó direito do nível 2: separadores 51 e 63
        self.node_right = IndexNode(
            keys=[51, 63],
            children=[self.leaf_D, self.leaf_E, self.leaf_F]
        )
 
        # Raiz (nível 1): separador 40 
        self.root = IndexNode(
            keys=[40],
            children=[self.node_left, self.node_right]
        )
 
        # Lista de todas as folhas em ordem (para buscas por intervalo)
        self.leaves_in_order = [
            self.leaf_A, self.leaf_B, self.leaf_C,
            self.leaf_D, self.leaf_E, self.leaf_F
        ]
 

    def _find_leaf(self, key):
        """
        Percorre o índice do topo até encontrar a folha primária
        responsável pela chave. Retorna (folha, caminho).
        """
        path = ["Raiz"]
        node = self.root
 
        # Nível 1: raiz
        child = node.find_child(key)
        path.append("Nó intermediário 1 " + ("esquerdo" if child is self.node_left else "direito"))
        node = child
 
        # Nível 2: nó intermediário
        leaf = node.find_child(key)
        path.append(leaf.name)
 
        return leaf, path
 
    # INSERÇÃO
 
    def insert(self, key, data):
        """
        Insere (key, data) na estrutura.
        1. Navega até a folha correta.
        2. Se a folha primária tem espaço → insere lá.
        3. Caso contrário → procura espaço na cadeia de overflow.
           Se não há espaço → cria nova página de overflow.
        """
        leaf, path = self._find_leaf(key)
        self.metrics["insercoes"] += 1
 
        print(f"\n[INSERÇÃO] Chave {key} | Caminho: {' → '.join(path)}")
 
        if not leaf.is_full():
            # Há espaço na folha primária
            leaf.records.append((key, data))
            leaf.records.sort()   # Mantém registros ordenados
            print(f"  → Inserido em {leaf.name}: {leaf.records}")
        else:
            # Folha primária cheia → vai para overflow
            self._insert_overflow(leaf, key, data)
 
    def _insert_overflow(self, leaf, key, data):
        """Insere em overflow: percorre a cadeia até encontrar espaço ou criar nova página."""
        if leaf.overflow_head is None:
            # Primeira overflow desta folha
            ov = OverflowPage()
            ov.records.append((key, data))
            leaf.overflow_head = ov
            self.metrics["overflow_criadas"] += 1
            print(f"  → {leaf.name} cheia! Nova página de overflow criada: {ov.records}")
        else:
            # Percorre a cadeia de overflow
            ov = leaf.overflow_head
            while ov is not None:
                if not ov.is_full():
                    ov.records.append((key, data))
                    ov.records.sort()
                    print(f"  → Inserido em overflow existente de {leaf.name}: {ov.records}")
                    return
                if ov.next is None:
                    break
                ov = ov.next
            # Todas as overflows estão cheias → cria nova
            new_ov = OverflowPage()
            new_ov.records.append((key, data))
            ov.next = new_ov
            self.metrics["overflow_criadas"] += 1
            print(f"  → Cadeia de overflow cheia em {leaf.name}! Nova página criada: {new_ov.records}")

    def search_equality(self, target_key):
        # 1. Navigate down the tree
        leaf, path = self._find_leaf(target_key)
        cost = len(path) # The path length gives us the initial visited nodes
        
        # 2. Search in the primary leaf (records are tuples now)
        for record in leaf.records:
            if record[0] == target_key: # record[0] is the key
                return record, cost, path 
       
        # 3. Search in the overflow pages
        current_overflow = leaf.overflow_head
        overflow_count = 1
        
        while current_overflow is not None:
            path.append(f"Overflow {overflow_count} from {leaf.name}")
            cost += 1
            
            for record in current_overflow.records:
                if record[0] == target_key:
                    return record, cost, path
                    
            current_overflow = current_overflow.next
            overflow_count += 1

        return None, cost, path

    def search_interval(self, min_key, max_key):
        # 1. Navigate to the starting leaf
        start_leaf, path = self._find_leaf(min_key)
        cost = len(path)
        found_records = []
        
        # 2. Find the index of the starting leaf in the ordered list
        leaf_idx = self.leaves_in_order.index(start_leaf)
        
        # 3. Sequential scan
        while leaf_idx < len(self.leaves_in_order):
            current_leaf = self.leaves_in_order[leaf_idx]
            
            # If it's not the starting leaf (already in path), count it
            if current_leaf != start_leaf:
                path.append(current_leaf.name)
                cost += 1

            # Stop condition: if the smallest key in this leaf is greater than max_key
            if current_leaf.records and current_leaf.records[0][0] > max_key:
                break

            # Collect from primary leaf
            for record in current_leaf.records:
                if min_key <= record[0] <= max_key:
                    found_records.append(record)

            # Collect from overflow pages
            current_overflow = current_leaf.overflow_head
            overflow_count = 1
            while current_overflow is not None:
                path.append(f"Overflow {overflow_count} from {current_leaf.name}")
                cost += 1
                for record in current_overflow.records:
                    if min_key <= record[0] <= max_key:
                        found_records.append(record)
                
                current_overflow = current_overflow.next
                overflow_count += 1

            # Move to the next leaf in the sequence
            leaf_idx += 1

        return found_records, cost, path