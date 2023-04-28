import random
import math
import os

CLASSES = ["artificer", "bard", "barbarian", "cleric", "druid", "fighter", "monk", "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard"]

LAMBDA_SIZE = 100
MU_SIZE = 20
MUTATION_RATE = 0.1
NUMBER_OF_GENERATIONS = 10000

PROFICIENCY_BONUS = 2

TARGET_AC = 16
KLARG_STATS = [9, 11, 8, 13, 14, 15]

FILE_STRING = "outputMagic.txt"
LAST_POPULATION_FILE = "magic_population.txt"

StatisticsDictionary = {}

#Objects for Genome and Population
#Representation = [class, CHA, WIS, INT, CON, DEX, STR]
class Genome:
    def __init__(self,
                 representation,
                 fitness):
        self.representation = representation
        self.fitness = fitness

class Population:
    def __init__(self, 
                 members, 
                 champion,
                 champion_fitness,
                 average_fitness):
        self.members = members
        self.champion = champion
        self.champion_fitness = champion_fitness
        self.average_fitness = average_fitness

#Returns fitness as key for list sort function
def getFitness(g):
    return g.fitness

#Creates Genomes
def InitializeGenome(pointBuy):
    rep = []

    rep.append(CLASSES[random.randint(0, len(CLASSES) - 1)])

    # Assign a 10 to each stat
    for i in range(0, 6):
        rep.append(10)
    
    for i in range(0, pointBuy):
        randStat = random.randint(1,6)
        if rep[randStat] + 1 <= 18:
            rep[randStat] += 1

    #Create genome and set its fitness
    genome = Genome(rep, 0.0)
    genome.fitness = Objective(genome)
    return genome

def InitializePopulation(pointBuy):
    
    members = []

    #Create members of population with size mu
    for i in range(MU_SIZE):
        members.append(InitializeGenome(pointBuy))
    
    #Create population with saved members
    population = Population(members, 0.0, "", 0.0)

    #AddPopulationStats returns a population with the added statistics (Champion fitness, average fitness, and diversity)
    return AddPopulationStats(population)

def CreateLambdaPopulation(population, pointBuy):
    members = []
    offspringSet = []

    #Create a population of offspring from randomly selected parents
    for i in range(10):
        offspringRep = []
        offspringSet = []

        #randomly select parents
        parents = ParentSelection(population)

        for i in range(10):
            offspringRep = []
            while len(offspringRep) < 7 or sum(offspringRep[1:]) != (60 + pointBuy):
                #perform recombination on parents
                offspringRep = Recombination(parents[0], parents[1])
            
            offspring = Genome(offspringRep, 0.0)

            #Use rng to decide whether or not offspring mutates
            if(random.uniform(0,1) < MUTATION_RATE):
                offspring = Mutation(offspring)

            #Get fitness of offspring
            offspring.fitness = Objective(offspring)
            members.append(offspring)
            offspringSet.append(offspring)

        population.members.remove(parents[0])
        population.members.remove(parents[1])

    #create population from members
    lambdaPop = Population(members, 0.0, "", 0.0)

    return AddPopulationStats(lambdaPop)


def Recombination(parentOne, parentTwo):

    #Using discrete recombination with the hope that the genomes with the highest fitness will be those who had 2 good parents
    #Additionally this means that if a very good parent makes offspring with a very bad parent, there's no chance that the offspring is
    #as bad as the parent, as it cannot directly take the bad parent's attributes
    child = []

    child.append(parentOne.representation[0] if random.randint(1,2) == 1 else parentTwo.representation[0])

    for i in range(1,7):
        child.append(int(parentOne.representation[i]) if random.randint(1,2) == 1 else int(parentTwo.representation[i]))

    return child

def Mutation(genome):
    
    toIndex = 0
    fromIndex = 0
    if(random.randint(1,2) == 1):
        genome.representation[0] = CLASSES[random.randint(0, len(CLASSES)-1)]
    else:
        while True:
            toIndex = random.randint(1,6)
            fromIndex = random.randint(1,6)
            
            if(genome.representation[fromIndex] - 1 >= 10 and genome.representation[toIndex] + 1 <= 18):
                genome.representation[fromIndex] -= 1
                genome.representation[toIndex] += 1
                break

    return genome

def ParentSelection(muPopulation):
    #randomly chooses two parents
    parents = random.sample(muPopulation.members, 2)
            
    return parents

def SurvivorSelection(lambdaPopulation):

    survivors = []

    #sort members from best to worst
    lambdaPopulation.members.sort(key=lambda g: g.fitness)
    # #remove the 5 genomes with the lowest fitness to prevent them from surviving
    # lambdaPopulation.members = lambdaPopulation.members[5:]

    # #preserve the 5 genomes with the highest fitness to ensure we keep our current best genomes
    # survivors = lambdaPopulation.members[len(lambdaPopulation.members)-5:]

    for i in range(20):
        competitors = random.sample(lambdaPopulation.members, 5) if len(lambdaPopulation.members) > 5 else lambdaPopulation.members
        
        for competitor in competitors:
            lambdaPopulation.members.remove(competitor)

        #Add tournament winners to list of survivors
        survivors.append(runTournament(competitors))

    #create population from survivors
    population = Population(survivors, 0.0, "", 0.0)
    
    return AddPopulationStats(population)
    
