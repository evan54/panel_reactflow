from pathlib import Path
import uuid

import pandas as pd

import panel as pn
import param
import panel.custom
import panel.viewable

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

    _importmap = {
        "imports": {
            "@xyflow/react": "https://esm.sh/@xyflow/react",
        }
    }
    _esm = Path(__file__).parent / "reactflow.js"
    _stylesheets = [
        "https://cdn.jsdelivr.net/npm/@xyflow/react/dist/style.css",
    ]


class NodeTable(pn.viewable.Viewer):

    nodes = param.List()
    node_cols = param.List()

    def __init__(self, *, nodes=None, node_cols=None, on_click=None):
        if nodes is None:
            nodes = []
        if len(nodes) > 0:
            node_cols = list(nodes[0])
        super().__init__(nodes=nodes, node_cols=node_cols)
        self._tab = self._make_nodes_table(on_click)

    def _nodes_to_df(self):
        if not self.nodes:
            return pd.DataFrame(columns=self.node_cols)
        df = pd.DataFrame([
            {
                "id": n["id"], 
                "label": n.get("data", {}).get("label", ""),
                "x": n["position"]["x"],
                "y": n["position"]["y"],
            }
            for n in self.nodes
        ])
        return df

    def _on_edit(self, event):
        row, col, val = event.row, event.column, event.value
        if col == "label":
            new_nodes = list(self.nodes)
            new_nodes[row]["data"]["label"] = val
            self.nodes = new_nodes

    def _make_nodes_table(self, on_click):
        df = self._nodes_to_df()
        tab = pn.widgets.Tabulator(
            df,
            show_index=False,
            layout="fit_data",
            editors={
                "label": "input",
            },
            buttons={'delete': '<i class="fa fa-trash"></i>'},
            selectable="checkbox",
            height=250,
            theme="simple",
            on_edit=self._on_edit,
            on_click=on_click,
        )
        return tab

    @pn.depends("nodes", watch=True)
    def _update_selected(self, *args, **kwargs):
        self._tab.selection = [
            i for i, n in enumerate(self.nodes) if n.get("selected", False)]

    @pn.depends("nodes", watch=True)
    def update_values(self):
        self._tab.value = self._nodes_to_df()

    def __panel__(self):
        return self._tab


class ReactFlowEditor(pn.custom.PyComponent):
    """
    Goals:
    * edit the label of a node
    * add a node
    * delete a node
    * select a node
    """

    reactflow_params = param.Dict()

    # UI options
    # --- Private: widgets and components
    _nodes_table = param.ClassSelector(class_=NodeTable)
    _edges_table = None
    _reactflow = param.ClassSelector(class_=ReactFlowComponent)

    # Column order to enforce on the grids
    _NODE_COLS = ("id", "label",)
    _EDGE_COLS = ("id", "source", "target",)

    def __init__(self, _new_node_props=None, **params):
        nodes = params.pop("nodes", [])
        edges = params.pop("edges", [])
        super().__init__(**params)

        self._new_node_props = _new_node_props
        self._nodes_table = NodeTable(nodes=nodes,
                                      on_click=self._table_on_click_delete)
        self._reactflow = ReactFlowComponent(
            nodes=nodes, edges=edges, **self.reactflow_params)
        self._reactflow.link(self._nodes_table, nodes="nodes")

    def _table_on_click_delete(self, event):
        if event.column == "delete":
            self._reactflow.nodes = [
                n for i, n in enumerate(self._reactflow.nodes)
                if i != event.row
            ]

    def _add_node_layout(self):
        self._add_node_label = pn.widgets.TextInput(name="Label")
        self._add_node_button = pn.widgets.Button(name="Submit")
        self._add_node_button.on_click(self._add_node)
        return pn.Card(
            self._add_node_label,
            self._add_node_button,
            title="Add Node", 
            sizing_mode="stretch_width"
        )

    def _add_node(self, event):
        new_node = {
            "id": str(uuid.uuid4()),
            "position": {"x": 0, "y": 0},
            "data": {"label": self._add_node_label.value},
        }
        if self._new_node_props:
            new_node.update(self._new_node_props)
        new_nodes = self._reactflow.nodes + [new_node]
        self._reactflow.nodes = new_nodes

    def _delete_node_layout(self):
        self._delete_selections_button = pn.widgets.Button(name="Delete selected")
        self._delete_selections_button.on_click(self._delete_node)
        return self._delete_selections_button

    def _delete_node(self, event):
        self._reactflow.nodes = [
            n for n in self._reactflow.nodes
            if not n.get("selected", False)
        ]

    def _update_from_table(self, event):
        self._reactflow.nodes = self._nodes_table.nodes

    def _submit_update_layout(self):
        self._submit_update_button = pn.widgets.Button(name="Submit updates")
        self._submit_update_button.on_click(self._update_from_table)
        return self._submit_update_button
       
    def __panel__(self):

        # return pn.pane.Markdown("## ReactFlow Editor", sizing_mode="stretch_width")
        header = pn.Row(
            pn.pane.Markdown("## ReactFlow Editor", sizing_mode="stretch_width"),
            pn.layout.HSpacer(),
        )

        grids = pn.Column(
            pn.pane.Markdown("**Nodes** (id, label)"),
            self._nodes_table,
            pn.Spacer(height=8),
            pn.pane.Markdown("**Edges** (id, source, target)"),
            self._edges_table,
            pn.Row(self._delete_node_layout, self._submit_update_layout),
            self._add_node_layout,
            sizing_mode="stretch_both",
        )

        canvas = pn.Column(
            pn.pane.Markdown("**Canvas**"),
            self._reactflow,
            sizing_mode="stretch_both",
        )

        layout = pn.Row(
            grids,
            canvas,
            sizing_mode="stretch_both",
            height=600,
        )
        return pn.Column(header, layout, sizing_mode="stretch_both")
