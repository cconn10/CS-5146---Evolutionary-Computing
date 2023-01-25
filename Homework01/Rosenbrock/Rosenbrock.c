
/****************************************************************************/
/* Program:     Homework 1                                                  */
/* Programmer:  Colin Conn                                                  */
/* Version:     3.0                                                         */
/* Date:        January 23, 2023                                            */ 
/*                                                                          */
/****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "../rng.h"		
#include "../rng.c"

//I made these global constants so they could be easily changed 
const int GENERATION_LIMIT = 10000;
const int POP_SIZE = 100;
const int BIT_STRING_LENGTH = 32;
const double MUATION_RATE = 0.01;
const double CROSSOVER_RATE = 0.5;


typedef struct genome_s
{ 
    int genome_len;
    char *bit;       
    double fitness;       
} genome_t;

typedef struct population_s
{ 
    int member_count;
    genome_t *member;
    double percent_identical;
    double champion_fitness;
    double average_fitness;
} population_t;

//Allocates memory to contain a genome
void SGA_Genome_Malloc(genome_t *genome, int length)
{   
    (*genome).bit = (char *)malloc(sizeof(char)*length);
    (*genome).genome_len = length;
    (*genome).fitness = 0.0;
}

//Deallocates memory containing a genome
void SGA_Genome_Free(genome_t *genome)
{  
    free((*genome).bit);
    (*genome).genome_len = 0;
}

//Loops through each member of the population and allocates memory for each genome
void SGA_Population_Malloc(population_t *population, int member_count, int genome_length)
{  
    int member_c;
    
    (*population).percent_identical = 0.0;
    (*population).member_count = member_count;
    (*population).member = (genome_t *)malloc(member_count * sizeof(genome_t));
    for (member_c=0; member_c < member_count; member_c++)
        SGA_Genome_Malloc(&((*population).member[member_c]), genome_length);	
}

//Copies the bitstring and fitness from <source_genome> to <destination-genome>
void SGA_Genome_Copy(genome_t *source_genome, genome_t *destination_genome)
{ 
    int bit_pos;
    if ((*source_genome).genome_len != (*destination_genome).genome_len)
    {fprintf(stderr, "ERROR in SGA_Genome_Copy: Source and Destination of Unequal Length\n");
        exit(0);
    }

    (*destination_genome).fitness = (*source_genome).fitness;
    for (bit_pos=0; bit_pos<(*destination_genome).genome_len; bit_pos++)
        (*destination_genome).bit[bit_pos] = (*source_genome).bit[bit_pos];
}

//Loops through population and copies data for each genome 
void SGA_Population_Copy(population_t *source_population, population_t *destination_population)
{ 
    int p_count;
    if ((*source_population).member_count != (*destination_population).member_count)
    {fprintf(stderr, "ERROR in SGA_Population_Copy: Source and Destination of Unequal Sizes\n");
        exit(0);
    }
    for (p_count=0; p_count < (*source_population).member_count; p_count++)
        SGA_Genome_Copy(&((*source_population).member[p_count]),&((*destination_population).member[p_count]));
}

//Initializes a genome, creating its bitstring and setting its fitness to 0.0
void SGA_Genome_Init(genome_t *genome, RNG *rng) 
{ 
    int bit_count;
    for (bit_count=0; bit_count < (*genome).genome_len; bit_count++)
        if (rng_uniform01(rng) < 0.5)
            (*genome).bit[bit_count] = 0;
        else
            (*genome).bit[bit_count] = 1;
    (*genome).fitness = 0.0;
}

//Loops through the population and initializes each genome
void SGA_Population_Init(population_t *population, RNG *rng)
{ 
    int m_count;
    for (m_count=0; m_count < (*population).member_count; m_count++)
        SGA_Genome_Init(&((*population).member[m_count]), rng);
}	

//
double SGA_Genome_Decode(genome_t *genome, int start, int end, double min, double max)
{ 
    double return_value;
    double max_decimal_value;
    double decimal_value;
    int    bit_count;	
    int    bit_pos;

    decimal_value = 0.0;
    max_decimal_value = 0.0;
    bit_count = 0;
    for (bit_pos=end; bit_pos>=start; bit_pos--)
    { 
        decimal_value     += (double)((*genome).bit[bit_pos])*pow(2.0, (double)bit_count);
        max_decimal_value += pow(2.0,(double)bit_count);
        bit_count++;
    }

    return_value = min + (max-min)*(decimal_value/max_decimal_value);	
    return return_value;

}

//Loops through each bit of a genome, then runs a random number generator
//if the random number is lower than the mutation rate, flip the bit
void SGA_Genome_Mutate(genome_t *genome, double mutation_rate, RNG *rng)
{ 
    int bit_count;
    for (bit_count=0; bit_count < (*genome).genome_len; bit_count++)
        if (rng_uniform01(rng) < mutation_rate)
            switch ((*genome).bit[bit_count])
            { case 0: (*genome).bit[bit_count] = 1;
                        break;
                case 1: (*genome).bit[bit_count] = 0;
                        break;
            }
	 
}

//Uses rng to pick a crossover point in the bitstring and then crosses over the sections of
//<parent_genome_1> and <parent_genome_2>
void SGA_Genome_1P_Crossover(genome_t *parent_genome_1, genome_t *parent_genome_2, RNG *rng)
{ 
    int bit_count;
    int crossover_point;	
    genome_t child_genome_1, child_genome_2;

    SGA_Genome_Malloc(&child_genome_1, (*parent_genome_1).genome_len);
    SGA_Genome_Malloc(&child_genome_2, (*parent_genome_1).genome_len);
    crossover_point = (int)round(rng_uniform(rng, 0.0, (double)(*parent_genome_1).genome_len));

    for (bit_count = 0; bit_count < crossover_point; bit_count++)
        { (child_genome_1).bit[bit_count] = (*parent_genome_1).bit[bit_count];
        (child_genome_2).bit[bit_count] = (*parent_genome_2).bit[bit_count];
        }

    for (; bit_count < (*parent_genome_1).genome_len; bit_count++)
        { (child_genome_1).bit[bit_count] = (*parent_genome_2).bit[bit_count];
        (child_genome_2).bit[bit_count] = (*parent_genome_1).bit[bit_count];
        }	 

    SGA_Genome_Copy(&child_genome_1, parent_genome_1);
    SGA_Genome_Copy(&child_genome_2, parent_genome_2); 

    SGA_Genome_Free(&child_genome_1);
    SGA_Genome_Free(&child_genome_2); 
}

// Creates a roulette wheel to choose parents to copy as children,
// mutate, and then crossover
void SGA_Population_Make_New_Generation(population_t *old_population, 
                                        population_t *new_population,
                                        double       mutation_rate,
                                        double       crossover_rate,
										RNG          *rng)

{  double sum_of_fitness_scores;
   double *roulette_wheel;
   double max_raw_fitness, min_raw_fitness;
   int m_count;

   int parent_one_index;
   int parent_two_index;
   double die_roll;

	roulette_wheel = (double *)malloc(sizeof(double)*(*old_population).member_count); 

    max_raw_fitness = min_raw_fitness = 0.0;
	for (m_count = 0; m_count < (*old_population).member_count; m_count++)
	   { if (((*old_population).member[m_count]).fitness > max_raw_fitness)
		     max_raw_fitness = ((*old_population).member[m_count]).fitness;	
		 if (((*old_population).member[m_count]).fitness < min_raw_fitness)
			     min_raw_fitness = ((*old_population).member[m_count]).fitness;
		}	    

	for (m_count = 0; m_count < (*old_population).member_count; m_count++)
	    roulette_wheel[m_count] = ((*old_population).member[m_count]).fitness;
	
	for (m_count = 0; m_count < (*old_population).member_count; m_count++)
		roulette_wheel[m_count] -= min_raw_fitness;

	for (m_count = 0; m_count < (*old_population).member_count; m_count++)
		roulette_wheel[m_count] += 1.0;
	
	sum_of_fitness_scores = 0.0;
	for (m_count = 0; m_count < (*old_population).member_count; m_count++)
		sum_of_fitness_scores += roulette_wheel[m_count];
	
	for (m_count = 0; m_count < (*old_population).member_count; m_count++)
		roulette_wheel[m_count] /= sum_of_fitness_scores;
		
    for (m_count = 1; m_count < (*old_population).member_count; m_count++)
		roulette_wheel[m_count] += roulette_wheel[m_count-1];

    for (m_count = 0; m_count < (*old_population).member_count-1; m_count++)
    {
        die_roll = rng_uniform01(rng);
        parent_one_index = 0;
        while (roulette_wheel[parent_one_index] < die_roll) parent_one_index++;
        die_roll = rng_uniform01(rng);
        parent_two_index = 0;
        while (roulette_wheel[parent_two_index] < die_roll) parent_two_index++;

        SGA_Genome_Copy( &((*old_population).member[parent_one_index]),&((*new_population).member[m_count]));
        SGA_Genome_Copy( &((*old_population).member[parent_two_index]),&((*new_population).member[m_count+1]));
    
        SGA_Genome_Mutate(&((*new_population).member[m_count]), mutation_rate,rng);
        SGA_Genome_Mutate(&((*new_population).member[m_count+1]), mutation_rate,rng);

        if (rng_uniform01(rng) < crossover_rate)
            SGA_Genome_1P_Crossover(&((*new_population).member[m_count]),&((*new_population).member[m_count+1]),rng);
			
    }
}


double SGA_Rosenbrock_Fitness(genome_t *genome)
{
    int bit_position;
    double one_count = 0.0;

    // Go through each bit of the genotype and increment every time a one is seen
    for (bit_position = 0; bit_position < (*genome).genome_len; bit_position++)
        one_count += (double)(*genome).bit[bit_position];

    // Fitness = ratio of ones : total length
    return one_count / (double)(*genome).genome_len;
}

void SGA_Population_Compute_Fitness(population_t *population)
{ 
    int m_count;
    double fitness_sum;
    double fitness;
    double max_raw_fitness = 0.0;

    //loop through each member of the population
    for (m_count = 0; m_count < (*population).member_count; m_count++)
    {
        //calculate the fitness of each member
        ((*population).member[m_count]).fitness = SGA_Max_Ones_Fitness(&((*population).member[m_count]));

        //add the sum to the total sum of all members
        fitness_sum += ((*population).member[m_count]).fitness;

        //check to see if that fitness is the highest seen so far
        if (((*population).member[m_count]).fitness > max_raw_fitness)
            max_raw_fitness = ((*population).member[m_count]).fitness;
        }
    //Average fitness = sum of fitness divided by population size
    (*population).average_fitness = fitness_sum / (*population).member_count;
    (*population).champion_fitness = max_raw_fitness;

    /* 
        I couldn't get percent identical to work correctly.

        My plan was to take the current genome whose fitness was computed
        and check that bitstring to see if any others were the same string. If the
        bitstring was unique I would increment a count. Then the percentage that was
        identical would (kinda) be the total number of members of the population minus
        the number of unique bitstrings in the population.

        My other theory was to do the same but with fitness values, where any string with the same 
        fitness was considered "identical," but that felt incorrect.
    */
    (*population).percent_identical = ((double)(((*population).member_count) - 1) / (double)(*population).member_count) * 100.0;
}

