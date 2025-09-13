import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useUi } from '../context/UiContext.jsx'

// Basic, dependency-free, dockable panels for four panel types.
// This component renders dock regions and floating panels.

function Header({ title, onClose, onFloat, onDockMenu, focusRef, onDragStart }) {
  return (
    <div
      className="flex items-center justify-between px-2 py-1 bg-gray-200 text-gray-800 cursor-move select-none"
      tabIndex={0}
      ref={focusRef}
      onMouseDown={onDragStart}
      onKeyDown={(e) => {
        if (e.key === 'Enter') { e.preventDefault(); onDockMenu?.() }
        if (e.key === 'Escape') { e.preventDefault(); /* drag cancel handled at top level */ }
      }}
      aria-label={`${title} panel header`}
    >
      <div className="text-xs font-medium truncate pr-2">{title}</div>
      <div className="flex items-center gap-1">
        <button title="Undock/Float" className="text-[10px] bg-gray-300 hover:bg-gray-400 rounded px-1 py-0.5" onClick={(e) => { e.stopPropagation(); onFloat?.() }}>Float</button>
        <button title="Close" className="text-[10px] bg-gray-300 hover:bg-gray-400 rounded px-1 py-0.5" onClick={(e) => { e.stopPropagation(); onClose?.() }}>×</button>
      </div>
    </div>
  )
}

function FloatingPanel({ fp, render, chooseRegion, showDockMenu, zIndex, onSnapChange, onSnapActive, getBounds }) {
  const { moveFloat, resizeFloat, dockPanel, togglePanel, bringToFront, toggleMaximize } = useUi()
  const [pos, setPos] = useState({ x: fp.x, y: fp.y })
  const [size, setSize] = useState({ w: fp.w, h: fp.h })
  useEffect(() => { setPos({ x: fp.x, y: fp.y }); setSize({ w: fp.w, h: fp.h }) }, [fp.x, fp.y, fp.w, fp.h])
  const dragRef = useRef(null)

  useEffect(() => () => {
    // cleanup any pending listeners on unmount
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }, [])

  const onMove = (e) => {
    const d = dragRef.current
    if (!d) return
    if (d.mode === 'move') {
      setPos({ x: d.ox + (e.clientX - d.sx), y: d.oy + (e.clientY - d.sy) })
      const region = chooseRegion(e.clientX, e.clientY)
      onSnapChange && onSnapChange(region)
    } else if (d.mode === 'resize') {
      const w = Math.max(220, d.ow + (e.clientX - d.sx))
      const h = Math.max(160, d.oh + (e.clientY - d.sy))
      setSize({ w, h })
    }
  }
  const onUp = (e) => {
    const d = dragRef.current
    if (!d) return
    if (d.mode === 'move') {
      const region = chooseRegion(e.clientX, e.clientY)
      if (region) dockPanel(fp.id, region)
      else moveFloat(fp.id, Math.max(8, pos.x), Math.max(64, pos.y))
      onSnapActive && onSnapActive(false)
      onSnapChange && onSnapChange(null)
    } else if (d.mode === 'resize') {
      resizeFloat(fp.id, size.w, size.h)
    }
    dragRef.current = null
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }

  const onDragStart = (e) => {
    e.preventDefault(); e.stopPropagation()
    if (fp.max) {
      const nx = (typeof fp.prevX === 'number') ? fp.prevX : fp.x
      const ny = (typeof fp.prevY === 'number') ? fp.prevY : fp.y
      const nw = (typeof fp.prevW === 'number') ? fp.prevW : fp.w
      const nh = (typeof fp.prevH === 'number') ? fp.prevH : fp.h
      setPos({ x: nx, y: ny })
      setSize({ w: nw, h: nh })
      toggleMaximize(fp.id)
    }
    dragRef.current = { mode: 'move', sx: e.clientX, sy: e.clientY, ox: pos.x, oy: pos.y }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    onSnapActive && onSnapActive(true)
  }
  const onResizeStart = (e) => {
    e.preventDefault(); e.stopPropagation()
    dragRef.current = { mode: 'resize', sx: e.clientX, sy: e.clientY, ow: size.w, oh: size.h }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
  }

  const onKey = (e) => {
    if (!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)) return
    const d = e.shiftKey ? 10 : 1
    const dx = e.key==='ArrowLeft'? -d : e.key==='ArrowRight'? d : 0
    const dy = e.key==='ArrowUp'? -d : e.key==='ArrowDown'? d : 0
    const nx = pos.x + dx, ny = pos.y + dy
    setPos({ x: nx, y: ny })
    moveFloat(fp.id, Math.max(8, nx), Math.max(64, ny))
  }

  const b = getBounds ? getBounds() : { left:0, top:0, width: window.innerWidth, height: window.innerHeight }
  const style = fp.max
    ? { left: 0, top: 56, width: b.width, height: Math.max(120, b.height - 56 - 60), zIndex: zIndex || 40 }
    : { left: pos.x, top: Math.max(64, pos.y), width: size.w, height: size.h, zIndex: zIndex || 40 }

  return (
    <div
      className="absolute bg-white border shadow-lg rounded overflow-hidden pointer-events-auto"
      style={style}
      onMouseDown={() => { bringToFront(fp.id) }}
    >
      <div onKeyDown={onKey} onDoubleClick={() => toggleMaximize(fp.id)}>
        <Header title={fp.title} onClose={() => togglePanel(fp.id)} onFloat={() => { /* already float */ }} onDockMenu={(e)=>showDockMenu(fp.id, e)} focusRef={undefined} onDragStart={onDragStart} />
      </div>
      <div className="relative" style={{ width: '100%', height: 'calc(100% - 28px)' }}>
        {render?.() || null}
        {!fp.max && <div className="absolute right-0 bottom-0 w-3 h-3 cursor-nwse-resize" onMouseDown={onResizeStart} />}
      </div>
    </div>
  )
}

