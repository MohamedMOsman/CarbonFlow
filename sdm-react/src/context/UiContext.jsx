import React, { createContext, useContext, useEffect, useMemo, useRef, useState } from 'react'

// Layout model (kept dependency-free):
// layout = {
//   panels: {
//     [id]: { id, title, open, state: 'docked'|'float', region: 'left'|'right'|'top'|'bottom'|'lt'|'rt'|'lb'|'rb'|null, x,y,w,h }
//   },
//   stacks: { left:string[], right:string[], top:string[], bottom:string[], lt:string[], rt:string[], lb:string[], rb:string[] },
//   active: { [region]: string|null },
//   sizes: { left:number, right:number, top:number, bottom:number, corners: { lt:[number,number], rt:[number,number], lb:[number,number], rb:[number,number] } }
// }

const STORAGE_KEY = 'sdm-react-ui-v1'

const defaultLayout = () => ({
  panels: {
    scenarios: { id: 'scenarios', title: 'Scenarios', open: true, state: 'docked', region: 'left', x: 40, y: 100, w: 320, h: 360 },
    systems: { id: 'systems', title: 'Systems', open: true, state: 'docked', region: 'left', x: 80, y: 160, w: 360, h: 420 },
    globals: { id: 'globals', title: 'Global Components', open: true, state: 'docked', region: 'left', x: 120, y: 220, w: 360, h: 420 },
    dimensions: { id: 'dimensions', title: 'Dimensions', open: true, state: 'docked', region: 'left', x: 160, y: 280, w: 300, h: 260 },
  },
  stacks: {
    left: ['scenarios','systems','globals','dimensions'], right: [], top: [], bottom: [], lt: [], rt: [], lb: [], rb: []
  },
  active: { left: 'systems', right: null, top: null, bottom: null, lt: null, rt: null, lb: null, rb: null },
  sizes: { left: 320, right: 320, top: 240, bottom: 240, corners: { lt: [320,260], rt: [320,260], lb: [320,260], rb: [320,260] } },
  fstack: [] // floating z-order back->front
})

function clamp(n, min, max) { return Math.max(min, Math.min(max, n)) }

const UiContext = createContext(null)

