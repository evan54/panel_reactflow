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
    label = param.String()
    xy = param.XYCoordinates()
    selected = param.Boolean(default=False)
    react_props = param.Dict(default={})
    name = param.String()

    tabular_params = ["id", "x", "y", "label"]

    def __init__(self, **params):
        super().__init__(**params)
        self.name = f"Node{self.id_}"

    def to_reactflow(self):
        return {
            "id": self.id_,
            "position": {"x": self.xy[0], "y": self.xy[1]},
            "data": {"label": self.label},
            "selected": self.selected,
            **self.react_props,
        }

    @classmethod
    def from_reactflow(cls, kwargs):
        pos = kwargs.pop("position")
        return cls(
            id_=kwargs.pop("id"),
            label=kwargs.pop("data", {}).get("label", None),
            xy=(pos["x"], pos["y"]),
            selected=kwargs.pop("selected", False),
            react_props=kwargs
        )

    def to_tabular(self):
        return {
            "id": self.id_,
            "x": self.xy[0],
            "y": self.xy[1],
            "label": self.label,
        }

    def __eq__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        return (
            self.id_ == other.id_ and
            self.label == other.label and
            self.xy == other.xy and
            self.selected == other.selected and
            self.react_props == other.react_props
        )


class Edge(param.Parameterized):

    source = param.ClassSelector(class_=Node)
    target = param.ClassSelector(class_=Node)
    label = param.String()
    selected = param.Boolean(default=False)
    react_props = param.Dict(default={})
    name = param.String()

    tabular_params = ["source_id", "target_id", "source_label", "target_label",
                      "label"]

    def __init__(self, **params):
        super().__init__(**params)
        self.name = f"Edge{self.source.id_}_{self.target.id_}"

    def to_reactflow(self):
        return {
            "id": f"{self.source.id_} -> {self.target.id_}",
            "source": self.source.id_,
            "target": self.target.id_,
            "label": self.label,
            **self.react_props,
        }

    def to_tabular(self):
        return {
            "source_id": self.source.id_,
            "target_id": self.target.id_,
            "source_label": self.source.label,
            "target_label": self.target.label,
            "label": self.label,
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
        self._node_tabulator = self._init_node_tabulator()
        self._edge_tabulator = self._init_edge_tabulator()
        self._add_node_label = pn.widgets.TextInput(name="Label")
        self._add_node_button = pn.widgets.Button(name="Submit")

        # initialise watchers
        self._updating = False
        self._init_watchers()

        # initalise layout
        self._layout = self._create_layout()

    ###########################################################################
    ## Helper functions
    ###########################################################################
    def _init_reactflow(self):
        return ReactFlowComponent(
            nodes=[n.to_reactflow() for n in self.nodes],
            edges=[e.to_reactflow() for e in self.edges],
            **self.reactflow_params
        )

    def _init_node_tabulator(self):
        df, selected = self._nodes_to_df()
        return pn.widgets.Tabulator(
            value=df,
            show_index=False,
            layout="fit_data",
            editors={"label": "input"},
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
            editors={"label": "input"},
            buttons={'delete': '<i class="fa fa-trash"></i>'},
            selectable="checkbox",
            selection=selected,
            height=250,
            theme="simple",
        )

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
        self.param.watch(self._update_ui_from_nodes_list, "nodes")

        # update state based on reactflow
        self._reactflow.param.watch(self._update_nodes_from_reactflow, "nodes")

        # update state based on tabulator
        self._node_tabulator.on_edit(self._update_nodes_from_tabulator_edit)
        self._node_tabulator.param.watch(self._update_selection_from_tabulator,
                                    "selection")
        self._node_tabulator.on_click(self._handle_tabulator_delete)

        # update state when clicking a button
        self._add_node_button.on_click(self._add_node)

    def _update_ui_from_nodes_list(self, event):
        """
        Updates both ReactFlow and Tabulator when the main 'nodes' list 
        changes.
        """
        self._reactflow.nodes = [n.to_reactflow() for n in self.nodes]
        df, selected_nodes = self._nodes_to_df()
        self._node_tabulator.value = df
        if self._node_tabulator.selection != selected_nodes:
            self._node_tabulator.selection = selected_nodes

    def _update_nodes_from_reactflow(self, event):
        """
        Updates the master 'nodes' list when nodes are changed in ReactFlow 
        (drag/select).
        """
        if self._updating:
            return
        self._updating = True
        try:
            self.nodes = [Node.from_reactflow(n) for n in event.new]
        finally:
            self._updating = False

    def _update_nodes_from_tabulator_edit(self, event):
        """ Update nodes based on label updating of a node """
        if self._updating:
            return
        self._updating = True
        try:
            node_to_update = self.nodes[event.row]
            if event.column == "label":
                node_to_update.label = event.value
                self.nodes = self.nodes[:] # Trigger update
        finally:
            self._updating = False

    def _update_selection_from_tabulator(self, event):
        """Updates node selection state when rows are selected in Tabulator."""
        if self._updating:
            return
        try:
            selected_indices = set(event.new)
            for i, node in enumerate(self.nodes):
                node.selected = i in selected_indices
            self.nodes = self.nodes[:]
        finally:
            self._updating = False

    def _handle_tabulator_delete(self, event):
        if event.column == "delete":
            self.nodes.pop(event.row)
            self.nodes = self.nodes[:]

    def _add_node(self, event):
        new_node = Node(
            id_=str(uuid.uuid4()),
            label=self._add_node_label.value,
            xy = (0, 0),
            selected = False,
            react_props=self.new_node_react_props,
        )
        self.nodes = self.nodes + [new_node]

    ###########################################################################
    ## LAYOUT
    ###########################################################################
    def _create_layout(self):
        """Creates the component's visible layout."""
        controls = pn.Card(
            pn.Row(self._add_node_label, self._add_node_button),
            title="<i class='fa-solid fa-plus'></i> Add Node",
            sizing_mode="stretch_width"
        )

        sidebar = pn.Column(
            pn.pane.Markdown("### Nodes"),
            self._node_tabulator,
            self._edge_tabulator,
            controls,
            width=650
        )
        canvas = pn.Column(
            pn.pane.Markdown("### Canvas"),
            self._reactflow,
            sizing_mode="stretch_both",
        )
        return pn.Row(sidebar, canvas, sizing_mode="stretch_both", min_height=600)

    def __panel__(self):
        return self._layout
