import React, { useRef, useState, useCallback } from 'react'
import { useModel } from '../context/ModelContext.jsx'

function ConnectorDot({ x, y, onStart, onEnd, side }) {
  return (
    <circle
      className="connector-dot"
      cx={x}
      cy={y}
      r={5}
      fill="#3b82f6"
      stroke="#1e40af"
      strokeWidth={1}
      onMouseDown={e => onStart?.(e, side)}
      onMouseUp={e => onEnd?.(e, side)}
    />
  )
}

function Card({ comp, onMouseDown, selected, hasOverride }) {
  const shapeClass = comp.type === 'Flow' ? 'shape-flow'
    : comp.type === 'Calculator' ? 'shape-calculator'
    : comp.type === 'Parameter' ? 'shape-parameter'
    : 'shape-stock'
  const colorClass = comp.type === 'Flow' ? 'border-green-400 bg-green-50'
    : comp.type === 'Calculator' ? 'border-yellow-400 bg-yellow-50'
    : comp.type === 'Parameter' ? 'border-purple-400 bg-purple-50'
    : comp.type === 'Reference' ? 'border-gray-400 bg-gray-50'
    : 'border-blue-400 bg-blue-50'
  return (
    <foreignObject x={comp.x} y={comp.y} width={comp.w} height={comp.h}>
      <div
        className={`border shadow-sm h-full w-full flex items-center justify-center select-none ${shapeClass} ${colorClass} ${selected? 'ring-2 ring-blue-400': (hasOverride ? 'ring-2 ring-amber-400' : '')} ${comp.type==='Reference' ? 'border-dashed' : ''}`}
        onMouseDown={onMouseDown}
        onClick={e => e.stopPropagation()}
      >
        <div className="text-sm text-gray-700 font-medium px-2 text-center truncate">
          {comp.name} <span className="text-xs text-gray-400">({comp.type})</span>
        </div>
      </div>
    </foreignObject>
  )
}

