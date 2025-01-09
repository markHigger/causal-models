import numpy as np
import random
from queue import Queue
import networkx as nx
import matplotlib.pyplot as plt

#Matricies are in form [P1, P2, P3, L1, L2, L3, i1, i2, i3]
circuit1_cm = np.zeros([9,9])
circuit1_cm[0, 6] = 1 # R1 -> i1
circuit1_cm[1, 7] = 1 # R2 -> i2
circuit1_cm[2, 8] = 1 # R3 -> i3
circuit1_cm[3, 6] = 1 # L1 -> i1
circuit1_cm[6, 3] = 1 # i1 -> L1
circuit1_cm[4, 7] = 1 # L2 -> i2
circuit1_cm[7, 4] = 1 # i2 -> L2
circuit1_cm[8, 6] = 1 # i3 -> i1
circuit1_cm[8, 7] = 1 # i3 -> i2

circuit2_cm = np.zeros([9,9])
circuit2_cm[0, 6] = 1 # R1 -> i1
circuit2_cm[1, 7] = 1 # R2 -> i2
circuit2_cm[3, 6] = 1 # L1 -> i1
circuit2_cm[6, 3] = 1 # i1 -> L1
circuit2_cm[4, 7] = 1 # L2 -> i2
circuit2_cm[5, 8] = 1 # L3 -> i2
circuit2_cm[8, 5] = 1 # L3 -> i2
circuit2_cm[7, 4] = 1 # i2 -> L2
circuit2_cm[8, 6] = 1 # i3 -> i1
circuit2_cm[8, 7] = 1 # i3 -> i2

circuit3_cm = np.zeros([9,9])
circuit3_cm[0, 6] = 1 # R1 -> i1
circuit3_cm[1, 7] = 1 # R2 -> i2
circuit3_cm[2, 8] = 1 # R3 -> i3
circuit3_cm[3, 6] = 1 # L1 -> i1
circuit3_cm[6, 3] = 1 # i1 -> L1
circuit3_cm[4, 7] = 1 # L2 -> i2
circuit3_cm[7, 4] = 1 # i2 -> L2
circuit3_cm[8, 6] = 1 # i3 -> i1
circuit3_cm[8, 7] = 1 # i3 -> i2

circuit4_cm = np.zeros([9,9])
circuit4_cm[0, 6] = 1 # R1 -> i1
circuit4_cm[1, 7] = 1 # R2 -> i2
circuit4_cm[2, 7] = 1 # R3 -> i2
circuit4_cm[3, 6] = 1 # L1 -> i1
circuit4_cm[6, 3] = 1 # i1 -> L1
circuit4_cm[4, 7] = 1 # L2 -> i2
circuit4_cm[5, 7] = 1 # L3 -> i2
circuit4_cm[7, 5] = 1 # i2 -> L3
circuit4_cm[7, 4] = 1 # i2 -> L2
circuit4_cm[8, 6] = 1 # i3 -> i1
circuit4_cm[8, 7] = 1 # i3 -> i2

def generate_plan_causal_from_single_part(causal_model, broken_part):
    '''
    This function generates a plan to find a broken part using a breadth-first search through a causal model graph
    Inputs:
      causal_model - NxN directional connectivity matrix
      broken_part [int] - index of broken part

    Outputs:
      plan - M sized list of an order of parts to check.
    '''

    plan_of_attack = []
    # plan_of_attack.append(broken_part) # always check the original part that is broken first

    # current_part = broken_part
    # connected_parts = np.where(causal_model[:, current_part] == 1)[0]
    parts_to_check = Queue()
    parts_to_check.put(broken_part)
    while not parts_to_check.empty():
        current_part = parts_to_check.get()
        plan_of_attack.append(current_part)

        connected_parts = np.where(causal_model[:, current_part] == 1)[0]

        already_planned = np.nonzero((np.array(plan_of_attack)[:, None] == connected_parts))[1]
        connected_parts = np.delete(connected_parts, already_planned)

        while connected_parts.size:
            current_part = random.choice(connected_parts)
            connected_parts = np.delete(connected_parts, np.where(connected_parts == current_part)[0])
            parts_to_check.put(current_part)

    return plan_of_attack

def generate_plan_causal_from_multiple_parts(causal_model, broken_parts):
    origin_part_path = generate_plan_causal_from_single_part(causal_model, broken_parts[0])
    part_path = origin_part_path
    for broken_part in broken_parts[1:]:
        new_part_path = generate_plan_causal_from_single_part(causal_model, broken_part)
        for part in part_path.copy():
            if part not in new_part_path:
                part_path.remove(part)

    return part_path
        
def generate_observables_from_failure(causal_model, broken_part):
    observed_parts_broken = []

    
    return observed_parts_broken
    
dual_plan = generate_plan_causal_from_multiple_parts(circuit4_cm, [3,4])
graph = nx.from_numpy_array(circuit4_cm, create_using=nx.DiGraph)

options = {
    'node_color': 'blue',
    'node_size': 500,
    'width': 3,
    'arrowstyle': '-|>',
    'arrowsize': 12,
}
nx.draw_networkx(graph, arrows=True, **options)
plt.show()

print(generate_plan_causal_from_single_part(circuit1_cm, 3))
print(generate_plan_causal_from_single_part(circuit2_cm, 8))
