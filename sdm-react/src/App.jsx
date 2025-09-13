import React, { useEffect, useRef, useState } from 'react'
import { ModelProvider, useModel } from './context/ModelContext.jsx'
import Canvas from './components/Canvas.jsx'
// import LeftSidebar from './components/LeftSidebar.jsx'
import RightSidebar from './components/RightSidebar.jsx'
import { CalculatorModal, PivotModal, SimulationModal } from './components/Modals.jsx'
import WindowManager from './components/WindowManager.jsx'
import { UiProvider, useUi } from './context/UiContext.jsx'
import ScenariosPanel from './components/panels/ScenariosPanel.jsx'
import SystemsPanel from './components/panels/SystemsPanel.jsx'
import GlobalComponentsPanel from './components/panels/GlobalComponentsPanel.jsx'
import DimensionsPanel from './components/panels/DimensionsPanel.jsx'

function WindowsMenu() {
  const { layout, togglePanel, resetLayout } = useUi()
  const [open, setOpen] = React.useState(false)
  const items = [
    { id: 'scenarios', title: 'Scenarios' },
    { id: 'systems', title: 'Systems' },
    { id: 'globals', title: 'Global Components' },
    { id: 'dimensions', title: 'Dimensions' },
  ]
  return (
    <div className="relative">
      <button className="bg-gray-200 text-gray-800 text-sm px-3 py-1.5 rounded" onClick={() => setOpen(o => !o)}>Windows</button>
      {open && (
        <div className="absolute right-0 mt-2 w-56 bg-white border rounded shadow-lg p-2 z-50">
          <div className="text-xs text-gray-500 px-1 pb-1">Panels</div>
          {items.map(it => (
            <label key={it.id} className="flex items-center gap-2 px-1 py-1 hover:bg-gray-50 rounded cursor-pointer">
              <input type="checkbox" checked={!!layout.panels[it.id]?.open} onChange={() => togglePanel(it.id)} />
              <span className="text-sm">{it.title}</span>
            </label>
          ))}
          <div className="border-t my-2"></div>
          <button className="w-full text-left text-sm px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded" onClick={() => { resetLayout(); setOpen(false) }}>Reset layout</button>
        </div>
      )}
    </div>
  )
}

function AppShell() {
  const { clearAll, exportModel, importModel, selectedId, selectedIds, removeComponent, removeComponents, selectedConnectionId, disconnect } = useModel()
  const [simOpen, setSimOpen] = useState(false)
  const [pivotOpen, setPivotOpen] = useState(false)
  const [calcOpen, setCalcOpen] = useState(false)
  const [pivotComp, setPivotComp] = useState(null)
  const [calcComp, setCalcComp] = useState(null)
  const fileRef = useRef(null)

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (selectedConnectionId) {
          disconnect(selectedConnectionId)
        } else if (Array.isArray(selectedIds) && selectedIds.length > 1) {
          removeComponents(selectedIds)
        } else if (selectedId) {
          removeComponent(selectedId)
        }
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [selectedId, selectedIds, selectedConnectionId, disconnect, removeComponent, removeComponents])

  return (
    <div className="h-screen flex flex-col">
      <header className="bg-white shadow z-10">
        <div className="container mx-auto px-4 py-3 flex justify-between items-center">
          <h1 className="text-lg font-bold text-gray-700">System Dynamics Modeler (React)</h1>
          <div className="flex gap-2">
            <button className="bg-gray-200 text-gray-800 text-sm px-3 py-1.5 rounded" onClick={() => {
              const text = exportModel()
              const blob = new Blob([text], { type: 'application/json' })
              const a = document.createElement('a')
              a.href = URL.createObjectURL(blob)
              a.download = 'model.json'
              a.click()
              URL.revokeObjectURL(a.href)
            }}>Export</button>
            <button className="bg-gray-200 text-gray-800 text-sm px-3 py-1.5 rounded" onClick={() => fileRef.current?.click()}>Import</button>
            <input ref={fileRef} type="file" accept="application/json,.json" className="hidden" onChange={e => {
              const file = e.target.files?.[0]
              if (!file) return
              const reader = new FileReader()
              reader.onload = () => { importModel(String(reader.result||'')) }
              reader.readAsText(file)
              e.target.value = ''
            }} />
            <button className="bg-red-500 hover:bg-red-600 text-white text-sm px-3 py-1.5 rounded" title="Delete selected components" onClick={() => { if (selectedIds?.length) removeComponents(selectedIds) }}>Clear</button>
            <button className="bg-red-600 hover:bg-red-700 text-white text-sm px-3 py-1.5 rounded" title="Clear all components, systems, scenarios" onClick={clearAll}>Clear All</button>
            <button className="bg-green-600 hover:bg-green-700 text-white text-sm px-3 py-1.5 rounded" onClick={() => setSimOpen(true)}>Run Simulation</button>
            <WindowsMenu />
          </div>
        </div>
      </header>
      <div className="relative flex flex-1 overflow-hidden">
        {/* Center canvas */}
        <Canvas onOpenPivot={(c) => { setPivotComp(c); setPivotOpen(true) }} onOpenCalc={(c) => { setCalcComp(c); setCalcOpen(true) }} />
        {/* Right properties sidebar unchanged */}
        <RightSidebar onOpenPivot={(c) => { setPivotComp(c); setPivotOpen(true) }} onOpenCalc={(c) => { setCalcComp(c); setCalcOpen(true) }} />
        {/* Window manager overlay */}
        <WindowManager panels={{
          scenarios: { title: 'Scenarios', render: () => <ScenariosPanel /> },
          systems: { title: 'Systems', render: () => <SystemsPanel /> },
          globals: { title: 'Global Components', render: () => <GlobalComponentsPanel /> },
          dimensions: { title: 'Dimensions', render: () => <DimensionsPanel /> },
        }} />
      </div>

      <SimulationModal open={simOpen} onClose={() => setSimOpen(false)} />
      <PivotModal open={pivotOpen} onClose={() => setPivotOpen(false)} component={pivotComp} />
      <CalculatorModal open={calcOpen} onClose={() => setCalcOpen(false)} component={calcComp} />
    </div>
  )
}

export default function App() {
  return (
    <ModelProvider>
      <UiProvider>
        <AppShell />
      </UiProvider>
    </ModelProvider>
  )
}
