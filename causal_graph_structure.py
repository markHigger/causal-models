import numpy as np

class CausalPart:
    def __init__(self, part_id):
        self.part_id = part_id #string 
        self.caused_by = [] #list of CausalPart types
        self.causes = [] #list of CausalPart type

    def add_caused_by(self, caused_by):
        #adds new CausalPart as a cause of part if that part is not already there
        for part in self.caused_by:
            if part == caused_by:
                return
        self.caused_by.append(caused_by)

    def add_cause(self, cause):
         #adds new CausalPart for things the part causes if that part is not already there
        for part in self.causes:
            if part == cause:
                return
        self.causes.append(cause)

class CausalModel:
    def __init__(self):
        self.parts = []
        self.observable_parts = []
        self.non_interactable_parts = []

    def set_observable_parts(self, observable_parts):
        self.observable_parts = observable_parts
    
    def set_non_interactable_parts(self, interactable_parts):
        self.non_interactable_parts = interactable_parts

    def add_part_full(self, part_id, caused_by_ids, causes_ids):
        if not self.find_part(part_id):
            self.add_new_part_empty(CausalPart(part_id))
        part = self.find_part(part_id)
        self.add_part_causes(part, causes_ids)
        self.add_part_caused_bys(part, caused_by_ids)

    def add_new_part_empty(self, part):
        self.parts.append(part)

    def add_part_causes(self, part, cause_ids):
        for cause_id in cause_ids:
            # add part if its not already added
            if not self.find_part(cause_id):
                self.add_new_part_empty(CausalPart(cause_id))
            cause_part = self.find_part(cause_id)
            part.add_cause(cause_part)
            cause_part.add_caused_by(part)

    def add_part_caused_bys(self, part, caused_by_ids):
        for cause_by_id in caused_by_ids:
            # add part if its not already added
            if not self.find_part(cause_by_id):
                self.add_new_part_empty(CausalPart(cause_by_id))
            caused_by_part = self.find_part(cause_by_id)
            part.add_caused_by(caused_by_part)
            caused_by_part.add_cause(part)

    def find_all_causes_for_part(self, part_id, current_cause_list):
        # Recursive function which finds all the parts which can cause the target part to fail
        # returns list of part objects which can cause the target part to fail

        # Initilize current_cause_list to [] for root iteration
        root_part = self.find_part(part_id)
        current_cause_list.append(root_part)

        for caused_by in root_part.caused_by:
            part_is_excluded = False
            #check if part is already in the cause list, and run function on new cause part
            for excluded_part in current_cause_list:
                if caused_by == excluded_part:
                    part_is_excluded = True
            if not part_is_excluded:
                current_cause_list = self.find_all_causes_for_part(caused_by.part_id, current_cause_list)
        return current_cause_list

    def find_points_of_failure_from_observerables(self, part_ids_working, part_ids_not_working):

        # Initalize possible causes to all parts
        potential_causes_ids = []
        for part in self.parts:
            potential_causes_ids.append(part.part_id)

        # Remove parts which would not cause observed failures to fail
        for part_id in part_ids_not_working:
            part_causes = self.find_all_causes_for_part(part_id, [])
            part_causes_ids = []
            for cause in part_causes:
                part_causes_ids.append(cause.part_id)

            #find interserction of part causes and current cause list, removing parts that cant cause observed failures
            potential_causes_ids = list(set(part_causes_ids) & set(potential_causes_ids))

        # Remove parts which would cause observed successes to fail
        for part_id in part_ids_working:
            part_causes = self.find_all_causes_for_part(part_id, [])
            part_causes_ids = []

            for cause in part_causes:
                part_causes_ids.append(cause.part_id)

            #find  difference of part causes and current cause list, removing parts that would cause observable successes to fail
            potential_causes_ids = list(set(potential_causes_ids) - set(part_causes_ids))

        return potential_causes_ids

    def find_failures_caused_by_part(self, part_id, current_caused_by_list):
        # Recursive function which finds all the parts which the target part will cause to fail
        # returns list of part objects which can cause the target part to fail

        # Initilize current_cause_list to [] for root iteration
        root_part = self.find_part(part_id)
        current_caused_by_list.append(root_part)

        for cause in root_part.causes:
            part_is_excluded = False
            #check if part is already in the cause list, and run function on new cause part
            for excluded_part in current_caused_by_list:
                if cause == excluded_part:
                    part_is_excluded = True
            if not part_is_excluded:
                current_caused_by_list = self.find_failures_caused_by_part(cause.part_id, current_caused_by_list)
        return current_caused_by_list
    
    def find_observables_from_failure(self, part_id):
        '''returns list of working and not working observables'''
        working_observables = []
        not_working_observables = []

        assert self.observable_parts

        other_parts_failing = self.find_failures_caused_by_part(part_id, [])
        for obs_part_id in self.observable_parts:
            observable_failing = False
            for failing_part in other_parts_failing:
                if failing_part.part_id == obs_part_id:
                    observable_failing = True
            if observable_failing:
                not_working_observables.append(obs_part_id)
            else:
                working_observables.append(obs_part_id)

        return working_observables, not_working_observables


    def find_part(self, part_id):
        # returns CausalPart part in part list from part id
        for part in self.parts:
            if part.part_id == part_id:
                return part
        return False

    def init_from_matrix(self, matrix):
        '''TODO: add function which turns a graph in matrix form into CausalModel stucture'''
        # assert self.parts.empty()
        
        # for ridx in range(matrix.shape[0]):
        #     part = CausalPart(ridx)
        #     for cidx in range(matrix.shape[1]):


        
test_cm = CausalModel()
test_cm.add_part_full('R1', [], ['i1'])
test_cm.add_part_full('R2', [], ['i2'])
test_cm.add_part_full('R3', [], ['i3'])
test_cm.add_part_full('L1', ['i1'], ['i1'])
test_cm.add_part_full('L2', ['i2'], ['i2'])
test_cm.add_part_full('i1', ['L1', 'R1'], ['L1'])
test_cm.add_part_full('i2', ['L2', 'R2'], ['L2'])
test_cm.add_part_full('i3', [], ['i1', 'i2'])

# part_list_part = test_cm.find_all_causes_for_part('L1', [])
parts_list_failure = test_cm.find_points_of_failure_from_observerables(['L2'], ['L1'])
test_cm.set_observable_parts(['L1', 'L2'])
obs_working, obs_failing = test_cm.find_observables_from_failure('R2')
parts_to_test = test_cm.find_points_of_failure_from_observerables(obs_working, obs_failing)
print(parts_to_test)