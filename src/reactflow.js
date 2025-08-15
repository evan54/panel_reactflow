import {
  useCallback,
  useState,
  useRef,
  useEffect,
} from 'react';
import { 
  ReactFlow,
  ReactFlowProvider,
  Controls,
  Background,
  MiniMap,
  MarkerType,
  // applyNodeChanges,
  // applyEdgeChanges,
  addEdge,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';

export function render({ model }) {

  // console.log("rendering...")
  const [py_nodes, setPyNodes] = model.useState('nodes');
  const [py_edges, setPyEdges] = model.useState('edges');
  const [defaultEdgeOptions] = model.useState('default_edge_options');
  const [nodes, setNodes, onNodesChange] = useNodesState(py_nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(py_edges);

  // ref for latest nodes and edges
  const nodesRef = useRef(nodes);
  const edgesRef = useRef(edges);

  // sync current value
  useEffect(() => { nodesRef.current = nodes; }, [nodes]);
  useEffect(() => { edgesRef.current = edges; }, [edges]);

  // sync changes from python to local
  useEffect(() => { setNodes(py_nodes); }, [py_nodes, setNodes]);
  useEffect(() => { setEdges(py_edges); }, [py_edges, setEdges]);

  // Sync change from local to python
  const syncToPython = useCallback(() => {
    setPyNodes(nodesRef.current);
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
