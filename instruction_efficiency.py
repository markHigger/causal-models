from causal_graph_structure import CausalModel, CausalPart
import pandas as pd
import numpy as np

def compute_expected_value_frequency(failure_rates):
    '''E[M_f] = sum_{n=1}^{N}(P(p_{n-1})*n), where p_n are part falure rates sorted by frequency, and N is interactable parts'''
    failure_rates.sort(reverse=True)
    expected_instructions = 0
    for n_instructions, rate_of_failure in enumerate(failure_rates):
        expected_instructions += rate_of_failure * (n_instructions+1)
    
    return expected_instructions

def compute_expected_value_causal(causal_model, part_frequencies_df):
    '''
    E[M_c] = sum(E[Mb|p_n] * P(p_n))
    E[Mb|p_n] = 1/N * N*(N+1) / 2
    E[M_c] - expected value of the number instructions it will take for the causal algorthm for a given model
    Mb - Markov blanket of the model for parts to check
    p_n - part n
    P(p_n) - chance that p_n is the failed part
    
    '''

    expected_value_total = 0
    for idx, row in part_frequencies_df.iterrows():
        part_id = row['part ids']
        #find observables for a given part failure
        obs_working, obs_failing = causal_model.find_observables_from_failure(part_id)
        markov_blanket = causal_model.find_potential_root_causes_from_observerables(obs_working, obs_failing)
        num_parts = len(markov_blanket)
        expected_value_blanket = (num_parts + 1)/2
        expected_value_total += expected_value_blanket * row['failure rates']



        pass
    return expected_value_total



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

# frequecies = np.array(range(1,6))
# frequecies = [1, 1, 1, 1, 1]
frequecies = [0.8, 0.05, 0.05, 0.05, 0.05]
frequecies = frequecies / np.sum(frequecies)
frequecies = frequecies.tolist()

cm_1.set_part_failure_rates(['R1', 'L2', 'R3', 'R2', 'L1'], frequecies)
cm_1_part_failure_rates = {'part ids': cm_1.get_interactable_part_ids(), 
                           'failure rates': cm_1.get_part_failure_rates(cm_1.get_interactable_part_ids())}
cm_1_part_failure_rates = pd.DataFrame(data=cm_1_part_failure_rates)
cm_1_part_failure_rates = cm_1_part_failure_rates.sort_values(by=['failure rates'])

expected_value_f = compute_expected_value_frequency(cm_1_part_failure_rates['failure rates'].tolist())

expected_value_c = compute_expected_value_causal(cm_1, cm_1_part_failure_rates)

# print(cm_1.get_part_failure_rates(['R1', 'L2']))
