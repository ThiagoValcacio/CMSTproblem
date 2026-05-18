import gurobipy as gp
from gurobipy import GRB
from itertools import combinations
import math

# ============================================================
# Dados da instância
# ============================================================

# n = quantidade de nós clientes.
# O nó 0 é o nó central/depot.
# Portanto, os nós são: 0, 1, 2, ..., 10
n = 10

# Capacidade máxima de clientes por subárvore conectada ao nó 0
K = 3

# Matriz de custos cij
# Linha i, coluna j representa o custo do arco (i, j).
# A diagonal tem custo 1000, mas os arcos (i, i) serão ignorados.
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

# Conjunto de nós
V = range(n + 1)

# Conjunto de clientes, isto é, todos menos o nó central 0
clientes = range(1, n + 1)

# Conjunto de arcos direcionados (i, j), com i diferente de j
A = [(i, j) for i in V for j in V if i != j]


# ============================================================
# Criação do modelo
# ============================================================

model = gp.Model("LP_CMST_instancia")

# Variável x[i,j]
# x[i,j] representa se o arco direcionado (i,j) está na árvore.
# Como é LP, a variável é contínua entre 0 e 1.
x = model.addVars(
    A,
    lb=0,
    ub=1,
    vtype=GRB.CONTINUOUS,
    name="x"
)


# ============================================================
# Função objetivo
# ============================================================

# Minimizar o custo total dos arcos selecionados
model.setObjective(
    gp.quicksum(c[i][j] * x[i, j] for i, j in A),
    GRB.MINIMIZE
)


# ============================================================
# Restrições
# ============================================================

# Restrição (1):
# O total de arcos selecionados deve ser igual a n
model.addConstr(
    gp.quicksum(x[i, j] for i, j in A) == n,
    name="total_arcos"
)

# Restrição (2):
# Cada cliente deve ter exatamente um arco saindo dele
for i in clientes:
    model.addConstr(
        gp.quicksum(x[i, j] for j in V if j != i) == 1,
        name=f"saida_cliente_{i}"
    )

# Restrição (3) - Packing:
# Para todo subconjunto S dos clientes:
# soma dos arcos internos a S <= |S| - ceil(|S| / K)
#

for S_tuple in combinations(clientes, 2):
    S = set(S_tuple)

    model.addConstr(
        gp.quicksum(
            x[i, j]
            for i in S
            for j in S
            if i != j
        ) <= len(S) - math.ceil(len(S) / K),
        name=f"packing_card2_{'_'.join(map(str, S_tuple))}"
    )

# # ============================================================
# # Packing para S = {1,4,5,6,7,9,10}
# # ============================================================

S1 = {1, 4, 5, 6, 7, 9, 10}

model.addConstr(
    gp.quicksum(
        x[i, j]
        for i in S1
        for j in S1
        if i != j
    ) <= len(S1) - math.ceil(len(S1) / K),
    name="packing_S_1_4_5_6_7_9_10"
)


# # ============================================================
# # Packing para S = {1,5,4,10}
# # ============================================================

S2 = {1, 5, 4, 10}

model.addConstr(
    gp.quicksum(
        x[i, j]
        for i in S2
        for j in S2
        if i != j
    ) <= len(S2) - math.ceil(len(S2) / K),
    name="packing_S_1_5_4_10"
)

# # ============================================================
# # Packing para S = {9,4,3,7,10}
# # ============================================================

S3 = {9, 4, 3, 7, 10}

model.addConstr(
    gp.quicksum(
        x[i, j]
        for i in S3
        for j in S3
        if i != j
    ) <= len(S3) - math.ceil(len(S3) / K),
    name="packing_S_9_4_3_7_10"
)

# # ============================================================
# # LP2
# # Packing para S = {1,2,6,7,9}
# # ============================================================

# S4 = {1, 2, 6, 7, 9}

# model.addConstr(
#     gp.quicksum(
#         x[i, j]
#         for i in S4
#         for j in S4
#         if i != j
#     ) <= len(S4) - math.ceil(len(S4) / K),
#     name="packing_S_1_2_6_7_9"
# )

# # ============================================================
# # LP2
# # Packing para S = {3,4,5,10}
# # ============================================================

S5 = {3, 4, 5, 10}

