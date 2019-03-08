import random as r

from spell import *

def filter_dict (d, fn):
  return {k: v for k, v in d.iteritems() if fn(v)}

def random_entry (d):
  keys = d.keys()
  if len(keys) == 0:
    return ''
  k = r.choice(keys)
  return d[k]

def random_filter (d, fn):
  new_d = filter_dict(d, fn)
  token = random_entry(new_d)
  if not token:
    return token
  else:
    return token.word

# symbol: group of tokens such that there is at least one token in the group that,
#         when removed from the group, makes the group as a whole impossible to parse
def random_symbol (type=None, favor_evocation=False):
  if type is None:
    if not favor_evocation:
      return random_entry(_symbol_generators)()
    else:
      if r.randrange(100) < 20:
        return random_entry(_symbol_generators)()
      else:
        return rs_base()
  else:
    return _symbol_generators[type]()

# in the code section
def qualify_symbol (word_str):
  if r.randrange(100) < 20:
    return word_str
  else:
    modifier = random_filter(by_word, lambda t: t.type == 'modifiers')
    return modifier + ' ' + word_str

def rs_delay ():
  # delay.[negater,base stats].([negater, base stats])
  out = random_filter(by_word, lambda t: t.type == 'delays')
  out += ' ' + random_filter(by_word, lambda t: t.type in ['negater', 'base stats'])
  out += ' ' + random_filter(by_word, lambda t: t.type in ['negater', 'base stats'])
  return out

def rs_skills ():
  # (modifier).effects.[skills,stats,senses]
  out = random_filter(by_word, lambda t: t.type == 'effects')
  out += ' ' + random_filter(by_word, lambda t: t.type in ['skills', 'stats', 'senses'])
  return qualify_symbol(out)

def rs_interaction ():
  # (interactions.(spellbinding/shapes)).material.(<object>)
  out = random_filter(by_word, lambda t: t.type == 'interactions')
  if r.randrange(100) < 10:
    out += ' ' + random_filter(by_word, lambda t: t.type == 'shapes_spellbinding')

  if r.randrange(100) < 50:
    out += ' ' + random_filter(by_word, lambda t: t.type == 'object elements')
  else:
    out += ' ' + random_filter(by_word, lambda t: t.type == 'material')

  return qualify_symbol(out)

def rs_element ():
  return random_filter(by_word, lambda t: t.type == 'object elements')

def rs_misc ():
  # <object>.misc.code.[criteria,special criteria.*]
  front = rs_object()
  front += random_filter(by_word, lambda t: t.type == 'misc')

  back = ''
  if r.randrange(100) < 12:
    back = random_filter(by_word, lambda t: t.type == 'criteria')
  else:
    back = random_filter(by_word, lambda t: t.type == 'special criteria')
    magic_words = random_entry(by_word).word
    back += ' ' + magic_words

  return (front, back)

def rs_object ():
  #mode.slots.morphology.style.(enchantments)
  mode = random_filter(by_word, lambda t: t.type == 'modes')

  out = mode
  out += ' ' + random_filter(by_word, lambda t: t.type == 'slots_'+by_word[mode].effect)

  if mode == 'weapon':
    out += ' ' + random_filter(by_word, lambda t: t.type == 'morphology')
    if r.randrange(100) < 80:
      out += ' ' + random_filter(by_word, lambda t: t.type == 'enchantments_weapon')

    # TODO: armor enchantments e.g. resist X
    if mode ==  'armor' and r.randrange(100) < 75:
      fx = random_filter(by_word, lambda t: t.type == 'enchantments_armor')

      if type == 'glammered':
        pass
      elif type == 'nimble':
        out += qualify_symbol(fx)
      elif type == 'resist':
        fx += ' ' + random_filter(by_word, lambda t: t.type in ['species', 'object elements', 'material'])
        out += qualify_symbol(fx)

  if mode in ['weapon', 'armor']:
    out += ' ' + random_filter(by_word, lambda t: t.type == 'styles')

  return out

def rs_base ():
  return random_filter(by_word, lambda t: t.type == 'base stats')

def rs_negator ():
  return random_filter(by_word, lambda t: t.type == 'negaters')

def rs_loop ():
  return random_filter(by_word, lambda t: t.type == 'loops')

def rs_effect ():
  return random_filter(by_word, lambda t: t.type in ['evocation effects', 'illusion effects', 'restitution_effects'])

def rs_material ():
  out = random_filter(by_word, lambda t: t.type == 'material')
  out += ' ' + random_filter(by_word, lambda t: t.type == 'shapes_spellbinding')
  return out

# in the target declaration
def rs_attunement ():
  out = random_filter(by_word, lambda t: t.type == 'attunements')
  if r.randrange(100) < 50:
    out += ' ' + random_filter(by_word, lambda t: t.type == 'species')
  else:
    out += ' ' + random_filter(by_word, lambda t: t.type == 'material')

  return out

def rs_shape ():
  return random_filter(by_word, lambda t: t.type == 'shapes')

_symbol_generators = {
  'delay': rs_delay,
  # 'skills': rs_skills,
  # 'interaction': rs_interaction,
  # 'element': rs_element,
  #'spellbound': rs_misc,
  # 'object': rs_object,
  'base': rs_base,
  'negator': rs_negator,
  'loop': rs_loop,
  'effect': rs_effect,
  # 'material': rs_material
}
