import React, { useEffect, useRef, useState } from 'react'
import { ModelProvider, useModel } from './context/ModelContext.jsx'
import Canvas from './components/Canvas.jsx'
import LeftSidebar from './components/LeftSidebar.jsx'
import RightSidebar from './components/RightSidebar.jsx'
import { CalculatorModal, PivotModal, SimulationModal } from './components/Modals.jsx'

function AppShell() {
  const { clearAll, exportModel, importModel, selectedId, removeComponent, selectedConnectionId, disconnect } = useModel()
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
        } else if (selectedId) {
          removeComponent(selectedId)
        }
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [selectedId, selectedConnectionId, disconnect, removeComponent])

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
            <button className="bg-red-500 hover:bg-red-600 text-white text-sm px-3 py-1.5 rounded" onClick={clearAll}>Clear</button>
            <button className="bg-green-600 hover:bg-green-700 text-white text-sm px-3 py-1.5 rounded" onClick={() => setSimOpen(true)}>Run Simulation</button>
          </div>
        </div>
      </header>
      <div className="flex flex-1 overflow-hidden">
        <LeftSidebar />
        <Canvas onOpenPivot={(c) => { setPivotComp(c); setPivotOpen(true) }} onOpenCalc={(c) => { setCalcComp(c); setCalcOpen(true) }} />
        <RightSidebar onOpenPivot={(c) => { setPivotComp(c); setPivotOpen(true) }} onOpenCalc={(c) => { setCalcComp(c); setCalcOpen(true) }} />
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
      <AppShell />
    </ModelProvider>
  )
}
