#import json

# wrap prints so debugging messages can be turned off easily
def log (msg):
  #print msg
  return msg

by_word = {}
by_num = []

all_types = []
all_subsystems = []

# data
class Token:
  def __init__(self, n, word, glyph, abc, effect, subsystem, type):
    self.id = n
    self.word = word.strip()
    self.glyph = glyph.strip()
    self.abc = abc.strip()
    self.effect = effect.strip()
    self.subsystem = subsystem.strip()
    self.type = type.strip()

  def json_data(self):
    a = 0
    b = 0
    c = 0

    try:
      a, b, c = [int(n[:-1]) for n in self.abc.split(' ')]
    except:
      pass

    obj = {
      'word': self.word,
      'glyph': self.glyph,
      'effect': self.effect,
      'subsystem': self.subsystem,
      'type': self.type,
      'range': a,
      'cooldown': b,
      'level': c
    }

    return obj

class Spell:
  def __init__(self):
    self.td_symbols = []
    self.c_symbols = []

    self.compiled = ''

    self.compilation_errors = 0

    self.school = ''
    self.description = ''
    self.shape = ''

    self.a = 2 # range = 5(a+1) feet
    self.b = 2 # cooldown in turns
    self.c = 2 # level: put it in a function depending on the effect

    self.toggles = []

  def clone (self):
    s = Spell()
    s.td_symbols = [td for td in self.td_symbols]
    s.c_symbols = [c for c in self.c_symbols]
    return s

  def json_data (self, words=None):
    if len(self.compiled) == 0:
      self.compile(words)
    if words is None:
      words = self.words()
    return {
      'words': words,
      'glyphs': self.glyphs(words),
      'abc': '%d,%d,%d' % (self.a, self.b, self.c),
      'toggles': ', '.join(self.toggles),
      'shape': self.shape,
      'compiled': self.compiled
    }

  def add_symbol (self, location, symbol):
    if location == 'target declaration':
      self.td_symbols.append(symbol)
    elif location == 'code':
      self.c_symbols.append(symbol)

    self.compiled = ''

  def remove_symbol (self, location, index):
    if location == 'target declaration':
      del self.td_symbols[index]
    elif location == 'code':
      del self.c_symbols[index]

  def change_symbol (self, location, index, to):
    if location == 'target declaration':
      self.td_symbols[index] = to
    elif location == 'code':
      self.c_symbols[index] = to

  def words (self):
    target_declaration = ' '.join(self.td_symbols)
    code = ' '.join(self.c_symbols)
    return target_declaration + ' niz ' + code

  def glyphs (self, words=None):
    if words is None:
      words = self.words().split(' ')
    out = ''
    for word in words:
      out += by_word[word].glyph + ' '
    return out[:-1]

  # Actual compiler
  def compile(self, words=None):
    if words is None:
      words = self.words().split(' ')

    self.compiled = ''

    compilation_errors = 0

    delay_next = None # 'negative', 'positive'
    delay_countdown = -1
    delayed_abc = None
    delayed_toggle = None

    loop_countdown = -1
    loop_marker = 0

    skips = []

    i = -1
    while i <= len(words)-2:
      i += 1

      if i in skips:
        log('skipping ' + str(i))
        continue

      token = by_word[words[i]]

      # delays!
      delay_countdown -= 1
      if delay_countdown == 0:
        log('applying delayed effects')
        i += 1
        token = {
          'type': None,
          'abc': delayed_abc,
          'effect': delayed_toggle
        }

        delayed_abc = None
        delayed_toggle = None
        delay_next = None

      # is it a loop
      if token.type is 'loops':
        if loop_countdown > 0:
          compilation_errors += 1
        else:
          skips.append(i)

          # loop what follows
          if effect[0] is '[':
            loop_marker = i
            loop_countdown = int(effect[1])
            if loop_countdown == 0:
              loop_countdown = len(words) - i

            log ('starting loop ' + effect[0] + ' from ' + str(loop_marker) + ' to ' + str(loop_countdown))
          # loop what's before
          elif effect[0] is ']':
            n = int(effect[1])
            if n == 0:
              i = 0
            else:
              i -= n

            log('starting loop ' + effect[0] + ' from ' + str(i))

      # is it a delay
      elif token.type is 'delays':
        if delay_countdown > 0:
          compilation_errors += 1
        else:
          delay_countdown = int(effect[1])

          if effect[0] is '/':
            delay_next = 'positive'
          elif effect[0] is '|':
            delay_next = 'negative'

          log('delaying ' + effect[0] + ' for ' + delay_countdown + ' steps')

      # run abc effects
      # split abc into positive and negative
      if not token.abc in ['none', None]:
        abc = token.abc.split(' ')
        positive_abc = {'a': 0, 'b': 0, 'c': 0}
        negative_abc = {'a': 0, 'b': 0, 'c': 0}

        for resource in abc:
          key = resource[2]
          amt = int(resource[1])

          if resource[0] == '^':
            if getattr(self, key) > 0:
              negative_abc[key] = 2*getattr(self, key)
            elif getattr(self, key) < 0:
              positive_abc[key] = -2*getattr(self, key)
          elif resource[0] is '+':
            positive_abc[key] += amt
          elif resource[0] is '-':
            negative_abc[key] += amt

        if delay_next is 'positive':
          delayed_abc = positive_abc
          positive_abc = {'a': 0, 'b': 0, 'c': 0}
        elif delay_next is 'negative':
          delayed_abc = negative_abc
          negative_abc = {'a': 0, 'b': 0, 'c': 0}

        if delay_next is not None:
          delay_next = None
          log('delaying ' + delay_next)

        for key in 'abc':
          setattr(self, key, getattr(self, key) + positive_abc[key] - negative_abc[key])

        log('positive abc: ' + str(positive_abc['a']) + ',' + str(positive_abc['b']) + ',' + str(positive_abc['c']))
        log('negative abc: ' + str(negative_abc['a']) + ',' + str(negative_abc['b']) + ',' + str(negative_abc['c']))
        log('current abc: ' + str(self.a) + ',' + str(self.b) + ',' + str(self.c))

      if not token.effect in ['none', '', None]:
        log('applying effect ' + token.effect)
        type = token.effect[0]
        effect = token.effect[1:]
        # do toggles
        if type == '&':
          if effect in self.toggles:
            if delay_next is 'positive':
              delayed_toggle = token.effect
            else:
              self.toggles.remove(effect)
          elif not effect in self.toggles:
            if delay_next is 'negative':
              delayed_toggle = token.effect
            else:
              self.toggles.append(effect)
        elif type == '~':
          # ~fx is the only option right now
          if delay_next is 'negative':
            delayed_toggle = token.effect
          else:
            self.toggles = []
        elif type == '#':
          if self.shape:
            self.compiled += effect
          else:
            self.shape = effect
        else:
          if len(self.compiled) > 0:
            self.compiled += '\n'
          self.compiled += token.effect #effect is just token

      # update system classification
      # if self.a < 0:
      #   compilation_errors += 1
      # if self.b < 0:
      #   compilation_errors += 1
      # if self.c < 0:
      #   compilation_errors += 1

      # loops!
      loop_countdown -= 1
      if loop_countdown is 0:
        log('loop resetting to ' + str(loop_marker))
        loop_countdown = -1
        i = loop_marker
        continue

    if delay_next is not None:
      compilation_errors += 1

    if loop_countdown > 0:
      compilation_errors += 1

    if delay_countdown > 0:
      compilation_errors += 1

    self.compilation_errors = compilation_errors


# Read manifest

fname = 'vocab.csv'
line_num = 0
with open(fname, 'r') as file:
  for line in file:
    word, glyph, abc, effect, subsystem, type = line.split(',')
    if not type in all_types:
      all_types.append(type)
    if not subsystem in all_subsystems:
      all_subsystems.append(subsystem)
    print(glyph, end=" ")
    token = Token(line_num, word, glyph, abc, effect, subsystem, type)
    by_word[word] = token
    by_num.append(Token)
  print()

#obj = {}
#for k, v in by_word.items():
#  obj[k] = v.json_data()
#
#with open('tokens.json', 'w') as file:
#  file.write(json.dumps(obj, indent=2, ensure_ascii=False))
