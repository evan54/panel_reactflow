from pprint import pprint

from pathlib import Path
import uuid

import pandas as pd

import panel as pn
import param
import panel.custom
import panel.viewable
import panel.reactive

pn.extension(
    "tabulator",
    css_files=[
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css"],
)


class ReactFlowComponent(pn.custom.ReactComponent):
    """A Panel component that renders a simple React Flow diagram."""

    nodes = param.List(default=[], doc="ReactFlow nodes")
    edges = param.List(default=[], doc="ReactFlow edges")

    default_edge_options = param.Dict(
        doc="https://reactflow.dev/api-reference/types/default-edge-options")

    _importmap = {"imports": {"@xyflow/react": "https://esm.sh/@xyflow/react"}}
    _esm = Path(__file__).parent / "reactflow.js"
    _stylesheets = [
        "https://cdn.jsdelivr.net/npm/@xyflow/react/dist/style.css"]


class Node(param.Parameterized):

    id_ = param.String()
    xy = param.XYCoordinates()
    name = param.String()
    selected = param.Boolean(default=False)
    react_props = param.Dict(default={})

    tabular_params = ["id", "x", "y", "name"]

    def __init__(self, **params):
        super().__init__(**params)

    def to_reactflow(self):
        return {
            "id": self.id_,
            "position": {"x": self.xy[0], "y": self.xy[1]},
            "data": {"label": self.name},
            "selected": self.selected,
            **self.react_props,
        }

    @classmethod
    def from_reactflow(cls, kwargs):
        """ Extract the position and whether it's selected """
        pos = kwargs.pop("position")
        return {"id": kwargs["id"],
                "xy": (pos["x"], pos["y"]),
                "selected": kwargs.pop("selected", False)}

    def to_tabular(self):
        return {
            "id": self.id_,
            "x": self.xy[0],
            "y": self.xy[1],
            "name": self.name,
        }


class Edge(param.Parameterized):

    source = param.ClassSelector(class_=Node)
    target = param.ClassSelector(class_=Node)
    selected = param.Boolean(default=False)
    react_props = param.Dict(default={})
    weight = param.Number(bounds=(0., 1.), default=None)

    tabular_params = ["source_id", "target_id", "source_name", "target_name",]

    def __init__(self, **params):
        super().__init__(**params)
        self.id_ = f"Edge{self.source.id_}_{self.target.id_}"

    def to_reactflow(self):
        return {
            "id": f"{self.source.id_} -> {self.target.id_}",
            "source": self.source.id_,
            "target": self.target.id_,
            "label": None if self.weight is None else f"{self.weight:.2%}",
            "selected": self.selected,
            **self.react_props,
        }

    @classmethod
    def from_reactflow(cls, d_nodes, kwargs, react_props=None):
        """ Return edge instance """
        if react_props is None:
            react_props = {}
        weight = kwargs.get("label", None)
        if weight is not None and weight[-1] == "%":
            weight = float(weight[:-1]) / 100.
        return cls(
            source=d_nodes[kwargs.pop("source")],
            target=d_nodes[kwargs.pop("target")],
            weight=weight,
            selected=kwargs.pop("selected", False),
            react_props=react_props,
        )

    def to_tabular(self):
        return {
            "source_id": self.source.id_,
            "target_id": self.target.id_,
            "source_name": self.source.name,
            "target_name": self.target.name,
            "weight": self.weight,
        }


class ReactFlowEditor(pn.custom.PyComponent):
    """
    """
    # TODO
    # * finish edge management
    # * add edge
    # * delete edge
    # * modify edge
    # * select edge

    nodes = param.List(default=[])
    edges = param.List(default=[])

    def __init__(self, **params):
        self.reactflow_params = params.pop("reactflow_params", {})
        self.new_node_react_props = params.pop("new_node_react_props", {})
        self.new_edge_react_props = params.pop("new_edge_react_props", {})
        super().__init__(**params)

        # Initialise widgets
        self._reactflow = self._init_reactflow()
        self._nodes_tabulator = self._init_nodes_tabulator()
        self._edges_tabulator = self._init_edge_tabulator()
        self._add_node_name = pn.widgets.TextInput(name="Name")
        self._add_node_button = pn.widgets.Button(name="Submit")

        # initialise watchers
        self._updating = {"nodes": False, "edges": False}
        self._init_watchers()

        # initalise layout
        self._layout = self._create_layout()

    ###########################################################################
    ## initialisation functions
    ###########################################################################
    def _init_reactflow(self):
        return ReactFlowComponent(
            nodes=[n.to_reactflow() for n in self.nodes],
            edges=[e.to_reactflow() for e in self.edges],
            **self.reactflow_params
        )

    def _init_nodes_tabulator(self):
        df, selected = self._nodes_to_df()
        return pn.widgets.Tabulator(
            value=df,
            show_index=False,
            layout="fit_data",
            editors={"name": "input"},
            buttons={'delete': '<i class="fa fa-trash"></i>'},
            selectable="checkbox",
            selection=selected,
            height=250,
            theme="simple",
        )

    def _init_edge_tabulator(self):
        df, selected = self._edges_to_df()
        return pn.widgets.Tabulator(
            value=df,
            show_index=False,
            layout="fit_data",
            editors={"weight": "input"},
            buttons={'delete': '<i class="fa fa-trash"></i>'},
            selectable="checkbox",
            selection=selected,
            height=250,
            theme="simple",
        )

    ###########################################################################
    ## Helper functions
    ###########################################################################
    def _nodes_to_df(self):
        if not self.nodes:
            return pd.DataFrame(columns=Node.tabular_params), []
        df = pd.DataFrame([n.to_tabular() for n in self.nodes])
        selected = [i for i, n in enumerate(self.nodes) if n.selected]
        return df, selected

    def _edges_to_df(self):
        if not self.edges:
            return pd.DataFrame(columns=Edge.tabular_params), []
        df = pd.DataFrame([e.to_tabular() for e in self.edges])
        selected = [i for i, e in enumerate(self.edges) if e.selected]
        return df, selected

    ###########################################################################
    ## WATCHERS
    ###########################################################################

    def _init_watchers(self):
        """ Setup all the watchers """
        # global watcher to update UI based on state
        self.param.watch(self._update_ui, ["nodes", "edges"])

        # update state based on reactflow
        self._reactflow.param.watch(self._update_from_reactflow, 
                                    ["nodes", "edges"])

        # update state based on node tabulator
        self._nodes_tabulator.on_edit(self._update_nodes_from_tabulator_edit)
        self._nodes_tabulator.param.watch(
            self._update_selection_from_tabulator("nodes"), "selection")
        self._nodes_tabulator.on_click(self._handle_tabulator_delete("nodes"))


        # update state based on edge tabulator
        self._edges_tabulator.on_click(self._handle_tabulator_delete("edges"))
        self._edges_tabulator.on_edit(self._update_edges_from_tabulator_edit)
        self._edges_tabulator.param.watch(
            self._update_selection_from_tabulator("edges"), "selection")

        # update state when clicking a button
        self._add_node_button.on_click(self._add_node)

    ###########################################################################
    ## GENERIC WATCHERS
    def _update_ui(self, event):
        """
        Updates both ReactFlow and Tabulator when the main 'nodes' list 
        changes.
        """
        field = event.name
        setattr(self._reactflow, field, [
            e.to_reactflow() for e in getattr(self, field)])
        df, selected = getattr(self, f"_{field}_to_df")()
        tabulator = getattr(self, f"_{field}_tabulator")
        tabulator.value = df
        if tabulator.selection != selected:
            tabulator.selection = selected

    def _update_from_reactflow(self, *events):
        """
        Updates the master 'nodes' list when nodes are changed in ReactFlow 
        (drag/select).
        """
        for event in events:
            field = event.name
            if not self._updating[field]:
                self._updating[field] = True
                try:
                    d_nodes = {n.id_: n for n in self.nodes}
                    if field == "edges":
                        self.edges = [
                            Edge.from_reactflow(
                                d_nodes, e, self.new_edge_react_props)
                            for e in event.new
                        ]
                    elif field == "nodes":
                        n_new = len(event.new)
                        n_nodes = len(self.nodes)
                        if n_new != n_nodes:
                            raise ValueError("reactflow event returned diff"
                                             f"number of nodes ({n_new}) vs"
                                             f" state ({n_nodes})")
                        new_nodes = []
                        for n in event.new:
                            id_, xy, selected = Node.from_reactflow(n).values()
                            node_to_modify = d_nodes[id_]
                            node_to_modify.xy = xy
                            node_to_modify.selected = selected
                            new_nodes.append(node_to_modify)
                        self.nodes = new_nodes
                finally:
                    self._updating[field] = False

    def _update_selection_from_tabulator(self, field):
        """Updates node selection state when rows are selected in Tabulator."""
        def fun(event):
            if self._updating[field]:
                return
            try:
                selected_indices = set(event.new)
                for i, entry in enumerate(getattr(self, field)):
                    entry.selected = i in selected_indices
                setattr(self, field, getattr(self, field))
            finally:
                self._updating[field] = False
        return fun

    def _handle_tabulator_delete(self, field):
        def fun(event):
            if event.column == "delete":
                field_values = getattr(self, field)
                setattr(self, field,
                        field_values[:event.row] + field_values[event.row+1:])
                if field == "nodes":
                    field_value = field_values[event.row]
                    self.edges = [
                        e for e in self.edges
                        if field_value.id_ not in [e.target.id_, e.source.id_]
                    ]
        return fun

    ###########################################################################
    ## NODE WATCHERS
    def _update_nodes_from_tabulator_edit(self, event):
        """ Update nodes based on name updating of a node """
        if self._updating["nodes"]:
            return
        self._updating["nodes"] = True
        try:
            node_to_update = self.nodes[event.row]
            if event.column == "name":
                node_to_update.name = event.value
                self.nodes = self.nodes[:] # Trigger update
        finally:
            self._updating["nodes"] = False

    def _add_node(self, event):
        new_node = Node(
            id_=str(uuid.uuid4()),
            name=self._add_node_name.value,
            xy = (0, 0),
            selected = False,
            react_props=self.new_node_react_props,
        )
        self.nodes = self.nodes + [new_node]

    ###########################################################################
    ## EDGE WATCHERS
    def _update_edges_from_tabulator_edit(self, event):
        """ Update edges based on weight updating of a edge """
        if self._updating["edges"]:
            return
        self._updating["edges"] = True
        try:
            edge_to_update = self.edges[event.row]
            if event.column == "weight":
                edge_to_update.weight = event.value
                self.edges = self.edges
        finally:
            self._updating["edges"] = False

    ###########################################################################
    ## LAYOUT
    ###########################################################################
    def _create_layout(self):
        """Creates the component's visible layout."""
        controls = pn.Card(
            pn.Row(self._add_node_name, self._add_node_button),
            title="<i class='fa-solid fa-plus'></i> Add Node",
            sizing_mode="stretch_width"
        )

        sidebar = pn.Column(
            pn.pane.Markdown("### Nodes"),
            self._nodes_tabulator,
            self._edges_tabulator,
            controls,
            width=650
        )
        canvas = pn.Column(
            pn.pane.Markdown("### Canvas"),
            self._reactflow,
            sizing_mode="stretch_both",
        )
        return pn.Row(sidebar, canvas, sizing_mode="stretch_both", 
                      min_height=600)

    def __panel__(self):
        return self._layout
