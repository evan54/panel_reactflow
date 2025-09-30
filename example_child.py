import panel as pn

import panel.custom
import panel.viewable


import src.reactflow as rf


nodes_full = [
    {
        "id": "1",
        "position": {"x": 0, "y": 0},
        "data": {
            "label": "node 1",
        },
        "panes": pn.Column(
            pn.widgets.TextInput(name="Name", placeholder="Enter name..."),
            pn.widgets.Select(name='Select', 
                              options=['Biology', 'Chemistry', 'Physics']),
        ),
    },
    {
        "id": "2",
        "position": {"x": 0, "y": 100},
        "data": {
            "label": "node 2",
        },
        "panes": pn.Column(
            pn.widgets.TextInput(name="Name", placeholder="Enter name..."),
            pn.widgets.Select(name='Select', 
                              options=['Math', 'English']),
        ),
    },
    {
        "id": "3",
        "position": {"x": 0, "y": 100},
        "data": {
            "label": "node 3",
        },
    },
    {
        "id": "4",
        "position": {"x": 0, "y": 100},
        "panes": pn.Column(
            pn.widgets.TextInput(name="Name", placeholder="Enter name..."),
            pn.widgets.Select(name='Select', 
                              options=['Chem', 'History']),
        ),
    },
]

common_edge_props = {
    "markerEnd": {"type": "arrowclosed"},
    "style": {"strokeWidth": 3},
    "deletable": True,
}


"""
nodes = []
node_panes = []
for i, n in enumerate(nodes_full):
    node_panes.append(n.pop("panes"))

    if "data" in n:
        n["data"]["pane_index"] = i
    else:
        n["data"] = {"pane_index": i}
    n["type"] = "custom"
    nodes.append(n)
"""

def my_fun(x):
    print(x)

# node_panes[0].objects[0].param.watch(my_fun, "value")


app = rf.ReactFlowComponent(
    nodes=nodes_full,
    edges=[],
    height=1600,
    sizing_mode="stretch_width",
    default_edge_options=common_edge_props,
    stylesheets=[
        """
        .react-flow__node.selected {
            background-color: coral;
            border: 2px solid black;
        }

        .react-flow__node {
            background-color: white;
            border: 2px solid #777;
            border-radius: 10px;
        }

        """.strip(),
        # """
        # /* 1. Define a default background for the child, using a variable. */
        # .bk-Column {
        #     background-color: var(--node-bg-color, white);
        #     border-radius: inherit; /* Make child corners match parent's corners */
        #     width: 100%;
        #     height: 100%;
        # }

        # /* 2. When the parent node is selected, change the VALUE of the variable. */
        # .react-flow__node.selected {
        #     --node-bg-color: #FFDAB9; /* A pleasant light coral/peach color */
        #     box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        # }
        # """,
    ],
)

pn.Row(
    app,
).servable()
