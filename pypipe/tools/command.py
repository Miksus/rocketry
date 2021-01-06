
from .statement import parse_statement

from pybox.string.parse import ClosureParser
from pybox.container.visitor import Visitor

from pypipe.core.conditions.base import All, Any, Not

import re

def parse_sentence(s:str):
    p = ClosureParser()
    v = Visitor(visit_types=(list,))

    # 1. Split closures
    l = p.to_list(s)

    # 2. Split operations
    v.assign_elements(l, split_operations)
    
    # 2a. Remove extra tuples
    v.apply(l, flatten_tuples)
    
    v.assign_elements(l, parse)
    
    e = v.reduce(l, assemble)
    return e

def split_operations(s):
    regex = r'([&|\-+~])'
    s = s.strip()
    if bool(re.search(regex, s)):
        l = re.split(regex, s)
        l = [elem for elem in l if elem]
        if len(l) == 1:
            # Has only the 
            return l[0]

        return tuple(l)
    else:
        return s

def flatten_tuples(cont):

    for i, item in enumerate(cont):
        if isinstance(item, tuple):
            cont.pop(i)
            for j, tpl_item in enumerate(item):
                cont.insert(i+j, tpl_item)
    
    return cont

def parse(s:tuple):
    def parse_string(s):
        try:
            return parse_statement(s)
        except ValueError:
            return s.strip()

    if isinstance(s, str):
        return parse_string(s)
    else:
        return tuple(parse_string(e) for e in s)

def assemble(*s:tuple):
    def assemble_not(s:tuple):
        def contains_not(s):
            for e in s:
                if isinstance(e, str) and e in ("~",):
                    return True
            return False
        
        res = []
        s = list(reversed(s))
        while contains_not(s):
            pos = _index(s, ["~"])
            s[pos-1] = not_(s[pos-1])
            del s[pos]
        return tuple(reversed(s))

    def assemble_comparison(s:tuple):
        
        def contains_comparison(s):
            for e in s:
                if isinstance(e, str) and e in ("&", "|"):
                    return True
            return False

        res = []
        s = list(s)
        while contains_comparison(s):
            pos = _index(s, ["&", "|"])
            oper = {"|": any_, "&": all_}[s[pos]]
            s[pos] = oper(s[pos-1], s[pos+1])
            del s[pos-1]
            del s[pos+1-1]
        return tuple(reversed(s))

    def _flatten(*args, types, with_attr):
        comps = []
        for arg in args:
            if isinstance(arg, types):
                comps += getattr(arg, with_attr)
            else:
                comps.append(arg)
        return comps

    def all_(*args):
        comps = _flatten(*args, types=All, with_attr="subconditions")
        return All(*comps)

    def any_(*args):
        comps = _flatten(*args, types=Any, with_attr="subconditions")
        return Any(*comps)

    def not_(arg):
        if hasattr(arg, "__invert__"):
            return ~arg
        elif isinstance(arg, Not):
            return ~arg
        else:
            return Not(arg)

    def _index(s:list, items:list):
        "Get "
        for i, e in enumerate(s):
            if isinstance(e, str) and e in items:
                return i
        raise KeyError

    v = Visitor(visit_types=(list, tuple))
    s = v.flatten(s)

    s = assemble_not(s)
    s = assemble_comparison(s)

    return s[0] if isinstance(s, tuple) else s