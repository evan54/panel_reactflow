import {
  useCallback
} from 'react';
import { 
  ReactFlow,
  ReactFlowProvider,
  Controls,
  Background,
  MiniMap,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
} from '@xyflow/react';


function serializeMouseEvent(e) {
  return {
    altKey: e.altKey,
    button: e.button,
    buttons: e.buttons,
    clientX: e.clientX,
    clientY: e.clientY,
    ctrlKey: e.ctrlKey,
    metaKey: e.metaKey,
    movementX: e.movementX,
    movementY: e.movementY,
    pageX: e.pageX,
    pageY: e.pageY,
    relatedTarget: e.relatedTarget ? String(e.relatedTarget) : null,
    screenX: e.screenX,
    screenY: e.screenY,
    shiftKey: e.shiftKey
  };
}


export function render({ model }) {
  const [nodes, setNodes] = model.useState("nodes");
  const [edges, setEdges] = model.useState("edges");

  const onNodesChange = useCallback((changes) => {
    setNodes((nds) => applyNodeChanges(changes, nds));
    // model.send_msg({ type: "nodes_change", changes });
  }, [setNodes, model]);

  const genericMouseEvent = (type) => (event, ...args) => {
    model.send_msg([type, [serializeMouseEvent(event), args]]);
  }

  const genericHandler = (type) => (...args) => {
    // works
    const safeArgs = args.map(a => {
      try {
        return JSON.parse(JSON.stringify(a, getCircularReplacer()));
      } catch {
        return String(a); // Fallback if still not serializable
      }
    });
    model.send_msg([type, safeArgs]);
  };

  const onConnect = useCallback((connection) => {
    setEdges((eds) => addEdge(connection, eds));
    model.send_msg(['edge_connect', connection ]);
  }, [addEdge, model]);

  const onEdgesChange = (changes) => {
    setEdges((eds) => applyEdgeChanges(changes, eds));
    model.send_msg(['edges_change', changes]);
  };

  // Render the external React component with props
  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlowProvider>
        <ReactFlow 
         nodes={nodes}
         edges={edges}

         // nodes
         onNodesChange={onNodesChange}
         onNodeClick={genericMouseEvent('node_click')}
         onNodeDragStop={genericMouseEvent('node_drag_stop')}

         // edges
         onEdgesChange={onEdgesChange}
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
