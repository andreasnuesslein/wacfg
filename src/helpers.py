#!/usr/bin/env python

def uniq(seq):
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]

