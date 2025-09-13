import React from 'react'
import { useModel } from '../../context/ModelContext.jsx'

function TreeToggle({ open }) {
  return (
    <svg className={`w-3 h-3 text-gray-500 transition-transform ${open? 'rotate-0':'-rotate-90'}`} viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M6 6l6 4-6 4V6z" clipRule="evenodd"/></svg>
  )
}

export default function ScenariosPanel() {
  const { scenarios, activeScenarioId, setActiveScenarioId, addScenario, renameScenario, toggleScenario, deleteScenario } = useModel()

  const renderScenarioNode = (node, level=0) => {
    const hasChildren = scenarios.some(s => s.parentId === node.id)
    return (
      <div key={node.id} className="ml-2">
        <div className="flex items-center gap-1 group">
          <button className="p-1" onClick={() => toggleScenario(node.id)} title="Toggle">
            <TreeToggle open={node.isExpanded !== false} />
          </button>
          <button className={`flex-1 text-left text-sm px-1 rounded ${activeScenarioId===node.id? 'bg-blue-100 text-blue-800':'hover:bg-gray-100'}`} onClick={() => setActiveScenarioId(node.id)}>{node.name}</button>
          <button className="opacity-0 group-hover:opacity-100 text-xs px-1" onClick={() => {
            const name = prompt('Scenario name', node.name)
            if (name) renameScenario(node.id, name)
          }}>Rename</button>
          <button className="opacity-0 group-hover:opacity-100 text-xs px-1" onClick={() => setActiveScenarioId(addScenario('New Scenario', node.id))}>+ Child</button>
          {node.id !== 1 && (
            <button className="opacity-0 group-hover:opacity-100 text-xs px-1 text-red-600" onClick={() => { if (confirm(`Delete scenario "${node.name}" and its children?`)) deleteScenario(node.id) }}>Delete</button>
          )}
        </div>
        {node.isExpanded !== false && (
          <div className="ml-3">
            {scenarios.filter(s => s.parentId === node.id).map(c => renderScenarioNode(c, level+1))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="h-full w-full p-2 overflow-auto text-sm">
      <div className="flex items-center justify-between mb-1">
        <h2 className="text-sm font-semibold text-gray-600">Scenarios</h2>
        <button className="text-xs bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded" onClick={() => setActiveScenarioId(addScenario('New Scenario', null))}>+ Top-Level</button>
      </div>
      <div>
        {renderScenarioNode(scenarios.find(s => s.parentId === null) || { id: 1, name: 'Base', parentId: null, isExpanded: true })}
        {scenarios.filter(s => s.parentId === null && s.id !== 1).map(s => renderScenarioNode(s))}
      </div>
    </div>
  )
}