model.addConstr(
    gp.quicksum(
        x[i, j]
        for i in S5
        for j in S5
        if i != j
    ) <= len(S5) - math.ceil(len(S5) / K),
    name="packing_S_3_4_5_10"
)

# # ============================================================
# # LP2
# # Packing para S = {1,2,3,4,5,6,7,9,10}
# # ============================================================

# S6 = {1, 2, 3, 4, 5, 6, 7, 9, 10}

# model.addConstr(
#     gp.quicksum(
#         x[i, j]
#         for i in S6
#         for j in S6
#         if i != j
#     ) <= len(S6) - math.ceil(len(S6) / K),
#     name="packing_S_1_2_3_4_5_6_7_9_10"
# )

# # ============================================================
# # LP3
# # Packing para S = {2,3,4,5,7,8,10}
# # ============================================================

# S7 = {2, 3, 4, 5, 7, 8, 10}

# model.addConstr(
#     gp.quicksum(
#         x[i, j]
#         for i in S7
#         for j in S7
#         if i != j
#     ) <= len(S7) - math.ceil(len(S7) / K),
#     name="packing_S_2_3_4_5_7_8_10"
# )

# # ============================================================
# # LP3 - packing + multistar
# # Packing para S = {2,4,5,10}
# # ============================================================

S8 = {2, 4, 5, 10}

model.addConstr(
    gp.quicksum(
        x[i, j]
        for i in S8
        for j in S8
        if i != j
    ) <= len(S8) - math.ceil(len(S8) / K),
    name="packing_S_2_4_5_10"
)

# # ============================================================
# # LP4
# # Packing para S = {1,2,6,9}
# # ============================================================

S9 = {1, 2, 6, 9}

model.addConstr(
    gp.quicksum(
        x[i, j]
        for i in S9
        for j in S9
        if i != j
    ) <= len(S9) - math.ceil(len(S9) / K),
    name="packing_S_1_2_6_9"
)

# # ============================================================
# # LP5
# # Packing para S = {3,7,8,9}
# # ============================================================

S10 = {3, 7, 8, 9}

model.addConstr(
    gp.quicksum(
        x[i, j]
        for i in S10
        for j in S10
        if i != j
    ) <= len(S10) - math.ceil(len(S10) / K),
    name="packing_S_3_7_8_9"
)

# # ============================================================
# # LP6
# # Packing para S = {4,5,8,10}
# # ============================================================

# S11 = {4, 5, 8, 10}

# model.addConstr(
#     gp.quicksum(
#         x[i, j]
#         for i in S11
#         for j in S11
#         if i != j
#     ) <= len(S11) - math.ceil(len(S11) / K),
#     name="packing_S_4_5_8_10"
# )

# # ============================================================
# # LP3 - packing + multistar
# # Packing para S = {3,4,5,8,10}
# # ============================================================

S12 = {3, 4, 5, 8, 10}

model.addConstr(
    gp.quicksum(
        x[i, j]
        for i in S12    
        for j in S12
        if i != j
    ) <= len(S12) - math.ceil(len(S12) / K),
    name="packing_S_3_4_5_8_10"
)

# # ============================================================
# # LP4 - packing + multistar
# # Packing para S = {2,3,7,8}
# # ============================================================

# S13 = {2, 3, 7, 8}

# model.addConstr(
#     gp.quicksum(
#         x[i, j]
#         for i in S13 
#         for j in S13
#         if i != j
#     ) <= len(S13) - math.ceil(len(S13) / K),
#     name="packing_S_2_3_7_8"
# )

# # ============================================================
# # LP4 - packing + multistar
# # Packing para S = {4,5,7,10}
# # ============================================================

S14 = {4, 5, 7, 10}

model.addConstr(
    gp.quicksum(
        x[i, j]
        for i in S14 
        for j in S14
        if i != j
    ) <= len(S14) - math.ceil(len(S14) / K),
    name="packing_S_4_5_7_10"
)

# # ============================================================
# # LP4 - packing + multistar
# # Packing para S = {2,3,6,7,8,9}
# # ============================================================

S15 = {2, 3, 6, 7, 8, 9}

model.addConstr(
    gp.quicksum(
        x[i, j]
        for i in S15 
        for j in S15
        if i != j
    ) <= len(S15) - math.ceil(len(S15) / K),
    name="packing_S_2_3_6_7_8_9"
)