export default function WindowManager({ panels }) {
  // panels: { id: { title, render: () => JSX } }
  const { layout, dockPanel, floatPanel, togglePanel, setActiveInRegion, setRegionSize, setCornerSize, moveFloat } = useUi()
  const rootRef = useRef(null)
  const [drag, setDrag] = useState(null) // only for region/corner resizes
  const menuRef = useRef({ openFor: null, x: 0, y: 0 })
  const [menuSignal, setMenuSignal] = useState(0)
  const [snapRegion, setSnapRegion] = useState(null)
  const [snapActive, setSnapActive] = useState(false)

  const showDockMenu = (id, ev) => {
    const rect = ev?.currentTarget?.getBoundingClientRect()
    if (rect) menuRef.current = { openFor: id, x: rect.left, y: rect.bottom }
    else menuRef.current = { openFor: id, x: 40, y: 40 }
    setMenuSignal(x => x + 1)
  }

  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') { setDrag(null); setDockPreview(null) } }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  const bounds = () => (rootRef.current ? rootRef.current.getBoundingClientRect() : { left:0, top:0, right:0, bottom:0, width:0, height:0 })

  const chooseRegion = (clientX, clientY) => {
    const b = bounds()
    const x = clientX - b.left
    const y = clientY - b.top
    const thresh = 32
    const nearLeft = x < thresh
    const nearRight = x > b.width - thresh
    const nearTop = y < thresh
    const nearBottom = y > b.height - 56 // leave space for bottom zoom and toolbar
    if (nearLeft && nearTop) return 'lt'
    if (nearRight && nearTop) return 'rt'
    if (nearLeft && nearBottom) return 'lb'
    if (nearRight && nearBottom) return 'rb'
    if (nearLeft) return 'left'
    if (nearRight) return 'right'
    if (nearTop) return 'top'
    if (nearBottom) return 'bottom'
    return null
  }

  const onMouseMove = (e) => {
    if (!drag) return
    if (drag.type === 'region-resize') {
      if (drag.axis === 'xy') {
        drag.apply && drag.apply(e.clientX, e.clientY)
      } else {
        const delta = drag.axis === 'x' ? (e.clientX - drag.startX) : (e.clientY - drag.startY)
        drag.apply && drag.apply(delta)
      }
    } else if (drag.type === 'dock-float') {
      const dist = Math.hypot(e.clientX - drag.startX, e.clientY - drag.startY)
      const p = layout.panels[drag.id]
      const b = bounds()
      if (!drag.started && dist > 5) {
        // convert to floating and start moving
        // initial size from panel defaults
        const w = p.w || 320, h = p.h || 260
        const x = Math.max(8, e.clientX - b.left - w/2)
        const y = Math.max(64, e.clientY - b.top - 20)
        // set to float and position
        // We defer to context helper via window.requestAnimationFrame to ensure order
        // but here directly call helpers exposed above
        floatPanel(drag.id)
        moveFloat && moveFloat(drag.id, x, y)
        setSnapActive(true)
        setSnapRegion(chooseRegion(e.clientX, e.clientY))
        drag.started = true
      } else if (drag.started) {
        const w = p.w || 320
        const x = Math.max(8, e.clientX - b.left - w/2)
        const y = Math.max(64, e.clientY - b.top - 20)
        moveFloat && moveFloat(drag.id, x, y)
        setSnapRegion(chooseRegion(e.clientX, e.clientY))
      }
    }
  }
  const onMouseUp = (e) => {
    if (!drag) return
    if (drag.type === 'dock-float' && drag.started) {
      const region = chooseRegion(e.clientX, e.clientY)
      if (region) dockPanel(drag.id, region)
    }
    setDrag(null)
    setSnapActive(false)
    setSnapRegion(null)
  }

  // region containers
  const regionStacks = layout.stacks
  const sizes = layout.sizes

  const regionBox = (region, style) => {
    const ids = regionStacks[region] || []
    if (!ids.length) return null
    const activeId = layout.active[region] || ids[0]
    const panel = layout.panels[activeId]
    const title = panel?.title || activeId
    return (
      <div key={`region-${region}`} className="absolute bg-white border shadow-md rounded overflow-hidden" style={style}>
        <div
          className="flex items-center gap-1 border-b bg-gray-100 px-1 py-1"
          onMouseDown={(e) => {
            // start drag-from-docked only when not clicking a button/tab
            if (e.target.closest('button')) return
            const sx = e.clientX, sy = e.clientY
            setDrag({ type: 'dock-float', id: activeId, startX: sx, startY: sy, started: false })
          }}
        >
          <div className="flex-1 flex flex-wrap gap-1">
            {ids.map(id => (
              <button key={id} className={`text-xs px-2 py-0.5 rounded ${activeId===id? 'bg-white border shadow-sm':'bg-gray-200 hover:bg-gray-300'}`} onClick={() => setActiveInRegion(region, id)}>{layout.panels[id]?.title || id}</button>
            ))}
          </div>
          <button title="Float" className="text-[10px] bg-gray-200 hover:bg-gray-300 rounded px-1" onClick={() => floatPanel(activeId)}>Float</button>
          <button title="Close" className="text-[10px] bg-gray-200 hover:bg-gray-300 rounded px-1" onClick={() => togglePanel(activeId)}>×</button>
        </div>
        <div className="relative" style={{ width: '100%', height: 'calc(100% - 28px)' }}>
          {panels[activeId]?.render?.() || null}
          {/* region resize handles */}
          {['left','right'].includes(region) && (
            <div
              className="absolute top-0 bottom-0 w-1 cursor-col-resize bg-transparent"
              style={{ [region==='left'?'right':'left']: 0 }}
              onMouseDown={(e) => {
                e.preventDefault(); e.stopPropagation()
                const start = e.clientX
                const initial = sizes[region]
                setDrag({ type: 'region-resize', axis: 'x', startX: start, startY: 0, apply: (delta) => setRegionSize(region, initial + (region==='left'? delta : -delta)) })
              }}
            />
          )}
          {['top','bottom'].includes(region) && (
            <div
              className="absolute left-0 right-0 h-1 cursor-row-resize bg-transparent"
              style={{ [region==='top'?'bottom':'top']: 0 }}
              onMouseDown={(e) => {
                e.preventDefault(); e.stopPropagation()
                const start = e.clientY
                const initial = sizes[region]
                setDrag({ type: 'region-resize', axis: 'y', startX: 0, startY: start, apply: (delta) => setRegionSize(region, initial + (region==='top'? delta : -delta)) })
              }}
            />
          )}
        </div>
      </div>
    )
  }

  const cornerBox = (corner, style) => {
    const ids = regionStacks[corner] || []
    if (!ids.length) return null
    const activeId = layout.active[corner] || ids[0]
    const title = layout.panels[activeId]?.title || activeId
    return (
      <div key={`corner-${corner}`} className="absolute bg-white border shadow-md rounded overflow-hidden" style={style}>
        <div
          className="flex items-center gap-1 border-b bg-gray-100 px-1 py-1"
          onMouseDown={(e) => {
            if (e.target.closest('button')) return
            const sx = e.clientX, sy = e.clientY
            setDrag({ type: 'dock-float', id: activeId, startX: sx, startY: sy, started: false })
          }}
        >
          <div className="flex-1 flex flex-wrap gap-1">
            {ids.map(id => (
              <button key={id} className={`text-xs px-2 py-0.5 rounded ${activeId===id? 'bg-white border shadow-sm':'bg-gray-200 hover:bg-gray-300'}`} onClick={() => setActiveInRegion(corner, id)}>{layout.panels[id]?.title || id}</button>
            ))}
          </div>
          <button title="Float" className="text-[10px] bg-gray-200 hover:bg-gray-300 rounded px-1" onClick={() => floatPanel(activeId)}>Float</button>
          <button title="Close" className="text-[10px] bg-gray-200 hover:bg-gray-300 rounded px-1" onClick={() => togglePanel(activeId)}>×</button>
        </div>
        <div className="relative" style={{ width: '100%', height: 'calc(100% - 28px)' }}>
          {panels[activeId]?.render?.() || null}
          {/* resize bottom-right of the corner box */}
          <div
            className="absolute right-0 bottom-0 w-2 h-2 cursor-nwse-resize"
            onMouseDown={(e) => {
              e.preventDefault(); e.stopPropagation()
              const [iw, ih] = layout.sizes.corners[corner]
              const sx = e.clientX, sy = e.clientY
              setDrag({ type: 'region-resize', axis: 'xy', startX: sx, startY: sy, apply: (cx, cy) => {
                const dx = cx - sx, dy = cy - sy
                setCornerSize(corner, iw + (corner.includes('r')? dx : -dx), ih + (corner.includes('b')? dy : -dy))
              }})
            }}
          />
        </div>
      </div>
    )
  }

  const floatingPanels = Object.values(layout.panels).filter(p => p.open && p.state === 'float')
  const zOrder = (layout.fstack || []).filter(id => floatingPanels.find(p => p.id === id))

  return (
    <div ref={rootRef} className="absolute inset-0 pointer-events-none">
      {/* Dock regions */}
      {/* Left */}
      {regionBox('left', { left: 0, top: 0, bottom: 0, width: sizes.left, marginTop: 56, marginBottom: 56, pointerEvents: 'auto' })}
      {/* Right */}
      {regionBox('right', { right: 0, top: 0, bottom: 0, width: sizes.right, marginTop: 56, marginBottom: 56, pointerEvents: 'auto' })}
      {/* Top */}
      {regionBox('top', { left: 0, right: 0, top: 0, height: sizes.top, marginTop: 56, pointerEvents: 'auto' })}
      {/* Bottom (avoid zoom center overlap by reserving middle 280px) */}
      {regionBox('bottom', { left: 0, right: 0, bottom: 0, height: sizes.bottom, marginBottom: 60, pointerEvents: 'auto' })}

      {/* Corners */}
      {cornerBox('lt', { left: 8, top: 64, width: sizes.corners.lt[0], height: sizes.corners.lt[1], pointerEvents: 'auto' })}
      {cornerBox('rt', { right: 8, top: 64, width: sizes.corners.rt[0], height: sizes.corners.rt[1], pointerEvents: 'auto' })}
      {cornerBox('lb', { left: 8, bottom: 68, width: sizes.corners.lb[0], height: sizes.corners.lb[1], pointerEvents: 'auto' })}
      {cornerBox('rb', { right: 8, bottom: 68, width: sizes.corners.rb[0], height: sizes.corners.rb[1], pointerEvents: 'auto' })}

      {/* Floating panels */}
      {floatingPanels.map(fp => {
        const idx = Math.max(0, (zOrder.indexOf(fp.id)))
        const z = 100 + idx
        return (
          <FloatingPanel
            key={fp.id}
            fp={{ ...fp, title: layout.panels[fp.id]?.title || fp.title }}
            render={panels[fp.id]?.render}
            chooseRegion={chooseRegion}
            showDockMenu={showDockMenu}
            zIndex={z}
            onSnapChange={(r) => setSnapRegion(r)}
            onSnapActive={(v) => setSnapActive(!!v)}
            getBounds={bounds}
          />
        )
      })}

      {/* Snap targets overlay */}
      {snapActive && (
        <div className="absolute inset-0 pointer-events-none">
          {/* base targets */}
          {/* left/right */}
          <div className={`absolute bg-blue-400/5 border ${snapRegion==='left'?'border-blue-400 bg-blue-400/15':'border-transparent'}`} style={{ left: 0, top: 56, bottom: 56, width: sizes.left }} />
          <div className={`absolute bg-blue-400/5 border ${snapRegion==='right'?'border-blue-400 bg-blue-400/15':'border-transparent'}`} style={{ right: 0, top: 56, bottom: 56, width: sizes.right }} />
          {/* top/bottom */}
          <div className={`absolute bg-blue-400/5 border ${snapRegion==='top'?'border-blue-400 bg-blue-400/15':'border-transparent'}`} style={{ left: 0, right: 0, top: 56, height: sizes.top }} />
          <div className={`absolute bg-blue-400/5 border ${snapRegion==='bottom'?'border-blue-400 bg-blue-400/15':'border-transparent'}`} style={{ left: 0, right: 0, bottom: 60, height: sizes.bottom }} />
          {/* corners */}
          <div className={`absolute bg-blue-400/5 border ${snapRegion==='lt'?'border-blue-400 bg-blue-400/15':'border-transparent'}`} style={{ left: 8, top: 64, width: sizes.corners.lt[0], height: sizes.corners.lt[1] }} />
          <div className={`absolute bg-blue-400/5 border ${snapRegion==='rt'?'border-blue-400 bg-blue-400/15':'border-transparent'}`} style={{ right: 8, top: 64, width: sizes.corners.rt[0], height: sizes.corners.rt[1] }} />
          <div className={`absolute bg-blue-400/5 border ${snapRegion==='lb'?'border-blue-400 bg-blue-400/15':'border-transparent'}`} style={{ left: 8, bottom: 68, width: sizes.corners.lb[0], height: sizes.corners.lb[1] }} />
          <div className={`absolute bg-blue-400/5 border ${snapRegion==='rb'?'border-blue-400 bg-blue-400/15':'border-transparent'}`} style={{ right: 8, bottom: 68, width: sizes.corners.rb[0], height: sizes.corners.rb[1] }} />
        </div>
      )}

      {/* Invisible mouse capture for region/corner resize */}
      <div className="absolute inset-0" style={{ pointerEvents: drag? 'auto':'none' }} onMouseMove={onMouseMove} onMouseUp={onMouseUp} />

      {/* Dock menu popover */}
      {menuRef.current.openFor && (
        <div className="fixed bg-white border rounded shadow-lg text-sm" style={{ left: menuRef.current.x, top: menuRef.current.y, zIndex: 50 }}>
          {['left','right','top','bottom','lt','rt','lb','rb'].map(r => (
            <button key={r} className="block w-full text-left px-3 py-1 hover:bg-gray-100" onClick={() => { dockPanel(menuRef.current.openFor, r); menuRef.current.openFor=null; setMenuSignal(x=>x+1) }}>Dock {r.toUpperCase()}</button>
          ))}
          <button className="block w-full text-left px-3 py-1 hover:bg-gray-100" onClick={() => { floatPanel(menuRef.current.openFor); menuRef.current.openFor=null; setMenuSignal(x=>x+1) }}>Float</button>
        </div>
      )}
    </div>
  )
}


