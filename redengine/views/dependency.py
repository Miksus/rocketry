
from typing import TYPE_CHECKING, DefaultDict, Optional, Union
from redengine._base import RedBase
from redengine.conditions import Any, All, DependFinish, DependSuccess
from redengine.conditions.task import DependFailure
from redengine.core import Task
from redengine.core.condition.base import BaseCondition
from .base import register_view

if TYPE_CHECKING:
    from redengine import Session

class Link:

    def __init__(self, 
                 parent:Task, 
                 child:Task, 
                 relation:Union[DependSuccess, DependFailure, DependFinish]=None, 
                 type:Optional[Union[Any, All]]=None):
        self.parent = parent 
        self.child = child
        self.relation = relation
        self.type = type

    def __iter__(self):
        return iter((self.parent, self.child))

    def __eq__(self, other):
        if type(self) == type(other):
            return (
                self.parent == other.parent
                and self.child == other.child
                and self.relation == other.relation
                and self.type == other.type
            )
        else:
            return False

    def __str__(self):
        s = f'{self.parent.name!r} -> {self.child.name!r}'
        if self.type is All:
            s = s + ' (multi)'
        return s

    def to_dict(self):
        return {
            'parent': self.parent,
            'child': self.child,
            'relation': self.relation,
            'type': self.type
        }

    def __getitem__(self, item:str):
        return self.to_dict()[item]

@register_view('dependencies')
class Depenency:
    """View for task dependencies

    Examples
    --------

    Plot dependencies (requires NetworkX and Matplotlib)
    .. code-block:: python

        import matplotlib.pyplot as plt
        from redengine import session
        session.dependencies.to_networkx()
        plt.show()
    """
    def __init__(self, s:'Session'):
        self.session = s

    def to_dict(self):
        "Put dependencies to list of dicts"
        return list(link.to_dict() for link in self)

    def to_networkx(self, graph=None, edge_kwds=None):
        """Draw NetworkX graph from dependencies

        Note that this method requires installing
        `networkx <https://networkx.org/documentation/stable/index.html>`_.

        Parameters
        ----------
        graph : networkx.Graph, optional
            NetworkX graph, by default created

        Returns
        -------
        networkx.Graph
            Graph object
        """
        edge_kwds = {} if edge_kwds is None else edge_kwds
        if graph is None:
            import networkx as nx
            graph = nx.DiGraph()
        graph.add_nodes_from(list(self.session.tasks.keys()))

        edges = DefaultDict(lambda: DefaultDict(lambda: []))
        for link in self:
            edge = (link.parent.name, link.child.name)

            relation = link.relation if link.relation in (DependFailure, DependSuccess) else 'other'
            type_ = All if link.type not in (All, Any) else link.type
            edges[relation][type_].append(edge)

        pos = nx.spring_layout(graph)
        nx.draw_networkx_nodes(graph, pos, node_color="w", node_shape="s")
        nx.draw_networkx_labels(graph, pos, bbox=dict(boxstyle="square,pad=0.3", edgecolor="k", facecolor="w"))

        # Draw edges or links
        kwds = {'arrowsize': 30, 'arrows': True}
        kwds.update(edge_kwds)
        nx.draw_networkx_edges(graph, pos, edgelist=edges[DependSuccess][All], style='solid', edge_color='g', **kwds)
        nx.draw_networkx_edges(graph, pos, edgelist=edges[DependSuccess][Any], style='dashed', edge_color='g', **kwds)

        nx.draw_networkx_edges(graph, pos, edgelist=edges[DependFailure][All], style='solid', edge_color='r', **kwds)
        nx.draw_networkx_edges(graph, pos, edgelist=edges[DependFailure][Any], style='dashed', edge_color='r', **kwds)

        nx.draw_networkx_edges(graph, pos, edgelist=edges['other'][Any], style='solid', edge_color='k', **kwds)
        nx.draw_networkx_edges(graph, pos, edgelist=edges['other'][Any], style='dashed', edge_color='k', **kwds)

        return graph

    def __iter__(self):
        for task in self.session.tasks.values():
            yield from self._get_links(task)

    def _get_links(self, task:Task) -> Union[Any, All]:
        cond = task.start_cond
        if isinstance(cond, (Any, All)):
            for subcond in cond:
                if isinstance(subcond, (DependFinish, DependSuccess, DependFailure)):
                    req_task = subcond.kwargs['depend_task']
                    req_task = self.session.get_task(req_task)
                    yield Link(req_task, task, relation=type(subcond), type=type(cond))
        elif isinstance(cond, (DependFinish, DependSuccess, DependFailure)):
            req_task = cond.kwargs['depend_task']
            req_task = self.session.get_task(req_task)
            yield Link(req_task, task, relation=type(cond))

    def __str__(self):
        return '\n'.join(map(lambda x: str(x), self))