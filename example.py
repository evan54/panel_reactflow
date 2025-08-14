import panel as pn
import param
import reactflow

from importlib import reload
reload(reactflow)


def get_flow():

    # common node properties
    common_node_props = {"sourcePosition": "right", "targetPosition": "left"}

    # set nodes up and add default props
    nodes = [{**n, **common_node_props} for n in [
        {"id": "1", "position": {"x": 0, "y": 0}, "data": {"label": "1"}}, 
        {"id": "2", "position": {"x": 250, "y": 0}, "data": {"label": "2"}}, 
        {"id": "3", "position": {"x": 500, "y": 0}, "data": {"label": "3"}}, 
    ]]

    # common edge properties
    common_edge_props = {
        "markerEnd": {"type": "arrowclosed"},
        "style": {"strokeWidth": 3},
        "deletable": True,
    }

    edges = [{
        "id": "1 > 2",
        "source": "1",
        "target": "2",
        "label": "my edge",
    }]

    flow = reactflow.ReactFlowComponent(
        nodes=nodes,
        edges=edges,

        default_edge_options=common_edge_props,
        sizing_mode="stretch_width",
        styles={"border": "1px solid gray"},
        height=100,
        stylesheets=[
        """
        .react-flow__node.selected {
            background-color: coral;
        }
        """.strip()]
    )

    flow_editor = reactflow.ReactFlowEditor(
        nodes=nodes,
        edges=edges,
        reactflow_params=dict(
            styles={"border": "1px solid gray"},
            default_edge_options=common_edge_props,
            sizing_mode="stretch_both",
            stylesheets=[
                """
                .react-flow__node.selected {
                    background-color: coral;
                }
                """.strip()
            ],
        ),
    )

    return flow, flow_editor


flow, flow_editor = get_flow()
button = pn.widgets.Button(name="add node")

app = pn.template.FastGridTemplate(
    favicon="https://python.org/static/favicon.ico"
)

app.main[0:10, :] = pn.Column(
    pn.pane.Markdown("hello"),
    pn.Column(flow),
    button,
    pn.layout.Divider(),
    flow_editor,
)
app.servable()
