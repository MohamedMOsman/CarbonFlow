import React from 'react'
import { useModel } from '../../context/ModelContext.jsx'

function TreeToggle({ open }) {
  return (
    <svg className={`w-3 h-3 text-gray-500 transition-transform ${open? 'rotate-0':'-rotate-90'}`} viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M6 6l6 4-6 4V6z" clipRule="evenodd"/></svg>
  )
}

export default function GlobalComponentsPanel() {
  const { systems, components, addReference, activeSystemId, toggleSystem } = useModel()

  const renderGlobalTree = (systemNode) => {
    return (
      <div key={`g-${systemNode.id}`} className="ml-2">
        <div className="flex items-center gap-1 group">
          <button className="p-1" onClick={() => toggleSystem(systemNode.id)} title="Toggle">
            <TreeToggle open={systemNode.isExpanded !== false} />
          </button>
          <div className="text-xs text-gray-600 font-medium">{systemNode.name}</div>
        </div>
        {systemNode.isExpanded !== false && (
          <>
            <ul className="ml-3 space-y-1">
              {components.filter(c => c.systemId === systemNode.id && c.type !== 'Reference').map(c => (
                <li key={c.id} className="flex items-center justify-between text-xs">
                  <span>{c.name} <span className="text-gray-400">({c.type})</span></span>
                  <button className="px-2 py-0.5 bg-gray-100 hover:bg-gray-200 rounded" onClick={() => {
                    if (!activeSystemId) { alert('Select a target system first.'); return }
                    addReference(activeSystemId, c.id)
                  }}>Ref here</button>
                </li>
              ))}
            </ul>
            <div className="ml-3">
              {systems.filter(s => s.parentId === systemNode.id).map(ch => renderGlobalTree(ch))}
            </div>
          </>
        )}
      </div>
    )
  }

  return (
    <div className="h-full w-full p-2 overflow-auto text-sm">
      <div className="flex items-center justify-between mb-1">
        <h2 className="text-sm font-semibold text-gray-600">Global Components</h2>
      </div>
      <div>
        {systems.filter(s => s.parentId === null).map(s => renderGlobalTree(s))}
      </div>
    </div>
  )
}