# ---------------------------------------------------- MULTISTAR -------------------------


# ============================================================
# Multistar para S = {1,4,5,6,7,9,10}
# ============================================================

S1 = {1, 4, 5, 6, 7, 9, 10}
fora_S1 = set(clientes) - S1

model.addConstr(
    K * gp.quicksum(
        x[i, j]
        for i in S1
        for j in S1
        if i != j
    )
    +
    gp.quicksum(
        x[i, j]
        for i in S1
        for j in fora_S1
    )
    <= len(S1) * (K - 1),
    name="multistar_S_1_4_5_6_7_9_10"
)

# ============================================================
# Multistar para S = {1,5,4,10}
# ============================================================

S2 = {1, 5, 4, 10}
fora_S2 = set(clientes) - S2

model.addConstr(
    K * gp.quicksum(
        x[i, j]
        for i in S2
        for j in S2
        if i != j
    )
    +
    gp.quicksum(
        x[i, j]
        for i in S2
        for j in fora_S2
    )
    <= len(S2) * (K - 1),
    name="multistar_S_1_5_4_10"
)

# ============================================================
# Multistar para S = {9,4,3,7,10}
# ============================================================

S3 = {9, 4, 3, 7, 10}
fora_S3 = set(clientes) - S3

model.addConstr(
    K * gp.quicksum(
        x[i, j]
        for i in S3
        for j in S3
        if i != j
    )
    +
    gp.quicksum(
        x[i, j]
        for i in S3
        for j in fora_S3
    )
    <= len(S3) * (K - 1),
    name="multistar_S_9_4_3_7_10"
)

# ============================================================
# Multistar para S = {1,2,5}
# ============================================================

S4 = {1, 2, 5}
fora_S4 = set(clientes) - S4

model.addConstr(
    K * gp.quicksum(
        x[i, j]
        for i in S4
        for j in S4
        if i != j
    )
    +
    gp.quicksum(
        x[i, j]
        for i in S4
        for j in fora_S4
    )
    <= len(S4) * (K - 1),
    name="multistar_S_1_2_5"
)

# ============================================================
# LP2
# Multistar para S = {3,4,5,10}
# ============================================================

# S5 = {3, 4, 5, 10}
# fora_S5 = set(clientes) - S5

# model.addConstr(
#     K * gp.quicksum(
#         x[i, j]
#         for i in S5
#         for j in S5
#         if i != j
#     )
#     +
#     gp.quicksum(
#         x[i, j]
#         for i in S5
#         for j in fora_S5
#     )
#     <= len(S5) * (K - 1),
#     name="multistar_S_3_4_5_10"
# )

# ============================================================
# LP2
# Multistar para S = {6,7,9}
# ============================================================

S6 = {6, 7, 9}
fora_S6 = set(clientes) - S6

model.addConstr(
    K * gp.quicksum(
        x[i, j]
        for i in S6
        for j in S6
        if i != j
    )
    +
    gp.quicksum(
        x[i, j]
        for i in S6
        for j in fora_S6
    )
    <= len(S6) * (K - 1),
    name="multistar_S_6_7_9"
)

# ============================================================
# LP2
# Multistar para S = {1,2,6,9}
# ============================================================

# S7 = {1, 2, 6, 9}
# fora_S7 = set(clientes) - S7

# model.addConstr(
#     K * gp.quicksum(
#         x[i, j]
#         for i in S7
#         for j in S7
#         if i != j
#     )
#     +
#     gp.quicksum(
#         x[i, j]
#         for i in S7
#         for j in fora_S7
#     )
#     <= len(S7) * (K - 1),
#     name="multistar_S_1_2_6_9"
# )

# ============================================================
# LP3
# Multistar para S = {3,4,5,7,10}
# ============================================================

# S8 = {3,4,5,7,10}
# fora_S8 = set(clientes) - S8

# model.addConstr(
#     K * gp.quicksum(
#         x[i, j]
#         for i in S8
#         for j in S8
#         if i != j
#     )
#     +
#     gp.quicksum(
#         x[i, j]
#         for i in S8
#         for j in fora_S8
#     )
#     <= len(S8) * (K - 1),
#     name="multistar_S_3_4_5_7_10"
# )

# ============================================================
# LP3
# Multistar para S = {1,2,6,7,9}
# ============================================================