export function UiProvider({ children }) {
  const [layout, setLayout] = useState(() => {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || defaultLayout() } catch { return defaultLayout() }
  })
  const rafRef = useRef(0)

  // persist with rAF to avoid heavy writes
  useEffect(() => {
    cancelAnimationFrame(rafRef.current)
    rafRef.current = requestAnimationFrame(() => {
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(layout)) } catch {}
    })
  }, [layout])

  // allow ModelContext import to restore layout via event
  useEffect(() => {
    const onImported = () => {
      try {
        const raw = localStorage.getItem(STORAGE_KEY)
        if (!raw) return
        const parsed = JSON.parse(raw)
        if (parsed && parsed.panels) setLayout(parsed)
      } catch {}
    }
    window.addEventListener('ui-layout-updated', onImported)
    return () => window.removeEventListener('ui-layout-updated', onImported)
  }, [])

  // helpers
  const showPanel = (id, show=true) => setLayout(l => {
    const p = l.panels[id]
    if (!p) return l
    const stacks = { ...l.stacks }
    let next = { ...l }
    if (!show) {
      // remove from any region stack
      Object.keys(stacks).forEach(r => { stacks[r] = stacks[r].filter(x => x !== id) })
      next = { ...l, stacks, active: { ...l.active } }
      Object.keys(next.active).forEach(r => { if (next.active[r] === id) next.active[r] = stacks[r][0] || null })
    } else {
      // restore into its region or left by default
      const target = p.region || 'left'
      Object.keys(stacks).forEach(r => { stacks[r] = stacks[r].filter(x => x !== id) })
      stacks[target] = [...(stacks[target]||[]), id]
      next = { ...l, stacks, active: { ...l.active, [target]: id } }
    }
    return { ...next, panels: { ...next.panels, [id]: { ...p, open: !!show } } }
  })
  const togglePanel = (id) => setLayout(l => {
    const open = !l.panels[id]?.open
    return showPanelInner(l, id, open)
  })

  // helper so toggle can reuse showPanel behavior without double setState
  function showPanelInner(state, id, show) {
    const p = state.panels[id]
    if (!p) return state
    const stacks = { ...state.stacks }
    let next = { ...state }
    if (!show) {
      Object.keys(stacks).forEach(r => { stacks[r] = stacks[r].filter(x => x !== id) })
      next = { ...state, stacks, active: { ...state.active } }
      Object.keys(next.active).forEach(r => { if (next.active[r] === id) next.active[r] = stacks[r][0] || null })
    } else {
      const target = p.region || 'left'
      Object.keys(stacks).forEach(r => { stacks[r] = stacks[r].filter(x => x !== id) })
      stacks[target] = [...(stacks[target]||[]), id]
      next = { ...state, stacks, active: { ...state.active, [target]: id } }
    }
    return { ...next, panels: { ...next.panels, [id]: { ...p, open: !!show } } }
  }

  const setActiveInRegion = (region, id) => setLayout(l => ({ ...l, active: { ...l.active, [region]: id } }))

  const resetLayout = () => setLayout(defaultLayout())

  const floatPanel = (id) => setLayout(l => {
    const p = l.panels[id]
    if (!p) return l
    // remove from region stack if present
    const stacks = { ...l.stacks }
    const prevRegion = p.region
    if (prevRegion && stacks[prevRegion]) stacks[prevRegion] = stacks[prevRegion].filter(x => x !== id)
    const fstack = (l.fstack||[]).filter(x => x !== id).concat(id)
    return { ...l, panels: { ...l.panels, [id]: { ...p, state: 'float', region: null, max: false } }, stacks, fstack }
  })

  const dockPanel = (id, region) => setLayout(l => {
    const stacks = { ...l.stacks }
    // remove from any current region
    Object.keys(stacks).forEach(r => { stacks[r] = stacks[r].filter(x => x !== id) })
    stacks[region] = [...(stacks[region]||[]), id]
    const fstack = (l.fstack||[]).filter(x => x !== id)
    return { ...l, panels: { ...l.panels, [id]: { ...l.panels[id], state: 'docked', region } }, stacks, active: { ...l.active, [region]: id }, fstack }
  })

  const moveFloat = (id, x, y) => setLayout(l => {
    const p = l.panels[id]
    if (!p || p.max) return l
    return { ...l, panels: { ...l.panels, [id]: { ...p, x, y } } }
  })
  const resizeFloat = (id, w, h) => setLayout(l => {
    const p = l.panels[id]
    if (!p || p.max) return l
    return { ...l, panels: { ...l.panels, [id]: { ...p, w: clamp(w, 220, 900), h: clamp(h, 160, 800) } } }
  })

  const setRegionSize = (region, size) => setLayout(l => ({ ...l, sizes: { ...l.sizes, [region]: clamp(size, 200, region==='top'||region==='bottom' ? 480 : 540) } }))
  const setCornerSize = (corner, w, h) => setLayout(l => ({ ...l, sizes: { ...l.sizes, corners: { ...l.sizes.corners, [corner]: [clamp(w,200,640), clamp(h,160,480)] } } }))

  const bringToFront = (id) => setLayout(l => ({ ...l, fstack: (l.fstack||[]).filter(x => x !== id).concat(id) }))

  const toggleMaximize = (id) => setLayout(l => {
    const p = l.panels[id]
    if (!p || p.state !== 'float') return l
    if (p.max) {
      const nx = (typeof p.prevX === 'number') ? p.prevX : p.x
      const ny = (typeof p.prevY === 'number') ? p.prevY : p.y
      const nw = (typeof p.prevW === 'number') ? p.prevW : p.w
      const nh = (typeof p.prevH === 'number') ? p.prevH : p.h
      return { ...l, panels: { ...l.panels, [id]: { ...p, max: false, x: nx, y: ny, w: nw, h: nh } } }
    }
    return { ...l, panels: { ...l.panels, [id]: { ...p, max: true, prevX: p.x, prevY: p.y, prevW: p.w, prevH: p.h } } }
  })

  const value = useMemo(() => ({
    layout, setLayout,
    showPanel, togglePanel, resetLayout,
    floatPanel, dockPanel, moveFloat, resizeFloat,
    setRegionSize, setCornerSize, setActiveInRegion,
    bringToFront, toggleMaximize,
    STORAGE_KEY
  }), [layout])

  return <UiContext.Provider value={value}>{children}</UiContext.Provider>
}

export function useUi() {
  const ctx = useContext(UiContext)
  if (!ctx) throw new Error('useUi must be used within UiProvider')
  return ctx
}