def runTournament(competitors):

    #Run until there is one final winner
    while len(competitors) > 1:
        match = random.sample(competitors, 2)

        competitors.remove(match[0])
        competitors.remove(match[1])

        #Adds winner of match back to the end of the array to be cycled back during next round
        if(match[0].fitness > match[1].fitness):
            threshold = match[1].fitness / (match[0].fitness + match[1].fitness)
            competitors.append(match[0] if random.uniform(0, 1) > threshold else match[1])
        else:
            threshold = match[0].fitness / (match[0].fitness + match[1].fitness)
            competitors.append(match[1] if random.uniform(0, 1) > threshold else match[0])

    #Assign to winner variable as a prize for survival
    winner = competitors[0]

    return winner


def AddPopulationStats(population):
    champion = population.members[0]
    championFitness = population.members[0].fitness
    totalFitness = 0


    for genome in population.members:

        #add fitness to cumulative to get average
        totalFitness += genome.fitness

        #check for champion fitness
        if genome.fitness > championFitness:
            championFitness = genome.fitness
            champion = genome

    population.champion = champion
    population.champion_fitness = championFitness
    population.average_fitness = totalFitness / len(population.members)

    return population


def Objective(genome):
    rep = genome.representation

    charClass = rep[0]
    charisma = rep[1]
    wisdom = rep[2]
    intelligence = rep[3]
    constitution = rep[4]
    dexterity = rep[5]
    strength = rep[6]

    defCHA = KLARG_STATS[0]
    defWIS = KLARG_STATS[1]
    defINT = KLARG_STATS[2]
    defCON = KLARG_STATS[3]
    defDEX = KLARG_STATS[4]
    defSTR = KLARG_STATS[5]

    atkDamage = 0
    damageBonus = 0

    saveDamage = 0

    toHit = 0
    toHitBonus = 0

    DPR = 0

    match str(charClass).lower():
        case "artificer":
            # 3d8 for spell
            saveDamage = 4.5 + 4.5 + 4.5

            DPR = calculate_dpr_save(defDEX, calculate_save(intelligence), saveDamage, False)

        case "bard":
            # 2d8 for spell
            saveDamage = 4.5 + 4.5

            DPR = calculate_dpr_save(defCON, calculate_save(charisma), saveDamage, True)

        case "barbarian":
            damageBonus = 2.0 + calculate_bonus(strength)
            # 2d6 for weapon attack
            atkDamage = 3.5 + 3.5 + damageBonus

            toHit = calculate_bonus(strength) + PROFICIENCY_BONUS

            DPR = calculate_dpr_atk_roll(toHit, atkDamage)

        case "cleric":
            # 3d10 for spell
            atkDamage = 5.5 + 5.5 + 5.5
            toHit = calculate_bonus(wisdom) + PROFICIENCY_BONUS

            DPR = calculate_dpr_atk_roll(toHit, atkDamage)

        case "druid":
            # 1d10 for spell attack
            # 2d6 for spell save
            atkDamage = 5.5 
            saveDamage = 3.5 + 3.5

            toHit = calculate_bonus(wisdom) + PROFICIENCY_BONUS

            DPR = calculate_dpr_atk_roll(toHit, atkDamage) + calculate_dpr_save(defDEX, calculate_save(wisdom), saveDamage, False)

        case "fighter":
            damageBonus = calculate_bonus(strength)
            # 2d6 for weapon attack
            atkDamage = 3.5 + 3.5 + damageBonus

            toHitBonus = 2.0
            toHit = calculate_bonus(strength) + PROFICIENCY_BONUS + toHitBonus

            DPR = calculate_dpr_atk_roll(toHit, atkDamage)

        case "monk":
            damageBonus = calculate_bonus(dexterity)
            # 1d8 for weapon attack
            # 1d4 for bonus unarmed strike
            atkDamage = 4.5 + 2.5 + damageBonus

            toHit = calculate_bonus(dexterity) + PROFICIENCY_BONUS

            DPR = calculate_dpr_atk_roll(toHit, atkDamage)

        case "paladin":
            damageBonus = calculate_bonus(strength)
            # 2d6 for weapon attack
            atkDamage = 3.5 + 3.5 + damageBonus 

            toHit = calculate_bonus(strength) + PROFICIENCY_BONUS

            DPR = calculate_dpr_atk_roll(toHit, atkDamage)

        case "ranger":
            damageBonus = calculate_bonus(dexterity)
            # 1d10 for weapon attack
            atkDamage = 5.5 + damageBonus

            toHit = calculate_bonus(dexterity) + PROFICIENCY_BONUS

            DPR = calculate_dpr_atk_roll(toHit, atkDamage)

        case "rogue":
            damageBonus = calculate_bonus(dexterity)
            atkDamage = 5.5 + 3.5 + damageBonus

            toHit = calculate_bonus(dexterity) + PROFICIENCY_BONUS

            DPR = calculate_dpr_atk_roll(toHit, atkDamage)

        case "sorcerer":
            # 3d10 for spell
            atkDamage = 5.5 + 5.5 + 5.5

            # Class feature adds 2d4 on miss (effective +3 to hit)
            toHitBonus = 1.5 + 1.5
            toHit = calculate_bonus(charisma) + PROFICIENCY_BONUS + toHitBonus

            DPR = calculate_dpr_atk_roll(toHit, atkDamage)

        case "warlock":
            # 1d8 for class feature attack
            # 2d6 for spell save
            atkDamage = 4.5 
            saveDamage = 3.5 + 3.5

            toHit = calculate_bonus(charisma) + PROFICIENCY_BONUS

            DPR = calculate_dpr_atk_roll(toHit, atkDamage) + calculate_dpr_save(defSTR, calculate_save(charisma), saveDamage, True)

        case "wizard":
            #Commented out because it is a strong local optima and throws stats out the window
            # # Magic Missile: 3d4 + 3 damage, no save no attack roll
            # atkDamage = 2.5 + 2.5 + 2.5
            # damageBonus = 3
            
            # DPR = atkDamage + damageBonus
            
            # 3d8 for spell
            toHit = calculate_bonus(intelligence) + PROFICIENCY_BONUS
            atkDamage = 4.5 + 4.5 + 4.5

            DPR = calculate_dpr_atk_roll(toHit, atkDamage)

    return DPR

