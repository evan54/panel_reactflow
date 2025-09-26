import panel as pn
import param
import src.reactflow as rf

from importlib import reload
reload(rf)


def get_flow():

    # common node properties
    common_node_props = {"sourcePosition": "right", "targetPosition": "left"}

    # set nodes up and add default props
    nodes = [{**n, **common_node_props} for n in [
        {"id": "1", "position": {"x": 0, "y": 0}, "data": {"label": "1"}}, 
        {"id": "2", "position": {"x": 250, "y": 0}, "data": {"label": "2"}}, 
        {"id": "3", "position": {"x": 500, "y": 0}, "data": {"label": "3"}}, 
    ]]

    nodes = [
        rf.Node(id_="1", xy=(0, 0), name="1", react_props=common_node_props),
        rf.Node(id_="2", xy=(250, 0), name="2", react_props=common_node_props,
            selected=True),
        rf.Node(id_="3", xy=(500, 0), name="3", react_props=common_node_props),
    ]
    # common edge properties
    common_edge_props = {
        "markerEnd": {"type": "arrowclosed"},
        "style": {"strokeWidth": 3},
        "deletable": True,
    }

    edges = [
        rf.Edge(source=nodes[0], target=nodes[1], weight=0.1),
        rf.Edge(source=nodes[1], target=nodes[2], weight=0.),
    ]

    flow = rf.ReactFlowComponent(
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

    flow_editor = rf.ReactFlowEditor(
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
        new_node_react_props=common_node_props,
    )

    return None, flow_editor

flow, flow_editor = get_flow()
button = pn.widgets.Button(name="add node")

app = pn.template.FastGridTemplate(
    favicon="https://python.org/static/favicon.ico",
    title="Reactflow example",
)

app.main[0:10, :] = pn.Column(
    flow_editor,
)
app.servable()
