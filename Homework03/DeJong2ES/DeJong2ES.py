import random
import math
import json
import os

N = 4
LAMBDA_SIZE = 100
MU_SIZE = 15
MUTATION_RATE = 0.1
NUMBER_OF_GENERATIONS = 1000000
PARENT_ONE_WEIGHT = 0.55
PARENT_TWO_WEIGHT = 0.45

cumulative_evals = 0

FILE_STRING = "./OutputRW5545-10.txt"

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

#Returns fitness as key for list sort function
def getFitness(g):
    return g.fitness

#Creates 
def InitializeGenome():
    rep = []

    #Each x value is a random float between -5.12 and 5.11
    for i in range(0, N):
        rep.append(random.uniform(-5.12, 5.11))

    #Sigma X and Sigma Y are a random Gaussian value with a mean of 0 and a standard deviation of one
    for i in range(0, N):
        rep.append(random.gauss(0, 1))

    #Create genome and set its fitness
    genome = Genome(rep, 0.0)
    genome.fitness = DeJongFitness(genome)
    return genome

def InitializePopulation():
    
    members = []

    #Create members of population with size mu
    for i in range(MU_SIZE):
        members.append(InitializeGenome())
    
    #Create population with saved members
    population = Population(members, 0.0, 0.0)

    #AddPopulationStats returns a population with the added statistics (Champion fitness, average fitness, and diversity)
    return AddPopulationStats(population)

def CreateLambdaPopulation(population):
    members = []

    #Create a population of offspring from randomly selected parents
    for i in range(LAMBDA_SIZE):

        #randomly select parents
        parents = ParentSelection(population)
        
        #perform recombination on parents
        offspring = Genome(Recombination(parents[0], parents[1]), 0.0)

        #Use rng to decide whether or not offspring mutates
        if(random.uniform(0,1) < MUTATION_RATE):
            offspring = Mutation(offspring)

        #Get fitness of offspring
        offspring.fitness = DeJongFitness(offspring)
        members.append(offspring)

    #create population from members
    lambdaPop = Population(members, 0.0, 0.0)

    return AddPopulationStats(lambdaPop)


def Recombination(parentOne, parentTwo):
    child = []

    #Using discrete recombination with the hope that the genomes with the highest fitness will be those who had 2 good parents
    #Additionally this means that if a very good parent makes offspring with a very bad parent, there's no chance that the offspring is
    #as bad as the parent, as it cannot directly take the bad parent's attributes
    for genotype in parentOne.representation:
        index = parentOne.representation.index(genotype)
        child.append(((PARENT_ONE_WEIGHT * genotype) + (PARENT_TWO_WEIGHT * parentTwo.representation[index])) / 2.0)

    return child

def Mutation(genome):
    

    #For both x and y, there is a 50/50 chance that the mutation adds or subtracts from the variable
    #the number that is added/subtracted is randomly generated between 0 and the sigma value of the genome
    for i in range(0, N):
        sigma = genome.representation[i + N]
        random_uniform = random.uniform(0, abs(sigma))
        if (random.randint(1,2) == 1 and genome.representation[i] + random_uniform <= 5.12) or genome.representation[i] - random_uniform >= -5.11:
            genome.representation[i] = genome.representation[i] + random_uniform
        else:
            genome.representation[i] = genome.representation[i] - random_uniform

    return genome

def ParentSelection(muPopulation):
    #randomly chooses two parents
    parents = random.sample(muPopulation.members, 2)
    
    return parents

def SurvivorSelection(lambdaPopulation):

    survivors = []

    #sort members from best to worst
    lambdaPopulation.members.sort(key=getFitness)

    #remove the 5 genomes with the lowest fitness to prevent them from surviving
    lambdaPopulation.members = lambdaPopulation.members[5:]

    #preserve the 5 genomes with the highest fitness to ensure we keep our current best genomes
    survivors = lambdaPopulation.members[len(lambdaPopulation.members)-5:]

    for i in range(10):
        competitors = random.sample(lambdaPopulation.members, 9) if len(lambdaPopulation.members) > 9 else lambdaPopulation.members
        
        for competitor in competitors:
            lambdaPopulation.members.remove(competitor)

        #Add tournament winners to list of survivors
        survivors.append(runTournament(competitors))

    #create population from survivors
    lambdaPopulation = Population(survivors, 0.0, 0.0)
    
    return AddPopulationStats(lambdaPopulation)
    
def runTournament(competitors):

    #Run until there is one final winner
    while len(competitors) > 1:
        match = random.sample(competitors, 2)

        competitors.remove(match[0])
        competitors.remove(match[1])

        #Adds winner of match back to the end of the array to be cycled back during next round
        if(match[0].fitness > match[1].fitness):

            competitors.append(match[0] if random.uniform(0, 1) > 0.2 else match[1])
        else:
            competitors.append(match[1] if random.uniform(0, 1) > 0.2 else match[0])

    #Assign to winner variable as a prize for survival
    winner = competitors[0]

    return winner


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
    for i in range(0, N-1):
        dejong += 100*((rep[i+1]-(rep[i]**2))**2) + (rep[i]-1)**2

    return 1000 / dejong 


with open(FILE_STRING, "w") as os:
    population = InitializePopulation()
    cumulative_evals += 100

    os.write("DeJong Test Suite 2 ES {} {} {} Generation {} {} {} {}\n".format(
        MU_SIZE, 
        LAMBDA_SIZE, 
        0.0, 
        0, 
        cumulative_evals, 
        population.champion_fitness,
        population.average_fitness))


    for generation in range(1, NUMBER_OF_GENERATIONS):

        #create lambda population
        lambdaPopulation = CreateLambdaPopulation(population)

        #create mu population from lambda population
        population = SurvivorSelection(lambdaPopulation)
        cumulative_evals += 100

        os.write("DeJong Test Suite 2 ES {} {} {} Generation {} {} {} {}\n".format(
        MU_SIZE, 
        LAMBDA_SIZE, 
        0.0, 
        generation, 
        cumulative_evals, 
        population.champion_fitness,
        population.average_fitness))

        
        if population.average_fitness > 300:
            print("THRESHOLD MET - Generation " + str(generation))
            break