# toHit = bonus that PC adds to attack
# damage = average damage roll for attack
def calculate_dpr_atk_roll(toHit, damage):

    hitChance = 1 - ((TARGET_AC - toHit) / 20)

    return (hitChance * damage)

# toSave = bonus that defender adds to save roll
# saveDC = threshold defender must beat to avoid damage
# damage = average damage roll for spell
# halfOnSave = boolean for whether defender takes half damage when they save
def calculate_dpr_save(toSave, saveDC, damage, halfOnSave):

    # Chance that target will fail save
    failChance = ((saveDC - calculate_bonus(toSave)) / 20)

    return (failChance * damage) if not halfOnSave else ((failChance * damage) + ((1 - failChance) * (damage / 2)))

def calculate_save(score):
    return 8 + calculate_bonus(score) + PROFICIENCY_BONUS

def calculate_bonus(score):
    return math.floor((score - 10.0) / 2.0)

def printStats(out, generation, population):
    #CHA, WIS, INT, CON, DEX, STR
    out.write("Generation {} | Average Fitness: {}\n\tChampion: {}, CHA {}, WIS {}, INT {}, CON {}, DEX {}, STR {} - FITNESS {}\n".format(
    generation, 
    population.average_fitness,
    population.champion.representation[0],
    population.champion.representation[1],
    population.champion.representation[2],
    population.champion.representation[3],
    population.champion.representation[4],
    population.champion.representation[5],
    population.champion.representation[6],
    population.champion_fitness))

with open(FILE_STRING, "w") as os:
    with open(LAST_POPULATION_FILE, "w") as lastPop:

        while True:
            print("How many points do you have to spend? (3 - 15)")
            
            points = int(input())
            if points < 3 or points > 15:
                print("INVALID INPUT")
            else:
                break

        population = InitializePopulation(points)
            

        os.write("DND 5e Character Generator | ES | Mu: {} | Lambda: {} |  Generation {} | Average Fitness: {}\n\tChampion: {}, CHA {}, WIS {}, INT {}, CON {}, DEX {}, STR {} | FITNESS {}\n".format(
        MU_SIZE, 
        LAMBDA_SIZE,
        0,
        population.average_fitness,
        population.champion.representation[0],
        population.champion.representation[1],
        population.champion.representation[2],
        population.champion.representation[3],
        population.champion.representation[4],
        population.champion.representation[5],
        population.champion.representation[6],
        population.champion_fitness))

        for genome in population.members:
            lastPop.write("{}, CHA {}, WIS {}, INT {}, CON {}, DEX {}, STR {}, FITNESS {}\n".format(
                genome.representation[0],
                genome.representation[1],
                genome.representation[2],
                genome.representation[3],
                genome.representation[4],
                genome.representation[5],
                genome.representation[6],
                genome.fitness
            ))
        lastPop.write("\n")

        for generation in range(1, NUMBER_OF_GENERATIONS):

            #create lambda population
            lambdaPopulation = CreateLambdaPopulation(population, points)

            #create mu population from lambda population
            population = SurvivorSelection(lambdaPopulation)

            if(generation % 100 == 0):
                printStats(os, generation, population)

            
            if population.average_fitness > 27:
                print("THRESHOLD MET - Generation " + str(generation))
                printStats(os, generation, population)
                break

            for genome in population.members:
                lastPop.write("{}, CHA {}, WIS {}, INT {}, CON {}, DEX {}, STR {}, FITNESS {}\n".format(
                    genome.representation[0],
                    genome.representation[1],
                    genome.representation[2],
                    genome.representation[3],
                    genome.representation[4],
                    genome.representation[5],
                    genome.representation[6],
                    genome.fitness
                ))
            lastPop.write("\n")


