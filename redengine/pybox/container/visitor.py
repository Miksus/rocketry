
from collections.abc import Iterable

class Visitor:

    """A visitor class to visit elements of nested containers

    Example:
    --------
        v = Visitor(
            visit_types=(list, tuple)
        )
        # Apply a function to each element (return None)
        v.apply([[11, 12, 13], 2, [311, [321, 322, 323], 33], 3], print)

        # Flatten the container
        v.flatten([[11, 12, 13], 2, [311, [321, 322, 323], 33], 3])
        >>> [11, 12, 13, 2, 311, 321, 322, 323, 33, 3]
    """

    def __init__(self, use_attr=None, use_func=None,
                 visit_types=None, visit_func=None, visit_with_attr=None, visit_iterables=None,
                 iter_attr=None, iter_item=None, iter_func=None):
        
        # Iteration:
        #   iter([1, 2, 3])
        #   myobj.things
        #   my_generator([1,2,3])
        #   myobj["things"]

        # Iteration check
        #   
        self.use_attr = use_attr
        self.use_func = use_func
        self.iter_func = iter_func

        self.visit_funcs = []
        if visit_types is not None:
            self.visit_funcs.append(lambda cont: isinstance(cont, visit_types))
        if visit_func is not None:
            self.visit_funcs.append(visit_func)
        if visit_with_attr:
            self.visit_funcs.append(lambda cont: hasattr(cont, visit_with_attr))

    def flatten(self, cont):
        """Turn nested container to flat container
        
        Example:
        --------
            v = Visitor(visit_types=(list,))
            v.flatten([[1,2,3], 4, [5,6,7]])
            >>> [1,2,3,4,5,6,7]
        """
        if not self.is_visitable(cont):
            # End up here only if first level of recursion
            return [cont]

        tgtcont = []
        for key, subcont in self.iter(cont):

            if self.is_visitable(subcont):
                out = self.flatten(subcont)
            else:
                out = [subcont]
            tgtcont += out
        return tgtcont

    def assign_elements(self, cont, func):
        "Assign function to the elements of the container"
        # cont: [1, [21, 22, 23], 3]
        #   iter 0:
        #       cont[0] = func(1)
        #   iter 1:
        #       subcont = [21, 22, 23]
        #       ....    
        # cont: {"a": 1, "b": {"ba": 1, "bb": 2, "bc": 3}, "c": 2}
        #   iter 0:
        #       cont["a"] = func(1)
        #   iter 1:
        #       subcont = {"ba": 1, "bb": 2, "bc": 3}
        #       ....    
        if not self.is_visitable(cont):
            # End up here only if first level of recursion
            raise TypeError(f"Values of {cont} cannot be set anywhere. The object must be a visitable")

        for key, obj in self.iter(cont):
            if self.is_visitable(obj):
                self.assign_elements(obj, func)
            else:
                value = func(obj)
                self._assign_value(cont, key, value)

    def assign_last(self, cont, func):
        "Assign function to the last level containers (containers that do not have subcontainers)"
        # cont: [1, [21, 22, 23], 3]
        #   iter 1:
        #       cont[1] = func([21, 22, 23])
        #       ....    
        if not self.is_visitable(cont):
            # End up here only if first level of recursion
            raise TypeError(f"Values of {cont} cannot be set anywhere. The object must be a visitable")

        for key, obj in self.iter(cont):
            if self.is_visitable(obj) and self.has_sub_containers(obj):
                # obj = [..., [...], ...]
                self.assign_last(obj, func)
            elif self.is_visitable(obj) and not self.has_sub_containers(obj):
                # obj = [...]
                value = func(obj)
                self._assign_value(cont, key, value)
            else:
                # obj = 123
                pass
            
    def _assign_value(self, cont, key, value):
        # list: cont=[1, 2, 3], key=0, value=5
        #   cont[0] = 5
        # dict: cont=[1, 2, 3], key=0, value=5

        if self.use_attr:
            # cont = Namespace(myattr=[1,2,3]) (key=0, value=-1)
            getattr(cont, self.use_attr)[key] = value
        else:
            # cont = [1,2,3] (key=0, value=-1)
            # cont = {"a":1, "b":2} (key="a", value=-1)
            cont[key] = value

    def reduce(self, cont, func):
        args = []   
        for key, subobj in self.iter(cont):
            if not self.is_visitable(subobj):
                # subobj = 5
                args.append(subobj)
            elif self.has_sub_containers(subobj):
                # subobj = [1, [2, 3], 4]
                value = self.reduce(subobj, func)
                args.append(value)
            else:
                # # subobj = [1, 2, 3, 4]
                subargs = [val for key, val in self.iter(subobj)]
                value = func(*subargs)
                args.append(value)
        # Now should be inner
        # cont = [3, 3]
        return func(*args)

    def has_sub_containers(self, obj):
        if not self.is_visitable(obj):
            return False
        return any(
            self.is_visitable(subobj)
            for key, subobj in self.iter(obj)
        )


    def visit(self, container, func):
        "Apply a function to each element"
        if not self.is_visitable(container):
            return func(container)
        self._visit(container, func)
            
    def _visit(self, cont, func):
        for key, subcont in self.iter(cont):
            if self.is_visitable(subcont):
                # Container
                self._visit(subcont, func)
            else:
                # Actual element
                func(subcont)
            
    def apply(self, cont, func):
        "Apply a function to each container"
        func(cont)
        for key, subcont in self.iter(cont):
            if self.is_visitable(subcont):
                # Container
                self.apply(subcont, func)
            else:
                # Actual element
                pass

    def prune(self, cont, prune_loners=False):
        """Flatten sub containers that contain only 
        one another container thus unnecessary

        Examples:
        ---------
            v = Visitor(
                visit_types=(list, tuple)
            )
            l = [1, [[1]], [[1, 2]]]
            v.prune(l)
            l
            >>> [1, [1], [1, 2]]

            l = [1, [[1]], [[1, 2]]]
            v.prune(l, prune_loners=True)
            l
            >>> [1, 1, [1, 2]]
        
        Arguments:
        ----------
            prune_loners [bool] : Whether to prune lone elements (like [1, [2]] --> [1, 2])"""
        def is_prunable(obj):
            return (
                self.is_visitable(obj)
                and (True if prune_loners else self.has_sub_containers(obj))
                and len(obj) == 1
            )
        if not self.is_visitable(cont):
            # End up here only if first level of recursion
            return
            #raise TypeError(f"Values of {cont} cannot be set anywhere. The object must be a visitable")

        for key, obj in self.iter(cont):
            # Prune until there is no more unnecessary layers
            while is_prunable(obj):
                
                _, value = next(self.iter(obj))
                self._assign_value(cont, key, value)
                obj = value

            if self.is_visitable(obj):
                self.prune(obj, prune_loners=prune_loners)

    def iter(self, obj):
        # List:
        #   [1,2,3]
        #   1, 2, 3
        # Dict:
        #   {"a": 1, "b": 2, "c": 3}
        #   1, 2, 3

        cont = self._get_container(obj)

        if self.iter_func:
            return self.iter_func(cont)

        # Try to figure it out
        if isinstance(cont, dict):
            return cont.items()
        else:
            # Includes lists, tuples, sets etc
            return enumerate(cont)
            
    def _get_container(self, obj):
        if self.use_attr:
            return getattr(obj, self.use_attr)
        else:
            return obj

    def is_visitable(self, obj):
        if len(self.visit_funcs) == 0:
            cont = self._get_container(obj)
            return isinstance(cont, Iterable)
        return all(
            func(obj)
            for func in self.visit_funcs
        )
