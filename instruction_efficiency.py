from causal_graph_structure import CausalModel, CausalPart
import pandas as pd
import numpy as np


cm_1 = CausalModel()
cm_1.add_part_full('R1', [], ['i1'])
cm_1.add_part_full('R2', [], ['i2'])
cm_1.add_part_full('R3', [], ['i3'])
cm_1.add_part_full('L1', ['i1'], ['i1'])
cm_1.add_part_full('L2', ['i2'], ['i2'])
cm_1.add_part_full('i1', ['L1', 'R1'], ['L1'])
cm_1.add_part_full('i2', ['L2', 'R2'], ['L2'])
cm_1.add_part_full('i3', [], ['i1', 'i2'])
cm_1.set_observable_parts(['L1', 'L2'])
cm_1.set_non_interactable_parts(['i1', 'i2', 'i3'])

frequecies = np.array(range(1,6))
frequecies = frequecies / np.sum(frequecies)
frequecies = frequecies.tolist()

cm_1.set_part_frequencies(['R1', 'R2', 'R3', 'L1', 'L2'], frequecies)

pass
