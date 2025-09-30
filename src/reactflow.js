import {
  useCallback,
  useState,
  useRef,
  useEffect,
  useMemo,
} from 'react';
import { 
  ReactFlow,
  ReactFlowProvider,
  Controls,
  Background,
  MiniMap,
  MarkerType,
  Handle,
  Position,
  // applyNodeChanges,
  // applyEdgeChanges,
  addEdge,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';


// 1. Create the CustomNode component
// This component will receive the rendered Panel child via props.data.panel_child
function CustomNode({ data }) {
  return (
    <>
      <Handle type="target" position={Position.Left} />
      <div style={{
        padding: '10px',
        border: '1px solid #777',
        borderRadius: '5px',
        background: '#fff',
        minWidth: '150px',
      }}>
        <h3>{data.label}</h3>
        {data.pane_component}
      </div>
      <Handle type="source" position={Position.Right} />
    </>
  );
}

export function render({ model }) {

  const nodeTypes = useMemo(() => ({ custom: CustomNode }), []);

  const node_panes = model.get_child('panel_nodes');
  const [py_nodes, setPyNodes] = model.useState('reactflow_nodes');
  const [py_edges, setPyEdges] = model.useState('edges');
  const [defaultEdgeOptions] = model.useState('default_edge_options');

  const processed_nodes = useMemo(() =>
    py_nodes.map(node => ({
      ...node,
      data: {
        ...node.data,
        pane_component: node_panes[node.data.pane_index],
      },
    })), [py_nodes, node_panes]);

  // const [nodes, setNodes, onNodesChange] = useNodesState(py_nodes);
  const [nodes, setNodes, onNodesChange] = useNodesState(processed_nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(py_edges);

  // ref for latest nodes and edges
  const nodesRef = useRef(nodes);
  const edgesRef = useRef(edges);

  // sync current value
  useEffect(() => { nodesRef.current = nodes; }, [nodes]);
  useEffect(() => { edgesRef.current = edges; }, [edges]);

  // sync changes from python to local
  useEffect(() => { setNodes(processed_nodes); }, [processed_nodes, setNodes]);
  useEffect(() => { setEdges(py_edges); }, [py_edges, setEdges]);

  // Sync change from local to python
  const syncToPython = useCallback(() => {
    const nodesToSync = nodesRef.current.map(({ data, ...rest }) => {
      const { pane_component, ...serializableData } = data;
      return { ...rest, data: serializableData };
    });
    // setPyNodes(nodesRef.current);
    setPyNodes(nodesToSync);
    setPyEdges(edgesRef.current);
  }, [setPyNodes, setPyEdges]);

  // onConnect needs to be handled specially as it modifies state directly
  const onConnect = useCallback((connection) => {
    const newEdges = addEdge(connection, edgesRef.current);
    setEdges(newEdges);
    setPyEdges(newEdges);
  }, [setEdges, setPyEdges]);

  // Render the external React component with props
  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlowProvider>
        <ReactFlow 
          nodes={nodes}
          edges={edges}
          defaultEdgeOptions={defaultEdgeOptions}
          nodeTypes={nodeTypes}

          // Local state
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}

          // Sync state
          onNodeDragStop={syncToPython}
          onSelectionChange={syncToPython}
          onConnect={onConnect}
        >
          <Controls />
          <MiniMap />
          <Background />
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
}
