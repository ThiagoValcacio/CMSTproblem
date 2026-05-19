from itertools import product, combinations

# ============================================================
# Dados da instância
# ============================================================

n = 10
K = 3

c = [
    [1000, 71, 80, 54, 60, 30, 34, 68, 54, 27, 53],
    [31, 1000, 50, 36, 60, 22, 44, 40, 72, 50, 36],
    [42, 20, 1000, 60, 70, 44, 28, 50, 22, 72, 31],
    [50, 60, 60, 1000, 22, 64, 80, 78, 44, 72, 80],
    [100, 70, 90, 72, 1000, 14, 50, 92, 86, 70, 10],
    [98, 80, 80, 70, 14, 1000, 60, 92, 88, 60, 22],
    [70, 20, 28, 80, 94, 72, 1000, 75, 50, 100, 50],
    [58, 40, 41, 22, 72, 53, 20, 1000, 36, 14, 36],
    [22, 36, 22, 44, 50, 30, 50, 41, 1000, 53, 36],
    [62, 50, 53, 36, 86, 60, 14, 14, 36, 1000, 36],
    [40, 50, 31, 80, 82, 31, 50, 28, 36, 58, 1000]
]

clientes = list(range(1, n + 1))


# ============================================================
# Verifica se uma subárvore é válida
# ============================================================

def valida_arborescencia(parent, S):
    S = set(S)

    # Cada grupo deve ter exatamente um arco indo para o depot 0
    if sum(1 for i in S if parent[i] == 0) != 1:
        return False

    # Todo nó deve chegar ao depot seguindo os arcos i -> parent[i]
    for origem in S:
        visitados = set()
        atual = origem

        while atual != 0:
            if atual in visitados:
                return False

            visitados.add(atual)

            if atual not in parent:
                return False

            atual = parent[atual]

            if atual not in S and atual != 0:
                return False

    return True


# ============================================================
# Melhor arborescência para um grupo S
# ============================================================

def melhor_subarvore_direcionada(S, c):
    S = tuple(sorted(S))

    opcoes_por_no = []

    for i in S:
        # Cada nó pode apontar para outro nó do grupo ou para o depot 0
        opcoes = [j for j in S if j != i] + [0]
        opcoes_por_no.append(opcoes)

    melhor_custo = float("inf")
    melhor_arcos = None

    for escolha in product(*opcoes_por_no):
        parent = dict(zip(S, escolha))

        if not valida_arborescencia(parent, S):
            continue

        custo = sum(c[i][parent[i]] for i in S)

        if custo < melhor_custo:
            melhor_custo = custo
            melhor_arcos = [(i, parent[i]) for i in S]

    return melhor_custo, melhor_arcos


# ============================================================
# Heurística gulosa para o CMST
# ============================================================

def heuristica_cmst_gulosa(clientes, K, c):
    componentes = [frozenset([i]) for i in clientes]

    info_componentes = {
        frozenset([i]): melhor_subarvore_direcionada([i], c)
        for i in clientes
    }

    iteracoes = []

    while True:
        melhor_merge = None

        for A, B in combinations(componentes, 2):
            if len(A) + len(B) > K:
                continue

            M = frozenset(set(A) | set(B))

            custo_M, arcos_M = melhor_subarvore_direcionada(M, c)

            custo_atual = info_componentes[A][0] + info_componentes[B][0]
            ganho = custo_atual - custo_M

            if melhor_merge is None or ganho > melhor_merge["ganho"]:
                melhor_merge = {
                    "ganho": ganho,
                    "A": A,
                    "B": B,
                    "M": M,
                    "custo_atual": custo_atual,
                    "custo_M": custo_M,
                    "arcos_M": arcos_M
                }

        if melhor_merge is None or melhor_merge["ganho"] <= 1e-9:
            break

        A = melhor_merge["A"]
        B = melhor_merge["B"]
        M = melhor_merge["M"]

        iteracoes.append(melhor_merge)

        componentes = [C for C in componentes if C not in [A, B]]
        componentes.append(M)

        del info_componentes[A]
        del info_componentes[B]

        info_componentes[M] = (
            melhor_merge["custo_M"],
            melhor_merge["arcos_M"]
        )

    custo_total = sum(info_componentes[C][0] for C in componentes)

    arcos_solucao = []
    for C in componentes:
        arcos_solucao.extend(info_componentes[C][1])

    return custo_total, componentes, arcos_solucao, iteracoes


# ============================================================
# Rodar heurística
# ============================================================

custo_heuristico, componentes, arcos, iteracoes = heuristica_cmst_gulosa(clientes, K, c)

print("Custo heurístico:", custo_heuristico)

print("\nComponentes finais:")
for C in componentes:
    print(set(C))

print("\nArcos da solução heurística:")
for i, j in arcos:
    print(f"x[{i},{j}] = 1 | custo = {c[i][j]}")

print("\nIterações da heurística:")
for idx, it in enumerate(iteracoes, start=1):
    print(
        f"Iteração {idx}: unir {set(it['A'])} + {set(it['B'])} "
        f"-> {set(it['M'])} | ganho = {it['ganho']} | "
        f"custo antes = {it['custo_atual']} | custo depois = {it['custo_M']}"
    )