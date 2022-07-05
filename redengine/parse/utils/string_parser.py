
from functools import partial
import re

from typing import Callable, Dict, List, Union

from redengine.pybox.string.parse import ClosureParser
from redengine.pybox.container.visitor import Visitor

RESERVED_KEYWORDS = ("&", "|", "~")
CLOSURES = ('(', ')')

class InstructionParser:
    """Utility class for parsing a string to 
    a set of conditions.

    Parameters
    ----------
        item_parser : Callable
            function for identifying the parser for the item
        operators: List[Dict[str, Union[str, Callable]]])
            list of settings for the reserved keywords of the 
            operators that can be found in the expression
            ex:
                [{
                    "symbol": "&",
                    "func": _parse_all,
                    "side": "both",
                }]

    Reserved keywords:
        "&" : and operator
        "|" : or operator
        "~" : not operator
        "(" : opening closure
        ")" : closing closure
    
    These characters cannot be found in
    individual condition parsing (ie. 
    in the names of tasks).
    """
    def __init__(self, item_parser: Callable, operators: List[Dict[str,Union[str,Callable]]]):
        self.item_parser = item_parser
        self.operators = operators
        self.symbols = set([str(oper["symbol"]) for oper in operators])

        self.reserved_keywords = RESERVED_KEYWORDS
        self.closures = CLOSURES

    def __call__(self, string: str, **kwargs):
        """Parse a string to condition. Allows logical operators"""
        _closure_parser = ClosureParser()
        _visitor = Visitor(visit_types=(list,))

        # 1. Split closures
        items = _closure_parser.to_list(string)

        # 2. Split operations
        _visitor.assign_elements(items, self._split_operations)
        
        # 3. Remove extra tuples
        _visitor.apply(items, _flatten_tuples)
        
        # 4. Parse the elements with the item_parser and assemble
        _visitor.assign_elements(items, partial(self._parse, **kwargs))
        result = _visitor.reduce(items, self._assemble) 

        return result

    def _parse(self, __s:Union[tuple,str], **kwargs):
        """Applies the item_parser if the input is not a reserved keyword"""
        def parse_string(s):
            s = s.strip()
            if s in self.reserved_keywords:
                return s
            else:
                return self.item_parser(s, **kwargs)

        s = __s #TODO: do we need to copy the input?
        if isinstance(s, str):
            return parse_string(s)
        else:
            return tuple(parse_string(e) for e in s)

    def _assemble(self, *s:tuple):
        """Assembles together the elements in input"""
        _visitor = Visitor(visit_types=(list, tuple))
        s = _visitor.flatten(s)

        for operator in self.operators:
            s = self._assemble_oper(s, 
                        oper_str=operator["symbol"], 
                        oper_func=operator["func"], 
                        side=operator["side"])
        
        return s[0] if isinstance(s, tuple) else s

    def _assemble_oper(self, s:list, oper_str:str, oper_func:Callable, side="both"):
        """Assembles the operation element by applying the oper_func
        to the items in s and replacing their values with the 'obj' result
        """
        s = list(reversed(s))
        while self._contains_operator(s, oper_str):
            pos = self._get_index_from_list_item(s, [oper_str])

            if side == "both":
                # we have reversed the "s" so we'll put the result obj of the oper_func 
                # instead of lhs and rhs, at the same position
                obj = oper_func(s[pos+1], s[pos-1])
                s[pos] = obj

                del s[pos-1]
                 # -1 because we already removed one element thus position is misaligned
                del s[pos+1-1]
            elif side == "right":
                # delete the element in the left position
                obj = oper_func(s[pos-1])
                s[pos-1] = obj
                del s[pos]
            elif side == "left":
                # delete the element in the right position
                obj = oper_func(s[pos+1])
                s[pos+1] = obj
                del s[pos]

        return tuple(reversed(s))

    @staticmethod
    def _contains_operator(s:list, oper_str:str):
        for e in s:
            if isinstance(e, str) and e in (oper_str,):
                return True
        return False

    @staticmethod
    def _get_index_from_list_item(s:list, items:list):
        for i, e in enumerate(s):
            if isinstance(e, str) and e in items:
                return i
        raise KeyError

    def _split_operations(self, s:str):
        symbols = ''.join(self.symbols)
        regex = r'([' + symbols + '])'
        s = s.strip()
        if bool(re.search(regex, s)):
            l = re.split(regex, s)
            l = [elem for elem in l if elem.strip()]

            # if more than 1 element, return a tuple
            if len(l) == 1:
                return l[0]
            else:
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
