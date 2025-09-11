import React, { useEffect, useRef, useState } from 'react'
import { useModel } from '../context/ModelContext.jsx'

export function SimulationModal({ open, onClose }) {
  const { modelForSimulation } = useModel()
  const data = modelForSimulation()
  if (!open) return null
  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="bg-white rounded-lg shadow-xl w-[800px] max-w-[90vw] max-h-[80vh] overflow-hidden" onClick={e => e.stopPropagation()}>
        <div className="p-4 border-b flex items-center justify-between">
          <div className="font-semibold">Simulation Data</div>
          <button className="text-sm text-gray-500" onClick={onClose}>Close</button>
        </div>
        <pre className="p-4 text-xs overflow-auto">{JSON.stringify(data, null, 2)}</pre>
      </div>
    </div>
  )
}

export function PivotModal({ open, onClose, component }) {
  const containerRef = useRef(null)
  const tableRef = useRef(null)
  const [editable, setEditable] = useState([])
  const { saveComponentData, getResolvedComponent, activeScenarioId } = useModel()

  useEffect(() => {
    if (!open || !component) return
    const resolved = getResolvedComponent(component, activeScenarioId)
    const rows = resolved?.data?.data || []
    setEditable(rows)
    if (containerRef.current && window.$) {
      const $ = window.$
      $(containerRef.current).empty()
      $(containerRef.current).pivotUI(rows, { rendererName: 'Table' })
    }
  }, [open, component, getResolvedComponent, activeScenarioId])

  if (!open || !component) return null

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="bg-white rounded-lg shadow-xl w-[1000px] max-w-[95vw] max-h-[90vh] overflow-hidden flex flex-col" onClick={e => e.stopPropagation()}>
        <div className="p-3 border-b flex items-center justify-between">
          <div className="font-semibold">Dataset Pivot: {component.name}</div>
          <div className="flex gap-2">
            <button className="text-xs bg-blue-600 text-white px-2 py-1 rounded" onClick={() => {
              saveComponentData(component.id, 'data', editable)
              onClose()
            }}>Save</button>
            <button className="text-xs bg-gray-200 px-2 py-1 rounded" onClick={onClose}>Close</button>
          </div>
        </div>
        <div className="flex-1 grid grid-cols-2 gap-2 p-3 overflow-hidden">
          <div className="overflow-auto border rounded p-2">
            <table className="min-w-full text-xs">
              <tbody>
                {editable.map((row, ri) => (
                  <tr key={ri}>
                    {row.map((cell, ci) => (
                      <td key={ci} className="border px-1 py-0.5" contentEditable suppressContentEditableWarning onBlur={e => {
                        setEditable(prev => {
                          const copy = prev.map(r => [...r])
                          copy[ri][ci] = e.target.textContent
                          return copy
                        })
                      }}>{String(cell)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="overflow-auto border rounded p-2">
            <div ref={containerRef} />
          </div>
        </div>
      </div>
    </div>
  )
}

export function CalculatorModal({ open, onClose, component }) {
  const { saveComponentData, connections, components, getResolvedComponent, activeScenarioId } = useModel()
  const [equation, setEquation] = useState(component ? (getResolvedComponent(component, activeScenarioId)?.data?.equation || '') : '')
  useEffect(() => {
    setEquation(component ? (getResolvedComponent(component, activeScenarioId)?.data?.equation || '') : '')
  }, [component, open, getResolvedComponent, activeScenarioId])
  if (!open || !component) return null
  const inputs = connections.filter(cn => cn.toId === component.id).map(cn => components.find(c => c.id === cn.fromId)).filter(Boolean)
  const outputs = connections.filter(cn => cn.fromId === component.id).map(cn => components.find(c => c.id === cn.toId)).filter(Boolean)
  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="bg-white rounded-lg shadow-xl w-[700px] max-w-[90vw] overflow-hidden" onClick={e => e.stopPropagation()}>
        <div className="p-3 border-b flex items-center justify-between">
          <div className="font-semibold">Calculator: {component.name}</div>
          <button className="text-sm text-gray-500" onClick={onClose}>Close</button>
        </div>
        <div className="p-4 space-y-3">
          <label className="block text-sm text-gray-700">Equation</label>
          <textarea className="w-full border rounded p-2 text-sm h-40" value={equation} onChange={e => setEquation(e.target.value)} />
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <div className="font-medium text-gray-600 mb-1">Inputs</div>
              <ul className="bg-gray-50 border rounded p-2 max-h-28 overflow-auto">
                {inputs.map(i => <li key={i.id}>{i.name}</li>)}
                {!inputs.length && <li className="text-gray-400">None</li>}
              </ul>
            </div>
            <div>
              <div className="font-medium text-gray-600 mb-1">Outputs</div>
              <ul className="bg-gray-50 border rounded p-2 max-h-28 overflow-auto">
                {outputs.map(o => <li key={o.id}>{o.name}</li>)}
                {!outputs.length && <li className="text-gray-400">None</li>}
              </ul>
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <button className="text-xs bg-blue-600 text-white px-2 py-1 rounded" onClick={() => { saveComponentData(component.id, 'equation', equation); onClose() }}>Save</button>
            <button className="text-xs bg-gray-200 px-2 py-1 rounded" onClick={onClose}>Cancel</button>
          </div>
        </div>
      </div>
    </div>
  )
}
