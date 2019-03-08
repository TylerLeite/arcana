import json

data = json.loads(file)

def comparator (x):
  abc = x['abc'].split(',')
  abc = [int(n) for n in abc]
  return sum(abc)

data = sorted(data, key=comparator)
with open('out_sort.json', 'w') as file:
  file.write(json.dumps(data, indent=2))
