import React, { useRef, useState, useCallback, useEffect } from 'react'
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
      onMouseDown={e => { e.stopPropagation(); onStart?.(e, side) }}
      onMouseUp={e => { e.stopPropagation(); onEnd?.(e, side) }}
    />
  )
}

function Card({ comp, onMouseDown, onMouseUp, selected, hasOverride }) {
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
        onMouseUp={onMouseUp}
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
  const { components, connections, moveComponent, setSelectedId, selectedId, selectedIds, setSelectedIds, connect, selectedConnectionId, setSelectedConnectionId, activeScenarioId, activeSystemId, tool, setTool } = useModel()
  const svgRef = useRef(null)
  const [dragging, setDragging] = useState(null) // {id, offsetX, offsetY}
  const [pendingConn, setPendingConn] = useState(null) // { fromId }
  const [scale, setScale] = useState(1)
  const [tx, setTx] = useState(0)
  const [ty, setTy] = useState(0)
  const [marquee, setMarquee] = useState(null) // {x,y,w,h}
  const [cursor, setCursor] = useState({ x: 0, y: 0 })

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
    setSelectedConnectionId(null)

    // Connect tool or Ctrl/Cmd-click: start/finish connection instead of drag
    if (tool === 'connect' || e.ctrlKey || e.metaKey) {
      if (pendingConn?.fromId && pendingConn.fromId !== comp.id) {
        connect(pendingConn.fromId, comp.id)
        setPendingConn(null)
      } else if (pendingConn?.fromId === comp.id) {
        // clicking same component again cancels
        setPendingConn(null)
      } else {
        setPendingConn({ fromId: comp.id })
      }
      // Update selection lightly
      if (!(e.ctrlKey || e.metaKey)) setSelectedIds([comp.id])
      setSelectedId(comp.id)
      return
    }

    // Default: drag to move
    setDragging({ id: comp.id, offsetX, offsetY })
    if (e.ctrlKey || e.metaKey) {
      setSelectedIds(prev => (prev.includes(comp.id) ? prev.filter(id => id !== comp.id) : [...prev, comp.id]))
    } else {
      setSelectedIds([comp.id])
    }
    setSelectedId(comp.id)
  }, [tool, pendingConn, connect, setSelectedId, setSelectedIds, setSelectedConnectionId])

  const onMouseMove = useCallback((e) => {
    const { x: cx, y: cy } = toCanvas(e.clientX, e.clientY)
    setCursor({ x: cx, y: cy })
    if (dragging) {
      const x = cx - dragging.offsetX
      const y = cy - dragging.offsetY
      moveComponent(dragging.id, Math.max(0, x), Math.max(0, y))
      return
    }
    if (marquee) {
      const x0 = marquee.__startX
      const y0 = marquee.__startY
      const left = Math.min(x0, cx)
      const top = Math.min(y0, cy)
      const w = Math.abs(cx - x0)
      const h = Math.abs(cy - y0)
      setMarquee({ __startX: x0, __startY: y0, x: left, y: top, w, h })
    }
  }, [dragging, moveComponent, marquee])

  const onMouseUp = useCallback((e) => {
    if (marquee) {
      // finalize selection
      const rect = marquee
      const within = (c) => {
        const cx1 = c.x, cy1 = c.y, cx2 = c.x + c.w, cy2 = c.y + c.h
        const rx1 = rect.x, ry1 = rect.y, rx2 = rect.x + rect.w, ry2 = rect.y + rect.h
        return !(cx1 > rx2 || cx2 < rx1 || cy1 > ry2 || cy2 < ry1)
      }
      const ids = components.filter(c => c.systemId === activeSystemId && within(c)).map(c => c.id)
      if (e.ctrlKey || e.metaKey) {
        const set = new Set([...(selectedIds||[]), ...ids])
        setSelectedIds(Array.from(set))
      } else {
        setSelectedIds(ids)
      }
      setSelectedId(ids[ids.length - 1] || null)
      setSelectedConnectionId(null)
      setMarquee(null)
    }
    setDragging(null)
  }, [marquee, components, activeSystemId, setSelectedIds, selectedIds, setSelectedId, setSelectedConnectionId])

  // Allow canceling pending connection with Escape or empty-canvas click
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') {
        if (pendingConn?.fromId) {
          setPendingConn(null)
        } else if (tool === 'connect') {
          setTool('select')
        }
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [pendingConn, tool, setTool])

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
    // Ensure any drag is released if mouseup happens on a connector
    setDragging(null)
  }

  const width = 3000
  const height = 2000

  const compsInSystem = components.filter(c => c.systemId === activeSystemId)
  const compIdSet = new Set(compsInSystem.map(c => c.id))

  return (
    <div className="relative flex-1 overflow-auto" onMouseUp={onMouseUp} onMouseMove={onMouseMove}>
      <svg ref={svgRef} width={width} height={height} className="min-w-full min-h-full"
        style={{ backgroundImage: 'linear-gradient(rgba(0,0,0,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(0,0,0,0.08) 1px, transparent 1px)', backgroundSize: '20px 20px', cursor: (tool==='connect' || pendingConn) ? 'crosshair' : 'default' }}
        onMouseDown={(e) => {
          const { x: cx, y: cy } = toCanvas(e.clientX, e.clientY)
          if (tool === 'select') {
            // start marquee on empty space
            setMarquee({ __startX: cx, __startY: cy, x: cx, y: cy, w: 0, h: 0 })
          } else {
            // in connect tool, clicking empty canvas cancels pending connection
            if (pendingConn?.fromId) setPendingConn(null)
            // and exit connect mode to return to selection
            setTool('select')
          }
          if (!(e.ctrlKey || e.metaKey)) setSelectedIds([])
          setSelectedId(null)
          setSelectedConnectionId(null)
        }}
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

          {/* Pending connection preview (from source to cursor) */}
          {pendingConn?.fromId && (() => {
            const from = components.find(c => c.id === pendingConn.fromId)
            if (!from || !compIdSet.has(from.id)) return null
            const center = { x: from.x + from.w/2, y: from.y + from.h/2 }
            const p1 = center
            const p2 = cursor
            const dx = (p2.x - p1.x) * 0.5
            const c1x = p1.x + dx, c1y = p1.y
            const c2x = p2.x - dx, c2y = p2.y
            const d = `M ${p1.x} ${p1.y} C ${c1x} ${c1y}, ${c2x} ${c2y}, ${p2.x} ${p2.y}`
            return <path d={d} fill="none" stroke="#2563eb" strokeWidth={2} markerEnd="url(#arrow-sel)" pointerEvents="none" />
          })()}

          {/* Components */}
          {compsInSystem.map(comp => {
            const pos = computeConnectorPositions(comp)
            const hasOverride = !!(comp.overrides && comp.overrides[activeScenarioId] && Object.keys(comp.overrides[activeScenarioId]||{}).length)
            return (
              <g key={comp.id}>
                <Card
                  comp={comp}
                  selected={(selectedIds||[]).includes(comp.id)}
                  hasOverride={hasOverride}
                  onMouseDown={(e) => onMouseDownCard(e, comp)}
                  onMouseUp={(e) => {
                    e.stopPropagation()
                    if (pendingConn?.fromId && pendingConn.fromId !== comp.id) {
                      connect(pendingConn.fromId, comp.id)
                      setPendingConn(null)
                    }
                    // Ensure drag ends even if mouseup doesn't bubble to container
                    if (dragging) setDragging(null)
                  }}
                />
                {/* Connector dots */}
                <ConnectorDot x={pos.left.x} y={pos.left.y} side="left" onStart={() => onStartConn(comp, 'left')} onEnd={() => onEndConn(comp, 'left')} />
                <ConnectorDot x={pos.right.x} y={pos.right.y} side="right" onStart={() => onStartConn(comp, 'right')} onEnd={() => onEndConn(comp, 'right')} />
                <ConnectorDot x={pos.top.x} y={pos.top.y} side="top" onStart={() => onStartConn(comp, 'top')} onEnd={() => onEndConn(comp, 'top')} />
                <ConnectorDot x={pos.bottom.x} y={pos.bottom.y} side="bottom" onStart={() => onStartConn(comp, 'bottom')} onEnd={() => onEndConn(comp, 'bottom')} />
              </g>
            )
          })}

          {/* Marquee rectangle */}
          {marquee && (
            <rect x={marquee.x} y={marquee.y} width={marquee.w} height={marquee.h} fill="rgba(59,130,246,0.15)" stroke="rgba(59,130,246,0.9)" strokeDasharray="5,5" />
          )}
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
