import React, { useMemo, useRef } from 'react'
import { useModel } from '../context/ModelContext.jsx'

function download(filename, text) {
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export default function RightSidebar({ onOpenPivot, onOpenCalc }) {
  const { components, selectedId, renameComponent, removeComponent, saveComponentData, connections, getResolvedComponent, activeScenarioId } = useModel()
  const selected = useMemo(() => components.find(c => c.id === selectedId), [components, selectedId])
  const effective = useMemo(() => {
    if (!selected) return null
    return selected.type === 'Reference'
      ? (components.find(c => c.id === selected.originalId) || selected)
      : selected
  }, [selected, components])
  const fileRef = useRef(null)

  const effType = effective?.type || ''
  const isDataset = effType === 'Dataset' || ['Stock','Flow','Parameter'].includes(effType)
  const isCalculator = effType === 'Calculator'
  const selId = selected?.id
  const resolvedEffective = useMemo(() => effective ? getResolvedComponent(effective, activeScenarioId) : null, [effective, activeScenarioId, getResolvedComponent])
  const inputs = useMemo(() => {
    if (!selId) return []
    return connections
      .filter(cn => cn.toId === selId)
      .map(cn => components.find(c => c.id === cn.fromId))
      .filter(Boolean)
  }, [connections, components, selId])
  const outputs = useMemo(() => {
    if (!selId) return []
    return connections
      .filter(cn => cn.fromId === selId)
      .map(cn => components.find(c => c.id === cn.toId))
      .filter(Boolean)
  }, [connections, components, selId])

  return (
    <aside className="w-80 bg-gray-50 p-4 border-l border-gray-200 shadow-inner space-y-3 overflow-auto">
      {!selected ? (
        <div className="text-sm text-gray-500">Select a component to edit.</div>
      ) : (
        <div>
          <div className="text-xs text-gray-500 uppercase">Component</div>
          <input
            className="mt-1 w-full border rounded px-2 py-1 text-sm"
            value={selected.name ?? ''}
            onChange={e => renameComponent(selected.id, e.target.value)}
          />
          <div className="text-xs text-gray-500">
            Type: {selected.type} {selected.type === 'Reference' && effective ? `-> ${effective.name} (${effective.type})` : ''}
          </div>
          <button className="mt-2 text-xs text-red-600 hover:underline" onClick={() => removeComponent(selected.id)}>Delete</button>
        </div>
      )}

      {isDataset && (
        <div className="space-y-2">
          <div className="text-xs text-gray-500 uppercase">Dataset</div>
          <div className="flex gap-2">
            <button className="text-xs bg-blue-600 text-white px-2 py-1 rounded" onClick={() => onOpenPivot(effective)}>Open Pivot</button>
            <button
              className="text-xs bg-gray-200 px-2 py-1 rounded"
              onClick={() => {
                const rows = (resolvedEffective?.data?.data) || []
                const toCsv = (arr) => arr.map(v => {
                  const s = String(v ?? '')
                  if (s.includes(',') || s.includes('"') || s.includes('\n')) return `"${s.replace(/"/g, '""')}"`
                  return s
                }).join(',')
                download(`${resolvedEffective?.name || effective.name}_data.csv`, rows.map(toCsv).join('\n'))
              }}
            >
              Export CSV
            </button>
            <button className="text-xs bg-gray-200 px-2 py-1 rounded" onClick={() => fileRef.current?.click()}>Import CSV</button>
            <input
              ref={fileRef}
              type="file"
              accept=".csv"
              className="hidden"
              onChange={e => {
                const file = e.target.files?.[0]
                if (!file) return
                const reader = new FileReader()
                reader.onload = () => {
                  const text = String(reader.result || '')
                  const lines = text.split(/\r?\n/).filter(Boolean)
                  const rows = lines.map(line => {
                    const parts = []
                    let curr = ''
                    let inQ = false
                    for (let i = 0; i < line.length; i++) {
                      const ch = line[i]
                      if (ch === '"') {
                        if (inQ && line[i + 1] === '"') { curr += '"'; i++ } else { inQ = !inQ }
                      } else if (ch === ',' && !inQ) { parts.push(curr); curr = '' } else { curr += ch }
                    }
                    parts.push(curr)
                    return parts
                  })
                  // editing a Reference affects its original
                  saveComponentData((selected.type === 'Reference' ? effective.id : selected.id), 'data', rows)
                  e.target.value = ''
                }
                reader.readAsText(file)
              }}
            />
          </div>
        </div>
      )}

      {isCalculator && (
        <div className="space-y-2">
          <div className="text-xs text-gray-500 uppercase">Calculator</div>
          <button className="text-xs bg-blue-600 text-white px-2 py-1 rounded" onClick={() => onOpenCalc(effective)}>Edit Equation</button>
        </div>
      )}

      {/* Connections overview */}
      <div className="space-y-2">
        <div className="text-xs text-gray-500 uppercase">Connections</div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div>
            <div className="font-medium text-gray-600">Inputs</div>
            <ul className="bg-gray-50 border rounded p-2 max-h-40 overflow-auto">
              {inputs.map(i => <li key={i.id}>{i.name}</li>)}
              {!inputs.length && <li className="text-gray-400">None</li>}
            </ul>
          </div>
          <div>
            <div className="font-medium text-gray-600">Outputs</div>
            <ul className="bg-gray-50 border rounded p-2 max-h-40 overflow-auto">
              {outputs.map(o => <li key={o.id}>{o.name}</li>)}
              {!outputs.length && <li className="text-gray-400">None</li>}
            </ul>
          </div>
        </div>
      </div>
    </aside>
  )
}
