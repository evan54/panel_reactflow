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
  applyNodeChanges,
  applyEdgeChanges,
  useNodesState,
  useEdgesState,
  addEdge,
} from '@xyflow/react';

export function render({ model }) {

  console.log("rendering...")
  const [py_nodes, setPyNodes] = model.useState('nodes');
  const [py_edges, setPyEdges] = model.useState('edges');
  const [defaultEdgeOptions] = model.useState('default_edge_options');

  // Helper functions
  const onNodesChange = useCallback(
    (changes) => setPyNodes((nds) => {
      const updated = applyNodeChanges(changes, nds);
      // console.log('Update nodes:', updated);
      return updated;
    }),
    [setPyNodes],
  );

  const onEdgesChange = useCallback(
    (changes) =>
      setPyEdges((eds) => {
        const updated = applyEdgeChanges(changes, eds);
        // console.log('Updated edges:', updated);
        return updated;
      }),
    [setPyEdges],
  );

  // Goal here is to update the python state with the selected nodes
  /*const onSelectionChange = useCallback(
    ({ nodes: selected_nodes, edges: selected_edges }) => {
      const selectedNodeIds = new Set(selected_nodes.map(n => n.id));
      model.send_msg("update_selected_nodes", selectedNodeIds)
    }, []
  );

  // Update python when a node is no longer dragged
  const onNodeDragStop = (event, ...changes) => {
    applyNodeChanges(changes, py_nodes)
  }
  */

  const onConnect = useCallback((connection) => {
    setPyEdges((eds) => addEdge(connection, eds));
    // model.send_msg(['edge_connect', connection ]);
  }, [addEdge, model]);

  // Render the external React component with props
  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlowProvider>
        <ReactFlow 
         nodes={py_nodes}
         edges={py_edges}
         defaultEdgeOptions={defaultEdgeOptions}

         // nodes
         onNodesChange={onNodesChange}
         // onNodeDrag={onNodesChange}
         // onNodeDragStop={onNodeDragStop}

         // edges
         onEdgesChange={onEdgesChange}
         onConnect={onConnect}

         // other
         // onSelectionChange={onSelectionChange}
        >

          <Controls />
          <MiniMap />
          <Background />
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
}

  /*

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

  const genericMouseEvent = (type) => (event, ...args) => {
    console.log(type)
    console.log(event, args)
    setPyNodes((nds) => {
      const next = applyNodeChanges(args, nds);
      return next;
    });
  }

  const genericHandler = (type) => (...args) => {
    // works
    const safeArgs = args.map(a => {
      try {
        return JSON.parse(JSON.stringify(a));
      } catch {
        return String(a);
      }
    });
    model.send_msg([type, safeArgs]);
  };
  */