export default function Canvas({ onOpenPivot, onOpenCalc }) {
  const { components, connections, moveComponent, setSelectedId, selectedId, connect, selectedConnectionId, setSelectedConnectionId, activeScenarioId, activeSystemId } = useModel()
  const svgRef = useRef(null)
  const [dragging, setDragging] = useState(null) // {id, offsetX, offsetY}
  const [pendingConn, setPendingConn] = useState(null) // { fromId }
  const [scale, setScale] = useState(1)
  const [tx, setTx] = useState(0)
  const [ty, setTy] = useState(0)

  const toCanvas = (clientX, clientY) => {
    if (!svgRef.current) return { x: 0, y: 0 }
    const rect = svgRef.current.getBoundingClientRect()
    return { x: ((clientX ?? 0) - rect.left - tx) / scale, y: ((clientY ?? 0) - rect.top - ty) / scale }
  }

  const onMouseDownCard = useCallback((e, comp) => {
    e.stopPropagation()
    const { x: cx, y: cy } = toCanvas(e.clientX, e.clientY)
    const offsetX = cx - comp.x
    const offsetY = cy - comp.y
    setDragging({ id: comp.id, offsetX, offsetY })
    setSelectedId(comp.id)
    setSelectedConnectionId(null)
  }, [setSelectedId])

  const onMouseMove = useCallback((e) => {
    if (!dragging) return
    const { x: cx, y: cy } = toCanvas(e.clientX, e.clientY)
    const x = cx - dragging.offsetX
    const y = cy - dragging.offsetY
    moveComponent(dragging.id, Math.max(0, x), Math.max(0, y))
  }, [dragging, moveComponent])

  const onMouseUp = useCallback(() => setDragging(null), [])

  const computeConnectorPositions = (c) => {
    const w = typeof c.w === 'number' ? c.w : 180
    const h = typeof c.h === 'number' ? c.h : 60
    const x = typeof c.x === 'number' ? c.x : 0
    const y = typeof c.y === 'number' ? c.y : 0
    return {
      left: { x: x, y: y + h/2 },
      right: { x: x + w, y: y + h/2 },
      top: { x: x + w/2, y: y },
      bottom: { x: x + w/2, y: y + h },
    }
  }

  const onStartConn = (comp, side) => {
    setPendingConn({ fromId: comp.id })
  }
  const onEndConn = (comp, side) => {
    if (pendingConn?.fromId && pendingConn.fromId !== comp.id) {
      connect(pendingConn.fromId, comp.id)
    }
    setPendingConn(null)
  }

  const width = 3000
  const height = 2000

  const compsInSystem = components.filter(c => c.systemId === activeSystemId)
  const compIdSet = new Set(compsInSystem.map(c => c.id))

  return (
    <div className="relative flex-1 overflow-auto" onMouseUp={onMouseUp} onMouseMove={onMouseMove}>
      <svg ref={svgRef} width={width} height={height} className="min-w-full min-h-full"
        style={{ backgroundImage: 'linear-gradient(rgba(0,0,0,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(0,0,0,0.08) 1px, transparent 1px)', backgroundSize: '20px 20px' }}
        onMouseDown={() => { setSelectedId(null); setSelectedConnectionId(null) }}
      >
        <g transform={`translate(${tx},${ty}) scale(${scale})`}>
          <defs>
            <marker id="arrow" markerWidth="10" markerHeight="10" refX="10" refY="5" orient="auto">
              <path d="M0,0 L10,5 L0,10 z" fill="#94a3b8" />
            </marker>
            <marker id="arrow-sel" markerWidth="10" markerHeight="10" refX="10" refY="5" orient="auto">
              <path d="M0,0 L10,5 L0,10 z" fill="#2563eb" />
            </marker>
          </defs>
          {/* Connections */}
          {connections.map(cn => {
            const from = components.find(c => c.id === cn.fromId)
            const to = components.find(c => c.id === cn.toId)
            if (!from || !to) return null
            if (!compIdSet.has(from.id) || !compIdSet.has(to.id)) return null
            const p1 = computeConnectorPositions(from).right
            const p2 = computeConnectorPositions(to).left
            const isSel = selectedConnectionId === cn.id
            const dx = (p2.x - p1.x) * 0.5
            const c1x = p1.x + dx, c1y = p1.y
            const c2x = p2.x - dx, c2y = p2.y
            const d = `M ${p1.x} ${p1.y} C ${c1x} ${c1y}, ${c2x} ${c2y}, ${p2.x} ${p2.y}`
            return <path key={cn.id} d={d} fill="none" stroke={isSel? '#2563eb' : '#94a3b8'} strokeWidth={isSel? 3 : 2} markerEnd={`url(#${isSel? 'arrow-sel':'arrow'})`} onClick={(e) => { e.stopPropagation(); setSelectedConnectionId(cn.id); setSelectedId(null) }} />
          })}

          {/* Components */}
          {compsInSystem.map(comp => {
            const pos = computeConnectorPositions(comp)
            const hasOverride = !!(comp.overrides && comp.overrides[activeScenarioId] && Object.keys(comp.overrides[activeScenarioId]||{}).length)
            return (
              <g key={comp.id}>
                <Card
                  comp={comp}
                  selected={selectedId === comp.id}
                  hasOverride={hasOverride}
                  onMouseDown={(e) => onMouseDownCard(e, comp)}
                />
                {/* Connector dots */}
                <ConnectorDot x={pos.left.x} y={pos.left.y} side="left" onStart={() => onStartConn(comp, 'left')} onEnd={() => onEndConn(comp, 'left')} />
                <ConnectorDot x={pos.right.x} y={pos.right.y} side="right" onStart={() => onStartConn(comp, 'right')} onEnd={() => onEndConn(comp, 'right')} />
                <ConnectorDot x={pos.top.x} y={pos.top.y} side="top" onStart={() => onStartConn(comp, 'top')} onEnd={() => onEndConn(comp, 'top')} />
                <ConnectorDot x={pos.bottom.x} y={pos.bottom.y} side="bottom" onStart={() => onStartConn(comp, 'bottom')} onEnd={() => onEndConn(comp, 'bottom')} />
              </g>
            )
          })}
        </g>
      </svg>

      {/* Zoom controls */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 bg-white/90 rounded shadow border flex items-center gap-1 px-2 py-1">
        <button className="text-xs px-2 py-1 bg-gray-100 rounded" onClick={() => setScale(s => Math.max(0.25, +(s - 0.1).toFixed(2)))}>-</button>
        <div className="text-xs w-16 text-center">{Math.round(scale*100)}%</div>
        <button className="text-xs px-2 py-1 bg-gray-100 rounded" onClick={() => setScale(s => Math.min(3, +(s + 0.1).toFixed(2)))}>+</button>
        <button className="text-xs px-2 py-1 bg-gray-100 rounded" onClick={() => { setScale(1); setTx(0); setTy(0) }}>Reset</button>
      </div>
    </div>
  )
}
