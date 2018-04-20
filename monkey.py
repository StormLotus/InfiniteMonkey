import string
import random
import argparse
from curses import wrapper

# Class for DNA.
class DNA():
	def __init__(self, size=0):
		# Create random genome.
		self.genome = [random.choice(string.ascii_letters+" .?") for a in range(size)]
		self.fitness = 0

	def __str__(self):
		return ''.join(self.genome)

	def __getitem__(self, specimen):
		return specimen.fitness

	# Operations with DNA using fitness.
	def __gt__(self, other):
		if self.fitness > other.fitness:
			return True
		else:
			return False

	def __add__(self, other):
		if type(other) is DNA:
			return self.fitness + other.fitness
		else:
			return self.fitness + other

	def __radd__(self, other):
		if other == 0:
			return self.fitness
		else:
			return self.__add__(other)

	def __sub__(self, other):
		if type(other) is DNA:
			return self.fitness - other.fitness
		else:
			return self.fitness - other

	def __rsub__(self, other):
		if other == 0:
			return self.fitness
		else:
			return self.__sub__(other)

	def __cmp__(self, other):
		if self.fitness < other.fitness:
			return -1
		elif self.fitness > other.fitness:
			return 1
		else:
			return 0

	# Calculate fitness.
	def calcFitness(self, target):
		fitness = 0

		# Get hits.
		for i in range(len(self.genome)):
			if self.genome[i] == target[i]:
				fitness += 1

		# Divide by length.
		self.fitness = fitness/len(self.genome)

	# Crossover two DNAs.
	def crossOver(self, partner):
		child = DNA()

		# Get a midpoint from that divide parents, combine them for child.
		midpoint = random.randint(0, len(self.genome))
		child.genome = self.genome[:midpoint] + partner.genome[midpoint:]

		return child

	# Mutate gene.
	def mutate(self, mutationRate):
		# Each base has a chance of mutationRate to change to a random character.
		for i in range(len(self.genome)):
			if random.random() < mutationRate:
				self.genome[i] = random.choice(string.ascii_letters+" .?")

# Class for Population.
class Population():
	def __init__(self, target, mutationRate, size):
		# Save importante variables and create a vector of DNAs.
		self.target = target
		self.mutationRate = mutationRate
		self.population = [DNA(len(target)) for i in range(size)]
		self.matingPool = []
		self.finished = False

		# Calculate fitness of the population.
		self.calcFitness()

	def __str__(self):
		string = ''

		for specimen in self.population:
			string += specimen.__str__() + '\n'

		return string

	def __len__(self):
		return len(self.population)

	def __iter__(self):
		self.i = 0
		return self

	def __next__(self):
		if self.i < len(self):
			self.i += 1
			return self.population[self.i-1]
		else:
			raise StopIteration

	# Internal function for mapping the fitness.
	def _mapValues(self, value, leftMin, leftMax, rightMin, rightMax):
		# Figure out how 'wide' each range is.
		leftSpan = leftMax - leftMin
		rightSpan = rightMax - rightMin

		# Convert the left range into a 0-1 range (float).
		valueScaled = float(value - leftMin) / float(leftSpan)

		# Convert the 0-1 range into a value in the right range.
		return rightMin + (valueScaled * rightSpan)

	# Calculate the fitness of the population.
	def calcFitness(self):
		# Calculate fitness for each specimen.
		for specimen in self.population:
			specimen.calcFitness(self.target)

		# If there is someone with a 1 fitness change finished flag.
		if self.best().fitness == 1.0:
			self.finished = True

	# Create a mating pool.
	def naturalSelection(self):
		self.matingPool = []

		# Get max fitness and use that to map the fitness of the specimen for a new fitness.
		maxFitness = max(self.population)

		for specimen in self.population:
			fitness = self._mapValues(specimen,0,maxFitness,0,1)

			# The ammount of times a specimen enters the mating pool is proportional with the fitness.
			self.matingPool += [specimen]*int(fitness*100)

	# Generate a new population.
	def generate(self):
		size = len(self)
		self.population = []

		# Size times get two random partners from the mating pool and cross over with them, mutating the child after and adding him to the population.
		for i in range(size):
			partnerA = random.choice(self.matingPool)
			partnerB = random.choice(self.matingPool)

			child = partnerA.crossOver(partnerB)
			child.mutate(self.mutationRate)
			self.population.append(child)

	# Get the best specimen of the population.
	def best(self):
		best = max(self.population)
		return best

	# Get the average fitness.
	def averageFitness(self):
		return sum(self.population)/len(self)

# Main window for curses
def main(stdscr):
	# Clear screen
	stdscr.clear()

	# Running algorithm
	random.seed()

	# Parse arguments.
	parser = argparse.ArgumentParser(description='Genetic algorithm tests.')
	parser.add_argument('target')
	parser.add_argument('mutation_rate')
	parser.add_argument('size')
	args = parser.parse_args()

	# Create an initial population.
	population = Population(args.target, float(args.mutation_rate), int(args.size))

	# Add static information to the screen.
	stdscr.addstr(0,0, 'Target: ' + args.target)
	stdscr.addstr(1, 0, 'Total generations: ')
	stdscr.addstr(2, 0, 'Average fitness: ')
	stdscr.addstr(3, 0, 'Population: ' + str(args.size))
	stdscr.addstr(4, 0, 'Mutation rate: ' + str(int(float(args.mutation_rate)*100)) + '%')
	stdscr.addstr(5,0, '------------')
	stdscr.addstr(6,0, 'Best: ')
	stdscr.addstr(7,0, '------------')
	stdscr.addstr(8,0, 'Top 10: ')

	generations = 1
	while True:
		population.naturalSelection()
		population.generate()
		population.calcFitness()

		# Add dynamic information to the screen.
		stdscr.addstr(1, 19, str(generations))
		stdscr.addstr(2, 17, str(population.averageFitness()))
		stdscr.addstr(6, 6, str(population.best()) + '/' + str(population.best().fitness))
		
		# Show the top 10 specimen.
		top10 = sorted(population)[-10:]
		top10str = ''
		for specimen in top10:
			top10str += str(specimen) + '\n'
		stdscr.addstr(9, 0, top10str)

		# Refresh window.
		stdscr.refresh()
		
		generations += 1
		# If the target is reached end program.
		if population.finished:
			break

	stdscr.getkey()

wrapper(main)