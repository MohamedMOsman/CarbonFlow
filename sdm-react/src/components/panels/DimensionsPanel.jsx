import React, { useMemo } from 'react'
import { useModel } from '../../context/ModelContext.jsx'

export default function DimensionsPanel() {
  const { components, getResolvedComponent, activeScenarioId } = useModel()

  const dimensions = useMemo(() => {
    const map = new Map()
    components.forEach(c => {
      const eff = getResolvedComponent(c, activeScenarioId)
      const rows = eff?.data?.data || []
      if (!Array.isArray(rows) || !rows.length) return
      const header = rows[0] || []
      header.forEach(h => {
        const key = String(h || '').trim()
        if (!key) return
        map.set(key, (map.get(key) || 0) + 1)
      })
    })
    return Array.from(map.entries()).map(([name, count]) => ({ name, count })).sort((a,b) => a.name.localeCompare(b.name))
  }, [components, getResolvedComponent, activeScenarioId])

  return (
    <div className="h-full w-full p-2 overflow-auto text-sm">
      <div className="flex items-center justify-between mb-1">
        <h2 className="text-sm font-semibold text-gray-600">Dimensions</h2>
        <div className="text-[10px] text-gray-500">{dimensions.length} total</div>
      </div>
      <ul className="space-y-1 bg-white p-2 border rounded max-h-full overflow-auto">
        {dimensions.map(d => (
          <li key={d.name} className="flex items-center justify-between text-xs">
            <span className="font-medium text-gray-700">{d.name}</span>
            <span className="text-gray-500 text-[10px] bg-gray-100 rounded px-1.5 py-0.5">{d.count} comps</span>
          </li>
        ))}
        {!dimensions.length && (
          <li className="text-xs text-gray-400">No dimensions detected yet</li>
        )}
      </ul>
      <div className="text-[10px] text-gray-500 mt-1">
        Based on header row of dataset-like components.
      </div>
    </div>
  )
}

