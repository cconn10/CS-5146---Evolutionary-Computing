import random
import math
import json
import os

LAMBDA_SIZE = 100
MU_SIZE = 15
MUTATION_RATE = 0.05
NUMBER_OF_GENERATIONS = 1000

cumulative_evals = 0

FILE_STRING = "./Output.txt"

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
                 diversity, 
                 champion_fitness,
                 average_fitness):
        self.members = members
        self.diversity = diversity
        self.champion_fitness = champion_fitness
        self.average_fitness = average_fitness

#Returns fitness as key for list sort function
def getFitness(g):
    return g.fitness

#Creates 
def InitializeGenome():
    rep = []

    #X and Y values are a random float between -10 and 10
    rep.append(random.uniform(-10.0, 10.0))
    rep.append(random.uniform(-10.0, 10.0))

    #Sigma X and Sigma Y are a random Gaussian value with a mean of 0 and a standard deviation of one
    rep.append(random.gauss(0, 1))
    rep.append(random.gauss(0, 1))

    #Create genome and set its fitness
    genome = Genome(rep, 0.0)
    genome.fitness = HimmelblauFitness(genome)
    return genome

def InitializePopulation():
    
    members = []

    #Create members of population with size mu
    for i in range(MU_SIZE):
        members.append(InitializeGenome())
    
    #Create population with saved members
    population = Population(members, 0.0, 0.0, 0.0)

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
        if(random.uniform(0,100) > 100 * MUTATION_RATE):
            offspring = Mutation(offspring)

        #Get fitness of offspring
        offspring.fitness = HimmelblauFitness(offspring)

        members.append(offspring)

    #create population from members
    lambdaPop = Population(members, 0.0, 0.0, 0.0)

    return AddPopulationStats(lambdaPop)


def Recombination(parentOne, parentTwo):
    child = []

    #Using discrete recombination with the hope that the genomes with the highest fitness will be those who had 2 good parents
    #Additionally this means that if a very good parent makes offspring with a very bad parent, there's no chance that the offspring is
    #as bad as the parent, as it cannot directly take the bad parent's attributes
    for genotype in parentOne.representation:
        index = parentOne.representation.index(genotype)
        child.append((genotype + parentTwo.representation[index]) / 2.0)

    return child

def Mutation(genome):
    
    sigmaX = genome.representation[2]
    sigmaY = genome.representation[3]

    #For both x and y, there is a 50/50 chance that the mutation adds or subtracts from the variable
    #the number that is added/subtracted is randomly generated between 0 and the sigma value of the genome
    if random.randint(1,2) == 1:
        genome.representation[0] = genome.representation[0] + random.uniform(0, sigmaX)
    else:
        genome.representation[0] = genome.representation[0] - random.uniform(0, sigmaX)
    
    if random.randint(1,2) == 2:
        genome.representation[1] = genome.representation[1] + random.uniform(0, sigmaY)
    else:
        genome.representation[1] = genome.representation[1] - random.uniform(0, sigmaY)

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
    for i in range(5):
        lambdaPopulation.members.pop(len(lambdaPopulation.members)-1)

    #preserve the 5 genomes with the highest fitness to ensure we keep our current best genomes
    survivors = lambdaPopulation.members[0:5]

    for i in range(10):
        competitors = random.sample(lambdaPopulation.members, 9)

        for competitor in competitors:
            lambdaPopulation.members.remove(competitor)
        
        #Add tournament winners to list of survivors
        survivors.append(runTournament(competitors))

    #create population from survivors
    lambdaPopulation = Population(survivors, 0.0, 0.0, 0.0)
    
    return AddPopulationStats(lambdaPopulation)
    
def runTournament(competitors):

    #Run until there is one final winner
    while len(competitors) > 1:
        match = random.sample(competitors, 2)

        competitors.remove(match[0])
        competitors.remove(match[1])

        #Adds winner of match back to the end of the array to be cycled back during next round
        if(match[0].fitness < match[1].fitness):
            competitors.append(match[0])
        else:
            competitors.append(match[1])

    #Assign to winner variable as a prize for survival
    winner = competitors[0]

    return winner


def AddPopulationStats(population):
    championFitness = population.members[0].fitness
    totalFitness = 0
    maxDistance = 0.0


    for genome in population.members:

        #add fitness to cumulative to get average
        totalFitness += genome.fitness

        #check for champion fitness
        if genome.fitness < championFitness:
            championFitness = genome.fitness

        members = population.members

        #calculate distance between each member of the population and every other member
        #could definitely be done faster but I can't remember how
        for g in members:
            distance = math.dist([genome.representation[0], genome.representation[1]], [g.representation[0], g.representation[1]])
            if distance > maxDistance:
                maxDistance = distance

    population.champion_fitness = championFitness
    population.average_fitness = totalFitness / len(population.members)
    population.diversity = maxDistance

    return population

def HimmelblauFitness(genome):
    x = genome.representation[0]
    y = genome.representation[1]

    #Compute Himmelblau's function for the given genome
    himmelblau = (((x ** 2) + y - 11.0) ** 2) + ((x + (y ** 2) - 7) ** 2)

    return himmelblau 


with open(FILE_STRING, "w") as os:
    population = InitializePopulation()
    cumulative_evals += 100

    os.write("Himmelblau ES {} {} {} Generation {} {} {} {} {}\n".format(
        MU_SIZE, 
        LAMBDA_SIZE, 
        0.0, 
        0, 
        cumulative_evals, 
        population.champion_fitness,
        population.average_fitness,
        population.diversity ))


    for generation in range(1, NUMBER_OF_GENERATIONS):

        #create lambda population
        lambdaPopulation = CreateLambdaPopulation(population)

        #create mu population from lambda population
        muPopulation = SurvivorSelection(lambdaPopulation)
        cumulative_evals += 100

        os.write("Himmelblau ES {} {} {} Generation {} {} {} {} {}\n".format(
        MU_SIZE, 
        LAMBDA_SIZE, 
        0.0, 
        generation, 
        cumulative_evals, 
        muPopulation.champion_fitness,
        muPopulation.average_fitness,
        muPopulation.diversity ))


