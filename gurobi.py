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
# Como n = 10, é viável gerar todos os subconjuntos.
for tamanho in range(2, n + 1):
    for S_tuple in combinations(clientes, tamanho):
        S = set(S_tuple)

        model.addConstr(
            gp.quicksum(
                x[i, j]
                for i in S
                for j in S
                if i != j
            ) <= len(S) - math.ceil(len(S) / K),
            name=f"packing_{'_'.join(map(str, S_tuple))}"
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