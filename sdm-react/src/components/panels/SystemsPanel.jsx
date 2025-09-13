import React from 'react'
import { useModel } from '../../context/ModelContext.jsx'

function TreeToggle({ open }) {
  return (
    <svg className={`w-3 h-3 text-gray-500 transition-transform ${open? 'rotate-0':'-rotate-90'}`} viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M6 6l6 4-6 4V6z" clipRule="evenodd"/></svg>
  )
}

export default function SystemsPanel() {
  const { systems, activeSystemId, setActiveSystemId, addSystem, renameSystem, toggleSystem, deleteSystem, isFsSupported, hasOutputDir, chooseOutputDir, syncAllToDisk, tool, setTool, addComponent } = useModel()

  const renderSystemNode = (node, level=0) => {
    const isActive = activeSystemId === node.id
    return (
      <div key={node.id} className="ml-2">
        <div className="flex items-center gap-1 group">
          <button className="p-1" onClick={() => toggleSystem(node.id)} title="Toggle">
            <TreeToggle open={node.isExpanded !== false} />
          </button>
          <button className={`flex-1 text-left text-sm px-1 rounded ${isActive? 'bg-blue-100 text-blue-800':'hover:bg-gray-100'}`} onClick={() => setActiveSystemId(node.id)}>{node.name}</button>
          <button className="opacity-0 group-hover:opacity-100 text-xs px-1" onClick={() => {
            const name = prompt('System name', node.name)
            if (name) renameSystem(node.id, name)
          }}>Rename</button>
          <button className="opacity-0 group-hover:opacity-100 text-xs px-1" onClick={() => addSystem('New System', node.id)}>+ Child</button>
          <button className="opacity-0 group-hover:opacity-100 text-xs px-1 text-red-600" onClick={() => { if (confirm(`Delete system "${node.name}" and all children/components?`)) deleteSystem(node.id) }}>Delete</button>
        </div>
        {node.isExpanded !== false && (
          <div className="ml-3">
            {systems.filter(s => s.parentId === node.id).map(c => renderSystemNode(c, level+1))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="h-full w-full p-2 overflow-auto text-sm space-y-2">
      <div className="flex items-center justify-between mb-1">
        <h2 className="text-sm font-semibold text-gray-600">Systems</h2>
        <div className="flex items-center gap-1">
          <button className="text-xs bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded" onClick={() => addSystem('New System', null)}>+ Top-Level</button>
          {isFsSupported && (
            <button className={`text-xs px-2 py-1 rounded ${hasOutputDir ? 'bg-green-100 text-green-800 hover:bg-green-200' : 'bg-gray-200 hover:bg-gray-300'}`} title={hasOutputDir ? 'Output folder selected' : 'Pick output folder for system/component files'} onClick={() => chooseOutputDir()}>{hasOutputDir ? 'Folder ✓' : 'Pick Folder'}</button>
          )}
          {isFsSupported && (
            <button className={`text-xs px-2 py-1 rounded ${hasOutputDir ? 'bg-blue-100 text-blue-800 hover:bg-blue-200' : 'bg-gray-100 text-gray-400'}`} disabled={!hasOutputDir} title="Create/refresh folders and component JSON files" onClick={() => syncAllToDisk()}>Sync</button>
          )}
        </div>
      </div>
      <div>
        {systems.filter(s => s.parentId === null).map(s => renderSystemNode(s))}
      </div>
      {activeSystemId && (
        <div className="mt-2 p-2 bg-white border rounded">
          <div className="text-xs font-medium text-gray-600 mb-1">New Components</div>
          <div className="grid grid-cols-2 gap-1">
            {['Stock','Flow','Parameter','Dataset','Calculator','Connector'].map(type => (
              <button
                key={type}
                className={`text-xs px-2 py-1 rounded ${type==='Connector' ? (tool==='connect' ? 'bg-blue-600 text-white' : 'bg-gray-100 hover:bg-gray-200') : 'bg-gray-100 hover:bg-gray-200'}`}
                onClick={() => {
                  if (type === 'Connector') { setTool(tool === 'connect' ? 'select' : 'connect') }
                  else { addComponent(activeSystemId, type) }
                }}
                title={type==='Connector' ? 'Connect mode: click source then target' : ''}
              >
                {type}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

