# panel_reactflow

Goal is to allow modification and bidirectional communication of a graph like structure. JS library ported is http://www.reactflow.dev/

Idea was to be similar to streamlit's cytoscape (https://github.com/vivien000/st-cytoscape).

Other very interesting project along these lines is https://github.com/Zelfior/reactflow_component/blob/master/reactflow.py but this seems to be mostly around a computation enginge.

ReactflowEditor (possibly to be deprecated)
<img width="1718" height="854" alt="image" src="https://github.com/user-attachments/assets/39b952cf-a64e-4b3b-94f6-0a7380164038" />

Example with panes:
<img width="1474" height="873" alt="image" src="https://github.com/user-attachments/assets/136c5e6f-c09d-4ff4-9a28-d06bebfbff6c" />


## TODO
* updates from the table isn't reflected in the reactflow component
* Right now the example.py is broken and ReactFlowEditor - however this might be deprecated because of the use of panes in nodes and nodes to be passed as a list of dicts to ReactFlowComponent which is a more bare bones component that should be used
