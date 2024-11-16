
# Libraries we used 
import json
import random
import sys
from deap import base, creator, tools, algorithms
import numpy as np
import math

# Initializing Some variables to be used in Constraints.

Total_Semesters = 4
Max_Credits_Sem = 12
Population_Size = 300                    
Generations_Name = 500
Tournament_Size = 5
# Crossover and mutation probabilities
Crossover_Probability=0.5
Mutation_Probability =  0.2  

############ Getting Data From Json File  ######################


json_file = sys.argv[2]     #  sys.argv[2]  is the second input from front(User)

# Reading the units and prerequisites from the json file

with open(json_file) as f:  
    data = json.load(f)
    units = data['units']  # Loading the units from JSON
    prerequisites = data['prerequisites']


# Fitness Function 

def Fitness(individual):

    # Initialising Variables

    violations = 0
    credits_per_semester = [0] * Total_Semesters  #[0,0,0,0]
    units_per_semester = [0] * Total_Semesters    #[0,0,0,0]
    unit_schedule = {}


    # Decoding the chromosomes. 
    # This loop iterates numbers of gene in chromosome times
    
    for i, gene in enumerate(individual):
        unit = list(units.keys())[i]
        semester = gene
        credits_per_semester[semester-1] += units[unit]['credits']
        units_per_semester[semester-1] += 1
        unit_schedule[unit] = semester

        
##############   Start Checking constraints #####################

        # Constraint 1 - "Checking Semester Availability "

        if semester not in units[unit]['available']:
            violations += 20  # Penalty if not satisfied

        # Constraint 2 - " Checking the Prerequisite of the unit"

    for unit, prereqs in prerequisites.items():
        if unit in unit_schedule:
            unit_semester = unit_schedule[unit]
            for prereq in prereqs:
                if prereq in unit_schedule:
                    prereq_semester = unit_schedule[prereq]
                    if prereq_semester >= unit_semester:
                        violations += 10  # Penalty if not satisfied

        #  Constraint 3 - " Maximum Credits per semester can not be more than 12"
    for credits in credits_per_semester:
        if credits > Max_Credits_Sem:
            # Strict penalty 
            violations += math.ceil(abs(credits - Max_Credits_Sem) / 4)

    """# Constraint 4 - " Maximum units per semster cn not be more than 4"
    for units_count in units_per_semester:
        if units_count > 4:
            violations += (units_count - 4) * 10"""

    return violations,






################# Mutation  ######################

def Mutate(individual):
    for i in range(len(individual)):
        if random.random() < Mutation_Probability:
            unit = list(units.keys())[i]
            available_semesters = units[unit]['available']
            individual[i] = random.choice(available_semesters)
    return individual,

# Setting up DEAP

# Setup DEAP
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

################# Valid Initialisation ######################
toolbox.register("attr_gene", random.choice, [1, 2, 3, 4])


toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_gene, n=len(units))
toolbox.register("population", tools.initRepeat, list, toolbox.individual, n=Population_Size)

toolbox.register("evaluate", Fitness)
toolbox.register("mate", tools.cxOnePoint)
toolbox.register("mutate", Mutate)
toolbox.register("select", tools.selTournament, tournsize=Tournament_Size)
##################### Main Function ##########################

def main():
    population = toolbox.population()
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)

    algorithms.eaSimple(population, toolbox, cxpb=Crossover_Probability, mutpb=Mutation_Probability, ngen=Generations_Name, stats=stats, halloffame=hof)

    return hof[0]

best = main()

# Gives the best results
#print("Best individual:", best)
#print("Best fitness:", Fitness(best))


##################### Decode and print schedules ################\

def decode_schedule(individual):
    schedule = {i: [] for i in range(1, Total_Semesters+1)}
    for i, semester in enumerate(individual):
        unit = list(units.keys())[i]
        schedule[semester].append(unit)
    return schedule

decoded_schedule = decode_schedule(best)
for semester, units in decoded_schedule.items():
    print(f"Semester {semester}: {', '.join(units)}")
