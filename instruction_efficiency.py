from causal_graph_structure import CausalModel, CausalPart
import pandas as pd
import numpy as np
import random
import itertools
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

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

def compute_expected_value_combined(causal_model, part_frequencies_df):
    '''
    E[M_c] = sum(E[Mb|p_n] * P(p_n))
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
        part_failure_rates_raw = causal_model.get_part_failure_rates(markov_blanket)
        part_failure_rates = (part_failure_rates_raw / np.sum(part_failure_rates_raw)).tolist()
        expected_value_blanket = compute_expected_value_frequency(part_failure_rates)
        # expected_value_blanket will be nan when there is a 0% chance of that part broken
        if not expected_value_blanket > 0:
            expected_value_blanket = 0

        expected_value_total += expected_value_blanket * row['failure rates']
        # {'part ids': causal_model.get_interactable_part_ids(), 
        #                    'failure rates': causal_model.get_part_failure_rates(causal_model.get_interactable_part_ids())}
        # num_parts = len(markov_blanket)

        # expected_value_blanket = (num_parts + 1)/2

        # expected_value_total += expected_value_blanket * row['failure rates']
    
    return expected_value_total


def create_distrobution_truncated_geometric(N, r):
    ''' = (1-r)^n * r / sum(1-r)^m * r'''
    probs = []
    for prob_idx in range(N):
        probs.append(np.pow((1 - r), prob_idx) * r)
    probs /= np.sum(probs)

    return probs.tolist()

def create_distrobution_uniform(N):
    probs = []
    for prob_idx in range(N):
        probs.append(1/N)
    return probs

def create_distrobution_step(N, cutoff):
    probs = []
    for prob_idx in range(N):
        if prob_idx < cutoff:
            probs.append(1/(cutoff))
        else:
            probs.append(0.0)
    return probs

def plot_PMF(distro, title, filename):
    values = list(range(len(distro)))
    ax = plt.figure(figsize=(8,6)).gca()
    ax.plot(values, distro,'bo',ms=15)
    ax.vlines(values, 0, distro, colors='b', lw=5, alpha=0.5)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylim([0, 1])
    plt.title(title, fontsize=14)
    plt.xlabel('Part Number', fontsize=14)
    plt.ylabel('Probability Part is Broken',fontsize=14)
    plt.tick_params(axis='both',which='major',labelsize=14)
    plt.grid(visible=True)
    plt.savefig(filename,dpi=600)
    # plt.show()


cm = CausalModel()
cm.add_part_full('R1', [], ['i1'])
cm.add_part_full('R2', [], ['i2'])
cm.add_part_full('R3', [], ['i3'])
cm.add_part_full('L1', ['i1'], ['i1'])
cm.add_part_full('L2', ['i2'], ['i2'])
cm.add_part_full('L3', ['i3'], ['i3'])
cm.add_part_full('i1', ['L1', 'R1'], ['L1'])
cm.add_part_full('i2', ['L2', 'R2'], ['L2'])
cm.add_part_full('i3', ['L3'], ['i1', 'i2', 'L3'])
cm.set_observable_parts(['L1', 'L2', 'L3'])
cm.set_non_interactable_parts(['i1', 'i2', 'i3'])

# frequecies = np.array(range(1,6))
# frequecies = [1, 1, 1, 1, 1]
# frequecies = [0.9, 0.025, 0.025, 0.025, 0.025]
# frequecies = frequecies / np.sum(frequecies)
# frequecies = frequecies.tolist()
# random.shuffle(frequecies)

probs_geometric = create_distrobution_truncated_geometric(6, 0.75)
probs_step = create_distrobution_step(6, 3)
probs_uniform = create_distrobution_uniform(6)
plot_PMF(probs_geometric, 'Geometric Distribution (r = 0.75)', 'geometric_distribution.pdf')
plot_PMF(probs_step, 'Step Distribution (N_c = 3)', 'step_distribution.pdf')
plot_PMF(probs_uniform, 'Uniform Distribution', 'uniform_distribution.pdf')

distros_all = [probs_geometric, probs_step, probs_uniform]
part_permutes = list(itertools.permutations(cm.get_interactable_part_ids()))

for distrobution in distros_all:
    expected_value_c = 0
    expected_value_f = 0
    expected_value_cf = 0
    for parts_list in part_permutes:
        cm.set_part_failure_rates(parts_list, distrobution)
        cm_part_failure_rates = {'part ids': cm.get_interactable_part_ids(), 
                            'failure rates': cm.get_part_failure_rates(cm.get_interactable_part_ids())}

        cm_part_failure_rates_df = pd.DataFrame(data=cm_part_failure_rates)
        cm_part_failure_rates_df = cm_part_failure_rates_df.sort_values(by=['failure rates'])

        expected_value_f += compute_expected_value_frequency(cm_part_failure_rates_df['failure rates'].tolist())
        expected_value_c += compute_expected_value_causal(cm, cm_part_failure_rates_df)
        expected_value_cf += compute_expected_value_combined(cm, cm_part_failure_rates_df)
    expected_value_c /= len(part_permutes)
    expected_value_f /= len(part_permutes)
    expected_value_cf /= len(part_permutes)
    print('c: ', expected_value_c)
    print('f: ', expected_value_f)
    print('cf: ', expected_value_cf)

# 6 part circuit
cm = CausalModel()
cm.add_part_full('R1', [], ['i1'])
cm.add_part_full('R2', [], ['i2'])
cm.add_part_full('R3', [], ['i3'])
cm.add_part_full('L1', ['i1'], ['i1'])
cm.add_part_full('L2', ['i2'], ['i2'])
cm.add_part_full('L3', ['i2'], ['i2'])
cm.add_part_full('i1', ['L1', 'R1'], ['L1'])
cm.add_part_full('i2', ['L2', 'L3', 'R2'], ['L2', 'L3'])
cm.add_part_full('i3', [], ['i1', 'i2'])
cm.set_observable_parts(['L1', 'L2', 'L3']) 
cm.set_non_interactable_parts(['i1', 'i2', 'i3'])


# frequecies = [0.7, 0.035, 0.035, 0.035, 0.035, 0.035]
# frequecies = frequecies / np.sum(frequecies)
# frequecies = frequecies.tolist()
# random.shuffle(frequecies)

probs_geometric = create_distrobution_truncated_geometric(6, 0.75)
probs_step = create_distrobution_step(6, 3)
print(np.sum(probs_step))
probs_uniform = create_distrobution_uniform(6)

distros_all = [probs_geometric, probs_step, probs_uniform]
part_permutes = list(itertools.permutations(cm.get_interactable_part_ids()))

for distrobution in distros_all:
    expected_value_c = 0
    expected_value_f = 0
    expected_value_cf = 0
    for parts_list in part_permutes:
        cm.set_part_failure_rates(parts_list, distrobution)
        cm_part_failure_rates = {'part ids': cm.get_interactable_part_ids(), 
                            'failure rates': cm.get_part_failure_rates(cm.get_interactable_part_ids())}

        cm_part_failure_rates_df = pd.DataFrame(data=cm_part_failure_rates)
        cm_part_failure_rates_df = cm_part_failure_rates_df.sort_values(by=['failure rates'])

        expected_value_f += compute_expected_value_frequency(cm_part_failure_rates_df['failure rates'].tolist())
        expected_value_c += compute_expected_value_causal(cm, cm_part_failure_rates_df)
        expected_value_cf += compute_expected_value_combined(cm, cm_part_failure_rates_df)
    expected_value_c /= len(part_permutes)
    expected_value_f /= len(part_permutes)
    expected_value_cf /= len(part_permutes)
    print('c: ', expected_value_c)
    print('f: ', expected_value_f)
    print('cf: ', expected_value_cf)
    

# circuit4_cm[0, 6] = 1 # R1 -> i1s
# circuit4_cm[1, 7] = 1 # R2 -> i2
# circuit4_cm[2, 7] = 1 # R3 -> i2
# circuit4_cm[3, 6] = 1 # L1 -> i1
# circuit4_cm[6, 3] = 1 # i1 -> L1
# circuit4_cm[4, 7] = 1 # L2 -> i2
# circuit4_cm[5, 7] = 1 # L3 -> i2
# circuit4_cm[7, 5] = 1 # i2 -> L3
# circuit4_cm[7, 4] = 1 # i2 -> L2
# circuit4_cm[8, 6] = 1 # i3 -> i1
# circuit4_cm[8, 7] = 1 # i3 -> i2


# print(cm_1.get_part_failure_rates(['R1', 'L2']))
