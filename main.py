import random as r
import json
from sets import Set

from generate import *
from spell import *

# ok ml time

# x, our instance variable, is the set of tokens we can use to form a spell
# m is our objective function, generally the same as Fg in unconstrainted optimization
#   problems, but not in constrained optimization problems (such as this one), nor
#   in decision problems
# sol is the set of sequences of tokens which form spells that can be cast
# ans is the set of all sequences of tokens
# S is our search space, a subset of ans with the property that at least one optimal
#   element of sol is present
# N, our neighborhood function, represents a transformation from one element of S
#   to another. A graph built from this function should be connected
# Fg, our guiding function, maps elements of ans to F (the fitness values) and is
#   able to produce a consistent ordering of the elemnts of F. Note that in the
#   case where sol and ans are the same, F will need to produce an evaluation for
#   some elements of ans which m doesn't need to worry about. in this case, spells
#   which produce compilation errors

def N (s):
  s = s.clone()

  # random neighbor
  if r.randrange(100) < 10:
    # target section mutation
    mutation_type = r.choice(['change shape', 'add attunement', 'remove attunement'])
    if mutation_type == 'remove attunement':
      if len(s.td_symbols) > 1:
        length = len(s.td_symbols)
        s.remove_symbol('target declaration', r.randrange(1, length))
      else:
        mutation_type = 'add attunement'
    if mutation_type == 'add attunement':
      s.add_symbol('target declaration', rs_attunement())
    elif mutation_type == 'change shape':
      s.change_symbol('target declaration', 0, rs_shape())

  else:
    # code section mutation
    mutation_type = r.choice(['add symbol', 'change symbol', 'remove symbol'])
    if mutation_type == 'remove symbol':
      if len(s.c_symbols) < 2:
        mutation_type = 'change symbol'
      else:
        length = len(s.c_symbols)
        s.remove_symbol('code', r.randrange(length))
    if mutation_type == 'change symbol':
      if len(s.c_symbols) == 0:
        mutation_type = 'add symbol'
      else:
        s.change_symbol('code', r.randrange(len(s.c_symbols)), random_symbol(None))
    if mutation_type == 'add symbol':
      s.add_symbol('code', random_symbol(None))

  return s

def Fg (s):
  if len(s.compiled) == 0:
    s.compile()

  nonnegative = 0
  for n in [s.a, s.b, s.c]:
    if n >= 0:
      nonnegative += 1

  abc = s.a + s.b + s.c
  fitness = min(s.a, s.b, s.c)

  x0 = len(s.toggles)
  x0 = max(0, -(x0-3)**2 + 5)
  fitness += x0

  words = s.words().split(' ')
  x1 = len(words)
  x1 = max(0, -(x1-8)**2 + 5)
  fitness += x1

  types = Set()
  for word in words:
    types.add(by_word[word].type)
  x2 = len(types)
  x2 = max(0, -(x2-4)**2 + 5)
  fitness += x2

  fitness = max(1, fitness + 1)

  error = -s.compilation_errors

  return (error, nonnegative, abc, fitness)

LOCAL_SEARCH_GENERATIONS = 30
def local_search (current):
  terminate = False
  generation = 0
  while not terminate:
    next = N(current)

    if Fg(next) > Fg(current):
      current = next

    if generation > LOCAL_SEARCH_GENERATIONS:
      terminate = True
    generation += 1

  return current

def generate_initial_population (sz):
  pop = []
  for i in range(sz):
    c = generate_random_configuration()
    c = local_search(c)
    pop.append(c)

  return pop

def generate_random_configuration ():
  s = Spell()
  s.add_symbol('target declaration', rs_shape())
  s.add_symbol('code', random_symbol(None))

  return s

def mutate_individual (individual):
  return N(individual)

def mate_individuals (*parents):
  total = sum([Fg(parent)[3] for parent in parents]) + len(parents)

  child = Spell()
  most_fit_parent = None
  most_fitness = -10000

  i = 0
  done = False
  while not done:
    which = r.randrange(total)

    for parent in parents:
      fitness = Fg(parent)[3]
      if fitness > most_fitness:
        most_fitness = fitness
        most_fit_parent = parent

      if which - fitness <= 0:
        if i >= len(parent.c_symbols):
          done = True
        else:
          child.add_symbol('code', parent.c_symbols[i])
          i += 1
          break
      else:
        which -= fitness

  child.td_symbols = [td for td in most_fit_parent.td_symbols]
  return child

CULLING_PERCENT = 0.5
def op_selection (pop):
  new_size = int(len(pop) * CULLING_PERCENT)
  return sorted(pop, key=Fg, reverse=True)[:new_size]

def op_recombination (pop):
  # for now, no sexual selection
  number_children = len(pop) * 2
  children = []
  for i in range(number_children):
    # note: there is a chance that both parents are the same individual
    children.append(mate_individuals(r.choice(pop), r.choice(pop)))
  return pop + children

def op_local_search (pop):
  for i in range(len(pop)):
    pop.append(local_search(pop[i]))
  return pop

def op_mutation (pop):
  for i in range(len(pop)):
    pop[i] = mutate_individual(pop[i])
  return pop

OPS = [op_selection, op_recombination, op_local_search, op_mutation, op_local_search]
# selection ->  halve population
# recombination -> triple population
# local_search -> double population
# mutation -> same population size
# local_search -> double population
# note: considering the large number of neighbors, small |new pop| may be better
def generate_new_population (pop):
  i = 0
  for op in OPS:
    S_par = clone_population(pop)
    S_desc = op(S_par)
    pop = S_desc
    i += 1

  return pop

def clone_population (pop):
  # deep copy each individual
  return [individual.clone() for individual in pop]

def update_population (pop, new_pop):
  # new_pop is large compared to pop_size, therefore we can select updates only
  #   from new_pop. alternative is to take select from pop U new_pop
  return sorted(new_pop, key=Fg, reverse=True)[:POP_SIZE]

ENTROPY = 0 # Shannon's entropy of these spells
def has_converged (pop):
  # calculating this entropy is costly, apply some filters first
  # Shannon's entropy for the lexicon of this population
  # compare it to the entropy of a random population
  return False

def restart_population (pop):
  # keep the most fit individual of the degenerate population, then fill the rest
  #   of the population with randos
  # note: don't want this fit individual to be an invasive species. possible solution:
  #   have lower selective pressure the first generation after a restart
  out = generate_new_population()
  out.pop()
  out.append(pop[0])
  return out


### The meat and potatoes ###
GENERATIONS = 1000
POP_SIZE = 100
def population_based_search ():
  pop = generate_initial_population(POP_SIZE)

  for i in range(GENERATIONS):
    print 'Generation', i
    new_pop = generate_new_population(pop)
    pop = update_population(pop, new_pop)

    if has_converged(pop):
      pop = restart_population(pop)
      # i = 0

    if i % 100 == 0:
      for individual in pop:
        individual.compile()

      out_pop = sorted(pop, key=lambda s: s.a+s.b+s.c, reverse=True)
      out_pop = [individual.json_data() for individual in out_pop]

      with open('out_' + str(i) + '.json', 'w') as file:
        file.write(json.dumps(out_pop, indent=2, ensure_ascii=False))

  return pop

pop = population_based_search()
for i in pop:
  i.compile()

pop = sorted(pop, key=lambda s: s.a+s.b+s.c, reverse=True)
pop = [individual.json_data() for individual in pop]

with open('out.json', 'w') as file:
  file.write(json.dumps(pop, indent=2, ensure_ascii=False))
