from pathlib import Path
import panel as pn
import param
from panel.custom import ReactComponent

pn.extension()


class ReactFlowComponent(ReactComponent):
    """A Panel component that renders a simple React Flow diagram."""

    nodes = param.List()
    edges = param.List()

    _importmap = {
        "imports": {
            "@xyflow/react": "https://esm.sh/@xyflow/react",
        }
    }
    _esm = Path(__file__).parent / "reactflow.js"
    # _stylesheets = ["https://cdn.jsdelivr.net/npm/reactflow/dist/style.min.css"]
    _stylesheets = [
        "https://cdn.jsdelivr.net/npm/@xyflow/react/dist/style.css",
        """
        .react-flow__node.selected {
            background-color: coral;
        }
        """.strip()
    ]

    def _handle_msg(self, msg):
        event_type, data =  msg
        print(event_type)
        if event_type == "node_click":
            self._on_node_click(data)
        elif event_type == "node_drag_stop":
            self._on_node_drag_stop(data)
        elif event_type == "edge_connect":
            self._on_edge_connect(data)

def set_nodes(flow):

    flow.nodes = [
        {"id": "1", "position": {"x": 0, "y":   0}, "data": {"label": "1"}}, 
        {"id": "2", "position": {"x": 0, "y": 100}, "data": {"label": "2"}}, 
        {"id": "3", "position": {"x": 0, "y": 200}, "data": {"label": "3"}}, 
    ]

def set_edges(flow):
    set_nodes(flow)
    flow.edges = [{
        "id": "1 > 2",
        "source": "1",
        "target": "2",
        "label": "my edge",
    }]

flow = ReactFlowComponent(sizing_mode="stretch_both",
                          styles={"border": "1px solid gray"})
set_edges(flow)
button = pn.widgets.Button(name="set nodes")
button.on_click(lambda _: set_nodes(flow))

app = pn.template.FastGridTemplate(
    favicon="https://python.org/static/favicon.ico"
)

app.main[0:5, :] = pn.Column(
    pn.pane.Markdown("hello"),
    pn.Column(flow, sizing_mode="stretch_both"),
    button,
)
app.servable()
