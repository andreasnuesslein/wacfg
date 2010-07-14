
def OUT(str, verbosity=1):
    print(str)

def uniq(seq):
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]