S9 = {1, 2, 6, 7, 9}
fora_S9 = set(clientes) - S9

model.addConstr(
    K * gp.quicksum(
        x[i, j]
        for i in S9
        for j in S9
        if i != j
    )
    +
    gp.quicksum(
        x[i, j]
        for i in S9
        for j in fora_S9
    )
    <= len(S9) * (K - 1),
    name="multistar_S_1_2_6_7_9"
)

# ============================================================
# LP3
# Multistar para S = {2,4,5,6,7,9,10}
# ============================================================

# S10 = {2, 4, 5, 6, 7, 9, 10}
# fora_S10 = set(clientes) - S10

# model.addConstr(
#     K * gp.quicksum(
#         x[i, j]
#         for i in S10
#         for j in S10
#         if i != j
#     )
#     +
#     gp.quicksum(
#         x[i, j]
#         for i in S10
#         for j in fora_S10
#     )
#     <= len(S10) * (K - 1),
#     name="multistar_S_2_4_5_6_7_9_10"
# )

# ============================================================
# LP2 - packing + multistar
# Multistar para S = {2,4,5,10}
# ============================================================

S11 = {2, 4, 5, 10}
fora_S11 = set(clientes) - S11

model.addConstr(
    K * gp.quicksum(
        x[i, j]
        for i in S11 
        for j in S11
        if i != j
    )
    +
    gp.quicksum(
        x[i, j]
        for i in S11
        for j in fora_S11
    )
    <= len(S11) * (K - 1),
    name="multistar_S_2_4_5_10"
)

# ============================================================
# LP3 - packing + multistar
# Multistar para S = {3,4,5,8,10}
# ============================================================

S12 = {3, 4, 5, 8, 10}
fora_S12 = set(clientes) - S12

model.addConstr(
    K * gp.quicksum(
        x[i, j]
        for i in S12 
        for j in S12
        if i != j
    )
    +
    gp.quicksum(
        x[i, j]
        for i in S12
        for j in fora_S12
    )
    <= len(S12) * (K - 1),
    name="multistar_S_3_4_5_8_10"
)

# ============================================================
# LP4 - packing + multistar
# Multistar para S = {2,3,6,7,8,9}
# ============================================================

S13 = {2, 3, 6, 7, 8, 9}
fora_S13 = set(clientes) - S13

model.addConstr(
    K * gp.quicksum(
        x[i, j]
        for i in S13 
        for j in S13
        if i != j
    )
    +
    gp.quicksum(
        x[i, j]
        for i in S13
        for j in fora_S13
    )
    <= len(S13) * (K - 1),
    name="multistar_S_2_3_6_7_8_9"
)

# ============================================================
# LP4 - packing + multistar
# Multistar para S = {4,5,7,10}
# ============================================================

S14 = {4, 5, 7, 10}
fora_S14 = set(clientes) - S14

model.addConstr(
    K * gp.quicksum(
        x[i, j]
        for i in S14 
        for j in S14
        if i != j
    )
    +
    gp.quicksum(
        x[i, j]
        for i in S14
        for j in fora_S14
    )
    <= len(S14) * (K - 1),
    name="multistar_S_4_5_7_10"
)

# ============================================================
# LP5 - packing + multistar
# Multistar para S = {3,7,8,9}
# ============================================================

S15 = {3, 7, 8, 9}
fora_S15 = set(clientes) - S15

model.addConstr(
    K * gp.quicksum(
        x[i, j]
        for i in S15 
        for j in S15
        if i != j
    )
    +
    gp.quicksum(
        x[i, j]
        for i in S15
        for j in fora_S15
    )
    <= len(S15) * (K - 1),
    name="multistar_S_3_7_8_9"
)

# ============================================================
# Resolver o modelo
# ============================================================

model.optimize()


# ============================================================
# Exibir resultados
# ============================================================

if model.status == GRB.OPTIMAL:
    print("\nSolução ótima encontrada.")
    print(f"Valor ótimo LP = {model.objVal:.4f}")

    print("\nArcos com valor positivo:")
    for i, j in A:
        if x[i, j].X > 1e-6:
            print(f"x[{i},{j}] = {x[i,j].X:.4f} | custo = {c[i][j]}")

else:
    print("\nO modelo não encontrou solução ótima.")
    print(f"Status Gurobi: {model.status}")