int main()
{
	RNG *random_number_generator;
	population_t POPULATION,POPULATION2;
	int generation_count;

	random_number_generator = rng_create();
	
	SGA_Population_Malloc(&POPULATION,  75, BIT_STRING_LENGTH);
	SGA_Population_Malloc(&POPULATION2, 75, BIT_STRING_LENGTH); 
	
	SGA_Population_Init(&POPULATION,random_number_generator);
	SGA_Population_Compute_Fitness(&POPULATION);

    printf("MaxOnes %d %d %.2f %.2f\n", POP_SIZE, BIT_STRING_LENGTH, MUATION_RATE, CROSSOVER_RATE);
	
	for (generation_count = 0; generation_count < GENERATION_LIMIT ; generation_count++)
    {  
        SGA_Population_Compute_Fitness(&POPULATION); 
        SGA_Population_Make_New_Generation(&POPULATION, &POPULATION2, MUATION_RATE, CROSSOVER_RATE, random_number_generator);
        SGA_Population_Copy(&POPULATION2, &POPULATION);

	    SGA_Population_Compute_Fitness(&POPULATION);
        printf("%d %lf %lf %.2f%% Identical\n", generation_count + 1, (*(&POPULATION)).champion_fitness, (*(&POPULATION)).average_fitness, (*(&POPULATION)).percent_identical);

        if((*(&POPULATION)).percent_identical == 100.0){
            printf("ALGORITHM TERMINATED: Population Converged");
            break;
        }
    }

    if((*(&POPULATION)).percent_identical != 100.0)
        printf("ALGORITHM TERMINATED: Reached %d Generations", GENERATION_LIMIT);

}
