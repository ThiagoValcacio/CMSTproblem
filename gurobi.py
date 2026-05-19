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


def get_forbidden_arcs_by_cost():
    forbidden = set()
    for u, v in combinations(clientes, 2):
        if c[u][v] >= max(c[u][0], c[v][0]):
            forbidden.add((u, v))
        if c[v][u] >= max(c[u][0], c[v][0]):
            forbidden.add((v, u))
    return forbidden


def forbid_arcs_due_to_root_attachment(forbidden_arcs, x_vals):
    for u, v in combinations(clientes, 2):
        if x_vals.get((u, 0), 0) >= 1 - 1e-6 or x_vals.get((v, 0), 0) >= 1 - 1e-6:
            forbidden_arcs.add((u, v))
            forbidden_arcs.add((v, u))
    return forbidden_arcs


def build_model(forbidden_arcs):
    model = gp.Model("LP_CMST_instancia")
    x = model.addVars(
        A,
        lb=0,
        ub=1,
        vtype=GRB.CONTINUOUS,
        name="x"
    )
    for i, j in forbidden_arcs:
        x[i, j].ub = 0
        x[i, j].lb = 0

    model.setObjective(
        gp.quicksum(c[i][j] * x[i, j] for i, j in A),
        GRB.MINIMIZE
    )

    model.addConstr(
        gp.quicksum(x[i, j] for i, j in A) == n,
        name="total_arcos"
    )

    for i in clientes:
        model.addConstr(
            gp.quicksum(x[i, j] for j in V if j != i) == 1,
            name=f"saida_cliente_{i}"
        )

    return model, x


def add_packing_constraint(model, x, S, name_suffix=None):
    if name_suffix is None:
        name_suffix = "pack_" + "_".join(map(str, sorted(S)))
    model.addConstr(
        gp.quicksum(
            x[i, j]
            for i in S
            for j in S
            if i != j
        ) <= len(S) - math.ceil(len(S) / K),
        name=f"{name_suffix}"
    )


def add_multistar_constraint(model, x, S, name_suffix=None):
    if name_suffix is None:
        name_suffix = "multi_" + "_".join(map(str, sorted(S)))
    outside = set(clientes) - set(S)
    model.addConstr(
        K * gp.quicksum(
            x[i, j]
            for i in S
            for j in S
            if i != j
        )
        +
        gp.quicksum(
            x[i, j]
            for i in S
            for j in outside
        )
        <= len(S) * (K - 1),
        name=f"{name_suffix}"
    )




# ============================================================
# Criação do modelo
# ============================================================

candidates = get_forbidden_arcs_by_cost()
forbidden_arcs = set()
model, x = build_model(forbidden_arcs)


# ============================================================
# Restrições adicionais
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


# ============================================================
# Modo interativo: rode uma iteração, adicione restrições manualmente e re-otimize
# ============================================================

model.optimize()

def print_solution(x, A, c):
    print(f"Valor objetivo (LP) = {model.objVal:.4f}")
    print("Arcos com valor positivo:")
    for i, j in A:
        if x[i, j].X > 1e-6:
            print(f"x[{i},{j}] = {x[i,j].X:.4f} | custo = {c[i][j]}")

print_solution(x, A, c)

print('\nEntrar em modo interativo. Comandos:')
print('  pack i,j,k   -> adiciona packing para o conjunto {i,j,k}')
print('  multi i,j,k  -> adiciona multistar para o conjunto {i,j,k}')
print('  reopt        -> re-otimiza com restrições adicionadas')
print('  exit         -> sai')
print('  list_candidates -> lista arcos candidatos à eliminação por custo')
print('  forbid i,j   -> proíbe o arco (i,j) e atualiza modelo')

while True:
    cmd = input('cmd> ').strip()
    if not cmd:
        continue
    parts = cmd.split()
    if cmd == 'exit' or cmd == 'quit':
        break
    if cmd == 'reopt':
        model.optimize()
        print_solution(x, A, c)
        continue
    if cmd == 'list_candidates':
        print('Candidates (u,v) where c[u,v] >= max(c[u,0], c[v,0]):')
        for u, v in sorted(candidates):
            print(f'  ({u},{v}) cost={c[u][v]}')
        continue
    if parts[0] == 'forbid' and len(parts) >= 2:
        try:
            nums = [int(p) for p in parts[1].split(',')]
            if len(nums) != 2:
                print('forbid requires two integers: forbid i,j')
                continue
            i, j = nums
            forbidden_arcs.add((i, j))
            try:
                x[i, j].ub = 0
                x[i, j].lb = 0
            except Exception:
                pass
            model.update()
            print(f'Arc ({i},{j}) forbidden')
        except Exception as e:
            print('Erro ao aplicar forbid:', e)
        continue
    parts = cmd.split()
    if parts[0] in ('pack', 'multi') and len(parts) >= 2:
        try:
            nums = [int(p) for p in parts[1].split(',')]
            S = set(nums)
            if parts[0] == 'pack':
                add_packing_constraint(model, x, S)
                print(f'Packing added for set {sorted(S)}')
            else:
                add_multistar_constraint(model, x, S)
                print(f'Multistar added for set {sorted(S)}')
            model.update()
        except Exception as e:
            print('Erro ao adicionar restrição:', e)
        continue
    print('Comando desconhecido')


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