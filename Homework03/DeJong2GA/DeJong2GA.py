import random
import math
import json
import os

N = 4
POPULATION_SIZE = 100
MUTATION_RATE = 0.8
CROSSOVER_RATE = 0.1
NUMBER_OF_GENERATIONS = 1000000

cumulative_evals = 0

FILE_STRING = "./OutputMR08-10.txt"

StatisticsDictionary = {}

#Objects for Genome and Population
class Genome:
    def __init__(self,
                 representation,
                 fitness):
        self.representation = representation
        self.fitness = fitness

class Population:
    def __init__(self, 
                 members, 
                 champion_fitness,
                 average_fitness):
        self.members = members
        self.champion_fitness = champion_fitness
        self.average_fitness = average_fitness

#Creates 
def InitializeGenome():
    rep = []

    #Each x value is a random float between -5.12 and 5.11
    for i in range(0, N):
        rep.append(random.uniform(-5.12, 5.11))

    #Create genome and set its fitness
    genome = Genome(rep, 0.0)
    genome.fitness = DeJongFitness(genome)
    return genome

def InitializePopulation():
    
    members = []

    #Create members of population with size mu
    for i in range(POPULATION_SIZE):
        members.append(InitializeGenome())
    
    #Create population with saved members
    population = Population(members, 0.0, 0.0)

    #AddPopulationStats returns a population with the added statistics (Champion fitness and average fitness)
    return AddPopulationStats(population)

def Crossover(parentOne, parentTwo):
    childOne = []
    childTwo = []
    
    crossover_point = random.randint(0, N)
    
    childOne = Genome(parentOne.representation[:crossover_point] + parentTwo.representation[crossover_point:], 0.0)
    childOne.fitness = DeJongFitness(childOne)

    childTwo = Genome(parentTwo.representation[:crossover_point] + parentOne.representation[crossover_point:], 0.0)
    childTwo.fitness = DeJongFitness(childTwo)

    return [childOne, childTwo]

def Mutation(genome):

    for i in range(0, len(genome.representation)):
        if random.uniform(0, 1) < MUTATION_RATE:
            genome.representation[i] = random.uniform(-5.12, 5.11)
    
    return genome


def MakeNewGeneration(population):

    newChildren = []
    parents = []

    totalFitness = sum(genome.fitness for genome in population.members)

    for i in range(0, POPULATION_SIZE):
        selectionChance = random.uniform(0, totalFitness)

        currentFitness = 0
        for genome in population.members:
            currentFitness += genome.fitness
            if currentFitness > selectionChance:
                parents.append(genome)
                break
        if len(parents) == 2:
            parents[0] = Mutation(parents[0])
            parents[1] = Mutation(parents[1])

            if random.uniform(0,1) < CROSSOVER_RATE:
                newChildren += Crossover(parents[0], parents[1])
            else:
                newChildren += parents
            parents = []

    #create population from survivors
    newPopulation = Population(newChildren, 0.0, 0.0)
    
    return AddPopulationStats(newPopulation)


def AddPopulationStats(population):
    championFitness = population.members[0].fitness
    totalFitness = 0


    for genome in population.members:

        #add fitness to cumulative to get average
        totalFitness += genome.fitness

        #check for champion fitness
        if genome.fitness > championFitness:
            championFitness = genome.fitness

    population.champion_fitness = championFitness
    population.average_fitness = totalFitness / len(population.members)

    return population

def DeJongFitness(genome):
    dejong = 1
    rep = genome.representation
    for i in range(0, len(rep)-1):
        dejong += 100*((rep[i+1]-(rep[i]**2))**2) + (rep[i]-1)**2

    return 1000 / dejong 

with open(FILE_STRING, "w") as os:
    population = InitializePopulation()
    cumulative_evals += POPULATION_SIZE

    os.write("DeJong Test Suite 2 GA {} {} Generation {} {} {} {}\n".format(
        POPULATION_SIZE, 
        0.0, 
        0, 
        cumulative_evals, 
        population.champion_fitness,
        population.average_fitness))


    for generation in range(1, NUMBER_OF_GENERATIONS):
        #create lambda population
        population = MakeNewGeneration(population)
        cumulative_evals += POPULATION_SIZE

        os.write("DeJong Test Suite 2 GA {} {} Generation {} {} {} {}\n".format(
        POPULATION_SIZE,
        0.0, 
        generation, 
        cumulative_evals, 
        population.champion_fitness,
        population.average_fitness))

        if population.average_fitness > 300:
            print("THRESHOLD MET - Generation " + str(generation))
            break


