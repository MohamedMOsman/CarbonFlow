import React, { createContext, useContext, useMemo, useState, useCallback } from 'react'

// Types (informal):
// Component: { id, name, type, x, y, w, h, data, overrides: { [scenarioId]: any }, systemId?, originalId? }
// Connection: { id, fromId, toId }
// System: { id, name, parentId: number|null, componentIds: number[], isExpanded?: boolean }
// Scenario: { id, name, parentId: number|null, isExpanded?: boolean }

const ModelContext = createContext(null)

let idCounter = 1
const genId = () => idCounter++

export function ModelProvider({ children }) {
  const [systems, setSystems] = useState([])
  const [components, setComponents] = useState([])
  const [connections, setConnections] = useState([])
  const [scenarios, setScenarios] = useState([{ id: 1, name: 'Base', parentId: null, isExpanded: true }])
  const [activeScenarioId, setActiveScenarioId] = useState(1)
  const [selectedId, setSelectedId] = useState(null)
  const [selectedConnectionId, setSelectedConnectionId] = useState(null)
  const [activeSystemId, setActiveSystemId] = useState(null)

  // --- File System Access API integration ---
  const [outputDirHandle, setOutputDirHandle] = useState(null)

  const isFsSupported = typeof window !== 'undefined' && 'showDirectoryPicker' in window

  const sanitizeName = useCallback((name) => {
    try {
      return String(name).replace(/[<>:"/\\|?*]/g, '').replace(/\s+/g, ' ').trim()
    } catch {
      return 'Unnamed'
    }
  }, [])

  const nextNumberedName = useCallback((prefix, existingNames) => {
    const re = new RegExp(`^${prefix}\\s+(\\d+)$`, 'i')
    let maxN = 0
    for (const n of existingNames) {
      const m = String(n || '').match(re)
      if (m) {
        const v = parseInt(m[1], 10)
        if (!Number.isNaN(v)) maxN = Math.max(maxN, v)
      }
    }
    return `${prefix} ${maxN + 1}`
  }, [])

  const chooseOutputDir = useCallback(async () => {
    if (!isFsSupported) {
      alert('File System Access API is not supported in this browser.')
      return null
    }
    try {
      const handle = await window.showDirectoryPicker({ id: 'sdm-output' })
      // ensure we have permission
      if (handle.requestPermission) {
        const perm = await handle.requestPermission({ mode: 'readwrite' })
        if (perm !== 'granted') {
          alert('Permission to write to the selected folder was not granted.')
          return null
        }
      }
      setOutputDirHandle(handle)
      return handle
    } catch (e) {
      console.error('chooseOutputDir failed', e)
      return null
    }
  }, [isFsSupported])

  const getSystemLineage = useCallback((systemId) => {
    const byId = new Map(systems.map(s => [s.id, s]))
    const arr = []
    let cur = byId.get(systemId)
    while (cur) { arr.push(cur); cur = byId.get(cur.parentId) }
    return arr.reverse() // root -> leaf
  }, [systems])

  const ensureSystemDir = useCallback(async (systemId) => {
    if (!outputDirHandle) return null
    try {
      let dir = outputDirHandle
      const lineage = getSystemLineage(systemId)
      for (const sys of lineage) {
        const folderName = sanitizeName(sys.name || `System-${sys.id}`)
        dir = await dir.getDirectoryHandle(folderName, { create: true })
      }
      return dir
    } catch (e) {
      console.error('ensureSystemDir failed', e)
      return null
    }
  }, [outputDirHandle, getSystemLineage, sanitizeName])

  const writeComponentJson = useCallback(async (comp) => {
    if (!outputDirHandle) return false
    try {
      const dir = await ensureSystemDir(comp.systemId)
      if (!dir) return false
      const fileName = `${sanitizeName(comp.name || `Component-${comp.id}`)}__${comp.id}.json`
      const fileHandle = await dir.getFileHandle(fileName, { create: true })
      const writable = await fileHandle.createWritable()
      const payload = {
        id: comp.id,
        name: comp.name,
        type: comp.type,
        data: comp.data || {},
        overrides: comp.overrides || {},
        position: { x: comp.x, y: comp.y, w: comp.w, h: comp.h },
      }
      await writable.write(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }))
      await writable.close()
      return true
    } catch (e) {
      console.error('writeComponentJson failed', e)
      return false
    }
  }, [outputDirHandle, ensureSystemDir, sanitizeName])

  const syncSystemToDisk = useCallback(async (systemId) => {
    if (!outputDirHandle) return false
    try {
      await ensureSystemDir(systemId)
      const comps = components.filter(c => c.systemId === systemId)
      for (const c of comps) { // sequential to avoid permission prompts flapping
        // skip references; nothing to persist
        if (c.type === 'Reference') continue
        // eslint-disable-next-line no-await-in-loop
        await writeComponentJson(c)
      }
      return true
    } catch (e) {
      console.error('syncSystemToDisk failed', e)
      return false
    }
  }, [outputDirHandle, components, ensureSystemDir, writeComponentJson])

  const syncAllToDisk = useCallback(async () => {
    if (!outputDirHandle) {
      const h = await chooseOutputDir()
      if (!h) return false
    }
    try {
      const rootSystems = systems.filter(s => s.parentId === null)
      const allSystems = []
      const collect = (sys) => { allSystems.push(sys); systems.filter(s => s.parentId === sys.id).forEach(collect) }
      rootSystems.forEach(collect)
      for (const s of allSystems) { // sequential
        // eslint-disable-next-line no-await-in-loop
        await syncSystemToDisk(s.id)
      }
      return true
    } catch (e) {
      console.error('syncAllToDisk failed', e)
      return false
    }
  }, [systems, outputDirHandle, chooseOutputDir, syncSystemToDisk])

  const addSystem = useCallback((name = null, parentId = null) => {
    const isAuto = !name || /^(new\s*system)$/i.test(name) || /^system\s+\d+$/i.test(name)
    const finalName = isAuto ? nextNumberedName('System', systems.map(s => s.name)) : name
    const sys = { id: genId(), name: finalName, parentId, componentIds: [], isExpanded: true }
    setSystems(s => [...s, sys])
    if (activeSystemId == null) setActiveSystemId(sys.id)
    // fire-and-forget create folder on disk
    if (outputDirHandle) {
      // Create folder for the new system immediately using its parent lineage
      (async () => {
        try {
          let dir = outputDirHandle
          const lineage = parentId ? getSystemLineage(parentId) : []
          for (const s of lineage) {
            const folderName = sanitizeName(s.name || `System-${s.id}`)
            // eslint-disable-next-line no-await-in-loop
            dir = await dir.getDirectoryHandle(folderName, { create: true })
          }
          const thisFolder = sanitizeName(sys.name || `System-${sys.id}`)
          await dir.getDirectoryHandle(thisFolder, { create: true })
        } catch (e) {
          console.error('create system folder failed', e)
        }
      })()
    }
    return sys.id
  }, [systems, activeSystemId, outputDirHandle, getSystemLineage, sanitizeName, nextNumberedName])

  const renameSystem = useCallback((id, name) => {
    setSystems(ss => ss.map(s => s.id === id ? { ...s, name } : s))
  }, [])

  const toggleSystem = useCallback((id) => {
    setSystems(ss => ss.map(s => s.id === id ? { ...s, isExpanded: !s.isExpanded } : s))
  }, [])

  const deleteSystem = useCallback((id) => {
    const collect = (rootId, arr=[]) => {
      arr.push(rootId)
      systems.filter(s => s.parentId === rootId).forEach(ch => collect(ch.id, arr))
      return arr
    }
    const toDelete = collect(id, [])
    const toDeleteSet = new Set(toDelete)
    setSystems(ss => ss.filter(s => !toDelete.includes(s.id)))
    setComponents(cs => cs.filter(c => !toDelete.includes(c.systemId)))
    setConnections(cons => cons.filter(cn => {
      const fromSys = csByIdRef.current[cn.fromId]?.systemId
      const toSys = csByIdRef.current[cn.toId]?.systemId
      return !(toDeleteSet.has(fromSys) || toDeleteSet.has(toSys))
    }))
    if (toDelete.includes(activeSystemId)) setActiveSystemId(null)
    if (selectedId && components.find(c => c.id === selectedId && toDeleteSet.has(c.systemId))) setSelectedId(null)
    if (selectedConnectionId) setSelectedConnectionId(null)

    // Remove the corresponding folder from disk (recursively), if configured
    if (outputDirHandle) {
      (async () => {
        try {
          // Walk to the parent of the folder we want to remove
          const lineage = getSystemLineage(id)
          if (!lineage.length) return
          const names = lineage.map(s => sanitizeName(s.name || `System-${s.id}`))
          let parent = outputDirHandle
          for (let i = 0; i < names.length - 1; i++) {
            try {
              // eslint-disable-next-line no-await-in-loop
              parent = await parent.getDirectoryHandle(names[i], { create: false })
            } catch {
              // Parent path doesn't exist; nothing to delete
              return
            }
          }
          const targetName = names[names.length - 1]
          try {
            await parent.removeEntry(targetName, { recursive: true })
          } catch (e) {
            console.warn('Failed to remove system folder', targetName, e)
          }
        } catch (e) {
          console.error('deleteSystem: fs removal failed', e)
        }
      })()
    }
  }, [systems, components, activeSystemId, selectedId, selectedConnectionId, outputDirHandle, getSystemLineage, sanitizeName])

  const addComponent = useCallback((systemId, type = 'Stock') => {
    const comp = {
      id: genId(),
      name: `${type} ${components.length + 1}`,
      type,
      x: 200 + components.length * 10,
      y: 120 + components.length * 10,
      w: 180,
      h: 60,
      data: (['Stock','Flow','Parameter','Dataset'].includes(type)) ? { data: [['A','B','C'],['1','2','3']] } : (type === 'Calculator' ? { equation: '' } : {}),
      overrides: {},
      systemId
    }
    setComponents(cs => [...cs, comp])
    setSystems(ss => ss.map(s => s.id === systemId ? { ...s, componentIds: [...s.componentIds, comp.id] } : s))
    // write component JSON under its system folder if configured
    if (outputDirHandle && comp.type !== 'Reference') {
      writeComponentJson(comp)
    }
    return comp.id
  }, [components.length, outputDirHandle, writeComponentJson])

  const addReference = useCallback((systemId, originalId) => {
    const original = components.find(c => c.id === originalId)
    if (!original) return null
    const ref = {
      id: genId(),
      name: `Ref(${original.name})`,
      type: 'Reference',
      originalId,
      x: original.x + 50,
      y: original.y + 50,
      w: original.w,
      h: original.h,
      overrides: {},
      data: {},
      systemId,
    }
    setComponents(cs => [...cs, ref])
    setSystems(ss => ss.map(s => s.id === systemId ? { ...s, componentIds: [...s.componentIds, ref.id] } : s))
    return ref.id
  }, [components])

  const moveComponent = useCallback((id, x, y) => {
    setComponents(cs => cs.map(c => c.id === id ? { ...c, x, y } : c))
  }, [])

  const renameComponent = useCallback((id, name) => {
    setComponents(cs => cs.map(c => c.id === id ? { ...c, name } : c))
  }, [])

  const removeComponent = useCallback((id) => {
    setComponents(cs => cs.filter(c => c.id !== id))
    setConnections(cons => cons.filter(cn => cn.fromId !== id && cn.toId !== id))
    setSystems(ss => ss.map(s => ({ ...s, componentIds: s.componentIds.filter(cid => cid !== id) })))
    if (selectedId === id) setSelectedId(null)
    if (selectedConnectionId) setSelectedConnectionId(null)
  }, [selectedId])

  const connect = useCallback((fromId, toId) => {
    if (!fromId || !toId || fromId === toId) return
    const id = genId()
    setConnections(cs => [...cs, { id, fromId, toId }])
  }, [])

  const disconnect = useCallback((connId) => {
    setConnections(cs => cs.filter(c => c.id !== connId))
  }, [])

  const addScenario = useCallback((name = null , parentId = null) => {
    const isAuto = !name || /^(new\s*scenario)$/i.test(name) || /^scenario\s+\d+$/i.test(name)
    const finalName = isAuto ? nextNumberedName('Scenario', scenarios.map(s => s.name)) : name
    const sc = { id: genId(), name: finalName, parentId, isExpanded: true }
    setScenarios(ss => [...ss, sc])
    return sc.id
  }, [scenarios, nextNumberedName])

  const renameScenario = useCallback((id, name) => {
    setScenarios(ss => ss.map(s => s.id === id ? { ...s, name } : s))
  }, [])

  const toggleScenario = useCallback((id) => {
    setScenarios(ss => ss.map(s => s.id === id ? { ...s, isExpanded: !s.isExpanded } : s))
  }, [])

  const deleteScenario = useCallback((id) => {
    const collect = (rootId, arr=[]) => {
      arr.push(rootId)
      scenarios.filter(s => s.parentId === rootId).forEach(ch => collect(ch.id, arr))
      return arr
    }
    const toDelete = collect(id, [])
    setScenarios(ss => ss.filter(s => !toDelete.includes(s.id)))
    if (toDelete.includes(activeScenarioId)) setActiveScenarioId(1)
  }, [scenarios, activeScenarioId])

  const setOverride = useCallback((componentId, patch) => {
    setComponents(cs => cs.map(c => {
      if (c.id !== componentId) return c
      const curr = c.overrides[activeScenarioId] || {}
      return { ...c, overrides: { ...c.overrides, [activeScenarioId]: { ...curr, ...patch } } }
    }))
  }, [activeScenarioId])

  const saveComponentData = useCallback((componentId, key, value) => {
    setComponents(cs => cs.map(c => {
      if (c.id !== componentId) return c
      const inScenario = (activeScenarioId !== 1) || (c.type === 'Reference')
      if (inScenario) {
        const curr = c.overrides[activeScenarioId] || {}
        return { ...c, overrides: { ...c.overrides, [activeScenarioId]: { ...curr, [key]: value } } }
      }
      return { ...c, data: { ...c.data, [key]: value } }
    }))
  }, [activeScenarioId])

  const getResolvedComponent = useCallback((c, scenarioId) => {
    if (!c) return null
    if (c.type === 'Reference') {
      const original = components.find(o => o.id === c.originalId)
      return getResolvedComponent(original, scenarioId)
    }
    // Walk up scenario tree from scenarioId to root, applying overrides
    const mapById = new Map(scenarios.map(s => [s.id, s]))
    const lineage = []
    let cur = mapById.get(scenarioId)
    while (cur) { lineage.push(cur.id); cur = mapById.get(cur.parentId) }
    let merged = { ...(c.data || {}) }
    // Apply from root -> leaf for intuitive inheritance (parent first, then child overwrite)
    lineage.reverse().forEach(sid => {
      if (c.overrides && c.overrides[sid]) {
        merged = { ...merged, ...c.overrides[sid] }
      }
    })
    return { ...c, data: merged }
  }, [components, scenarios])

  const clearAll = useCallback(() => {
    setSystems([])
    setComponents([])
    setConnections([])
    setScenarios([{ id: 1, name: 'Base', parentId: null, isExpanded: true }])
    setActiveScenarioId(1)
    setSelectedId(null)
    setSelectedConnectionId(null)
    setActiveSystemId(null)
    idCounter = 1
  }, [])

  const modelForSimulation = useCallback(() => {
    const comps = components
      .filter(c => c.type !== 'Reference')
      .map(c => {
        const resolved = getResolvedComponent(c, activeScenarioId)
        return { id: c.id, name: c.name, type: c.type, data: resolved?.data || {} }
      })
    const refMap = new Map(components.filter(c => c.type === 'Reference').map(r => [r.id, r.originalId]))
    const cons = connections
      .map(cn => ({ fromId: refMap.get(cn.fromId) || cn.fromId, toId: refMap.get(cn.toId) || cn.toId }))
      .filter(cn => cn.fromId && cn.toId)
    return { components: comps, connections: cons }
  }, [components, connections, activeScenarioId, getResolvedComponent])

  // quick lookup for deleteSystem connection filtering
  const csByIdRef = React.useRef({})
  React.useEffect(() => {
    const m = {}
    components.forEach(c => { m[c.id] = c })
    csByIdRef.current = m
  }, [components])

  // --- Persistence (localStorage) ---
  const STORAGE_KEY = 'sdm-react-model-v2'

  const exportModel = useCallback(() => {
    const payload = {
      systems, components, connections, scenarios, activeScenarioId, activeSystemId,
      idCounter
    }
    return JSON.stringify(payload)
  }, [systems, components, connections, scenarios, activeScenarioId, activeSystemId])

  const importModel = useCallback((json) => {
    try {
      const data = JSON.parse(json)
      if (!data) return false
      setSystems(Array.isArray(data.systems) ? data.systems : [])
      setComponents(Array.isArray(data.components) ? data.components : [])
      setConnections(Array.isArray(data.connections) ? data.connections : [])
      setScenarios(Array.isArray(data.scenarios) && data.scenarios.length ? data.scenarios : [{ id: 1, name: 'Base', parentId: null, isExpanded: true }])
      setActiveScenarioId(Number.isInteger(data.activeScenarioId) ? data.activeScenarioId : 1)
      setActiveSystemId(Number.isInteger(data.activeSystemId) ? data.activeSystemId : null)
      setSelectedId(null)
      setSelectedConnectionId(null)
      idCounter = Number.isInteger(data.idCounter) ? data.idCounter : Math.max(1,
        ...[...((data.components||[]).map(c=>c.id)), ...((data.systems||[]).map(s=>s.id)), ...((data.connections||[]).map(c=>c.id)), ...((data.scenarios||[]).map(s=>s.id))].filter(Boolean)
      ) + 1
      return true
    } catch (e) {
      console.error('Failed to import model', e)
      return false
    }
  }, [])

  // autosave on change
  React.useEffect(() => {
    try { localStorage.setItem(STORAGE_KEY, exportModel()) } catch {}
  }, [exportModel])

  // load on mount
  React.useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) importModel(raw)
    } catch {}
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // ensure at least one root system exists
  React.useEffect(() => {
    if (!systems.length) {
      addSystem('Main', null)
    } else if (activeSystemId == null) {
      setActiveSystemId(systems[0].id)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [systems.length])

  const value = useMemo(() => ({
    systems, components, connections, scenarios, activeScenarioId, selectedId, selectedConnectionId, activeSystemId,
    setActiveScenarioId, setSelectedId, setSelectedConnectionId, setActiveSystemId,
    addSystem, renameSystem, toggleSystem, deleteSystem,
    addComponent, addReference,
    moveComponent, renameComponent, removeComponent,
    connect, disconnect,
    addScenario, renameScenario, toggleScenario, deleteScenario, setOverride, saveComponentData,
    getResolvedComponent, clearAll, modelForSimulation,
    exportModel, importModel,
    // FS helpers
    chooseOutputDir, syncAllToDisk,
    hasOutputDir: !!outputDirHandle, isFsSupported
  }), [systems, components, connections, scenarios, activeScenarioId, selectedId, selectedConnectionId, activeSystemId,
      addSystem, renameSystem, toggleSystem, deleteSystem, addComponent, addReference, moveComponent, renameComponent, removeComponent, connect, disconnect, addScenario, renameScenario, toggleScenario, deleteScenario, setOverride, saveComponentData, getResolvedComponent, clearAll, modelForSimulation, exportModel, importModel, chooseOutputDir, syncAllToDisk, outputDirHandle, isFsSupported])

  return <ModelContext.Provider value={value}>{children}</ModelContext.Provider>
}

export function useModel() {
  const ctx = useContext(ModelContext)
  if (!ctx) throw new Error('useModel must be used within ModelProvider')
  return ctx
}
