import { useState, useRef } from 'react';
import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function NetworkGraph({ nodes, edges, onNodeClick, onEdgeClick, selectedNode, selectedEdge }) {
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const svgRef = useRef(null);

  // Simple force-directed layout simulation
  const layoutNodes = (nodesList) => {
    if (!nodesList || nodesList.length === 0) return [];

    const width = 800;
    const height = 600;
    const centerX = width / 2;
    const centerY = height / 2;

    // Group by type for initial positioning
    const byType = {
      PROJECT: [],
      AGENCY: [],
      STATE: [],
      SECTOR: []
    };

    nodesList.forEach(node => {
      if (byType[node.node_type]) {
        byType[node.node_type].push(node);
      }
    });

    // Position projects in center, others around
    const positioned = [];
    
    // Projects in center
    const projectRadius = 200;
    byType.PROJECT.forEach((node, i) => {
      const angle = (i / byType.PROJECT.length) * 2 * Math.PI;
      positioned.push({
        ...node,
        x: centerX + Math.cos(angle) * projectRadius,
        y: centerY + Math.sin(angle) * projectRadius
      });
    });

    // Agencies in outer ring
    const agencyRadius = 280;
    byType.AGENCY.forEach((node, i) => {
      const angle = (i / Math.max(byType.AGENCY.length, 1)) * 2 * Math.PI;
      positioned.push({
        ...node,
        x: centerX + Math.cos(angle) * agencyRadius,
        y: centerY + Math.sin(angle) * agencyRadius
      });
    });

    // States in outer ring
    const stateRadius = 320;
    byType.STATE.forEach((node, i) => {
      const angle = (i / Math.max(byType.STATE.length, 1)) * 2 * Math.PI + Math.PI / 4;
      positioned.push({
        ...node,
        x: centerX + Math.cos(angle) * stateRadius,
        y: centerY + Math.sin(angle) * stateRadius
      });
    });

    // Sectors in outer ring
    const sectorRadius = 360;
    byType.SECTOR.forEach((node, i) => {
      const angle = (i / Math.max(byType.SECTOR.length, 1)) * 2 * Math.PI + Math.PI / 2;
      positioned.push({
        ...node,
        x: centerX + Math.cos(angle) * sectorRadius,
        y: centerY + Math.sin(angle) * sectorRadius
      });
    });

    return positioned;
  };

  const positionedNodes = layoutNodes(nodes, edges);

  const getNodeColor = (node) => {
    if (node.node_type === 'PROJECT') {
      if (node.risk_category === 'CRITICAL') return colors.accent.danger;
      if (node.risk_category === 'VERY_HIGH') return colors.accent.danger;
      if (node.risk_category === 'HIGH') return colors.accent.warning;
      if (node.risk_category === 'MODERATE') return colors.accent.info;
      return colors.accent.success;
    }
    if (node.node_type === 'AGENCY') return colors.accent.primary;
    if (node.node_type === 'STATE') return colors.accent.info;
    if (node.node_type === 'SECTOR') return colors.accent.warning;
    return colors.text.muted;
  };

  const getNodeShape = (node) => {
    if (node.node_type === 'PROJECT') return 'circle';
    if (node.node_type === 'AGENCY') return 'rect';
    if (node.node_type === 'STATE') return 'rect';
    if (node.node_type === 'SECTOR') return 'rect';
    return 'circle';
  };

  const getNodeSize = (node) => {
    if (node.node_type === 'PROJECT') return 20;
    return 15;
  };

  const handleMouseDown = (e) => {
    if (e.target === svgRef.current) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - transform.x, y: e.clientY - transform.y });
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      setTransform({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
        scale: transform.scale
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const zoomSpeed = 0.001;
    const newScale = Math.max(0.1, Math.min(3, transform.scale - e.deltaY * zoomSpeed));
    setTransform({ ...transform, scale: newScale });
  };

  const handleReset = () => {
    setTransform({ x: 0, y: 0, scale: 1 });
  };

  const handleFit = () => {
    setTransform({ x: 0, y: 0, scale: 1 });
  };

  if (!nodes || nodes.length === 0) {
    return (
      <Card padding="lg">
        <div style={{ 
          height: '500px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          color: colors.text.muted 
        }}>
          No network data available
        </div>
      </Card>
    );
  }

  return (
    <Card padding="lg">
      <div style={{ marginBottom: spacing.md, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary }}>
          Network Graph
        </h3>
        <div style={{ display: 'flex', gap: spacing.sm }}>
          <button 
            onClick={handleReset}
            style={{ 
              padding: `${spacing.xs} ${spacing.sm}`,
              fontSize: typography.fontSize.sm,
              backgroundColor: colors.background.secondary,
              border: `1px solid ${colors.border.light}`,
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            Reset View
          </button>
          <button 
            onClick={handleFit}
            style={{ 
              padding: `${spacing.xs} ${spacing.sm}`,
              fontSize: typography.fontSize.sm,
              backgroundColor: colors.background.secondary,
              border: `1px solid ${colors.border.light}`,
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            Fit to Screen
          </button>
        </div>
      </div>

      <div style={{ position: 'relative', height: '600px', overflow: 'hidden', border: `1px solid ${colors.border.light}`, borderRadius: '0.5rem' }}>
        <svg
          ref={svgRef}
          width="100%"
          height="100%"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onWheel={handleWheel}
          style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
        >
          <g transform={`translate(${transform.x}, ${transform.y}) scale(${transform.scale})`}>
            {/* Edges */}
            {edges && edges.map((edge, index) => {
              const sourceNode = positionedNodes.find(n => n.id === edge.source);
              const targetNode = positionedNodes.find(n => n.id === edge.target);
              if (!sourceNode || !targetNode) return null;

              const isSelected = selectedEdge === edge;
              return (
                <line
                  key={index}
                  x1={sourceNode.x}
                  y1={sourceNode.y}
                  x2={targetNode.x}
                  y2={targetNode.y}
                  stroke={isSelected ? colors.accent.primary : colors.border.light}
                  strokeWidth={isSelected ? 3 : 1}
                  onClick={() => onEdgeClick && onEdgeClick(edge)}
                  style={{ cursor: 'pointer' }}
                />
              );
            })}

            {/* Nodes */}
            {positionedNodes.map((node) => {
              const isSelected = selectedNode === node;
              const color = getNodeColor(node);
              const shape = getNodeShape(node);
              const size = getNodeSize(node);

              return (
                <g
                  key={node.id}
                  onClick={() => onNodeClick && onNodeClick(node)}
                  style={{ cursor: 'pointer' }}
                >
                  {shape === 'circle' ? (
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r={size}
                      fill={color}
                      stroke={isSelected ? colors.text.primary : 'none'}
                      strokeWidth={isSelected ? 3 : 0}
                      opacity={isSelected ? 1 : 0.8}
                    />
                  ) : (
                    <rect
                      x={node.x - size}
                      y={node.y - size}
                      width={size * 2}
                      height={size * 2}
                      fill={color}
                      stroke={isSelected ? colors.text.primary : 'none'}
                      strokeWidth={isSelected ? 3 : 0}
                      opacity={isSelected ? 1 : 0.8}
                      rx={2}
                    />
                  )}
                  {node.node_type === 'PROJECT' && node.risk_category && (
                    <text
                      x={node.x}
                      y={node.y + size + 15}
                      textAnchor="middle"
                      fontSize="10"
                      fill={colors.text.secondary}
                    >
                      {node.risk_category}
                    </text>
                  )}
                </g>
              );
            })}
          </g>
        </svg>

        {/* Legend */}
        <div style={{ 
          position: 'absolute', 
          bottom: spacing.md, 
          left: spacing.md,
          backgroundColor: `${colors.background.primary}90`,
          padding: spacing.sm,
          borderRadius: '0.375rem',
          fontSize: typography.fontSize.sm,
          color: colors.text.muted
        }}>
          <div style={{ marginBottom: spacing.xs, fontWeight: 600 }}>Node Types:</div>
          <div style={{ display: 'flex', gap: spacing.sm, flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: colors.accent.success }}></div>
              <span>Project (Low Risk)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: colors.accent.warning }}></div>
              <span>Project (High Risk)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: colors.accent.danger }}></div>
              <span>Project (Critical)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
              <div style={{ width: '12px', height: '12px', backgroundColor: colors.accent.primary, borderRadius: '2px' }}></div>
              <span>Agency</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
              <div style={{ width: '12px', height: '12px', backgroundColor: colors.accent.info, borderRadius: '2px' }}></div>
              <span>State</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
              <div style={{ width: '12px', height: '12px', backgroundColor: colors.accent.warning, borderRadius: '2px' }}></div>
              <span>Sector</span>
            </div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <strong>Controls:</strong> Drag to pan, scroll to zoom, click nodes/edges to select
      </div>
    </Card>
  );
}
