
from .statement import parse_statement

from pybox.string.parse import ClosureParser
from pybox.container.visitor import Visitor

from pypipe.core.conditions.base import All, Any, Not

import re

def parse_condition(s:str):
    p = ClosureParser()
    v = Visitor(visit_types=(list,))

    # 1. Split closures
    l = p.to_list(s)

    # 2. Split operations
    v.assign_elements(l, _split_operations)
    
    # 2a. Remove extra tuples
    v.apply(l, _flatten_tuples)
    
    v.assign_elements(l, _parse)
    
    e = v.reduce(l, _assemble) 
    return e

def _split_operations(s):
    regex = r'([&|\-+~])'
    s = s.strip()
    if bool(re.search(regex, s)):
        l = re.split(regex, s)
        l = [elem for elem in l if elem.strip()]
        if len(l) == 1:
            # Has only the 
            return l[0]

        return tuple(l)
    else:
        return s

def _flatten_tuples(cont):

    for i, item in enumerate(cont):
        if isinstance(item, tuple):
            cont.pop(i)
            for j, tpl_item in enumerate(item):
                cont.insert(i+j, tpl_item)
    
    return cont

def _parse(s:tuple):
    def parse_string(s):
        try:
            return parse_statement(s)
        except ValueError:
            s = s.strip()
            if s not in ("&", "|", "~"):
                raise ValueError(f"Invalid token: '{s}'")
            return s

    if isinstance(s, str):
        return parse_string(s)
    else:
        return tuple(parse_string(e) for e in s)

def _assemble(*s:tuple):
    def assemble_not(s:tuple):
        def contains_not(s):
            for e in s:
                if isinstance(e, str) and e in ("~",):
                    return True
            return False
        
        s = list(reversed(s))
        while contains_not(s):
            pos = _index(s, ["~"])
            s[pos-1] = not_(s[pos-1])
            del s[pos]
        return tuple(reversed(s))

    def assemble_and(s):
        def contains_and(s):
            for e in s:
                if isinstance(e, str) and e in ("&",):
                    return True
            return False

        s = list(reversed(s))
        while contains_and(s):
            pos = _index(s, ["&"])

            # Set the comparison object to "&" in the list
            s[pos] = all_(s[pos+1], s[pos-1])
            # NOTE: We have reversed the "s" thus we also put the arguments to 

            # Remove lhs and rhs of the comparison as they are embedded in comparison object
            del s[pos-1]
            del s[pos+1-1] # We -1 because we already removed one element thus pos is misaligned
            
        return tuple(reversed(s))

    def assemble_or(s):
        def contains_or(s):
            for e in s:
                if isinstance(e, str) and e in ("|",):
                    return True
            return False
        
        s = list(reversed(s))
        while contains_or(s):
            pos = _index(s, ["|"])

            # Set the comparison object to "|" in the list
            s[pos] = any_(s[pos+1], s[pos-1])
            # NOTE: We have reversed the "s" thus we also put the arguments to 

            # Remove lhs and rhs of the comparison as they are embedded in comparison object
            del s[pos-1]
            del s[pos+1-1] # We -1 because we already removed one element thus pos is misaligned

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
    s = assemble_and(s)
    s = assemble_or(s)
    
    # TODO: Clean this mess (but be careful)
    # TODO: Unify and modularize compare_... functions
    #   A class "Assembler"?
    #       Methods
    #           assemble(tupl)
    #               Turns tuple into assembled tuple (calls seek and build)
    #           seek(tupl)
    #               Find next occurence of the operation in the tuple
    #           build(lhs, rhs) (lhs=left hand side, rhs=right hand side)
    #               - lhs=None for Not

    return s[0] if isinstance(s, tuple) else s