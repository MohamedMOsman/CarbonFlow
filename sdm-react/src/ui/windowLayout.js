// Dependency-free layout helpers to enable basic tests without DOM

export function initialLayout() {
  return {
    panels: {
      a: { id:'a', title:'A', open:true, state:'docked', region:'left', x:0,y:0,w:300,h:200 },
      b: { id:'b', title:'B', open:true, state:'docked', region:'left', x:0,y:0,w:300,h:200 },
      c: { id:'c', title:'C', open:true, state:'docked', region:'right', x:0,y:0,w:300,h:200 },
    },
    stacks: { left:['a','b'], right:['c'], top:[], bottom:[], lt:[], rt:[], lb:[], rb:[] },
    active: { left:'a', right:'c', top:null, bottom:null, lt:null, rt:null, lb:null, rb:null },
    sizes: { left:320, right:320, top:240, bottom:240, corners:{ lt:[320,260], rt:[320,260], lb:[320,260], rb:[320,260] } }
  }
}

export function dock(state, id, region) {
  const s = clone(state)
  Object.keys(s.stacks).forEach(r => { s.stacks[r] = s.stacks[r].filter(x => x !== id) })
  s.stacks[region] = [...(s.stacks[region]||[]), id]
  s.panels[id].state = 'docked'
  s.panels[id].region = region
  s.active[region] = id
  return s
}

export function floaty(state, id) {
  const s = clone(state)
  Object.keys(s.stacks).forEach(r => { s.stacks[r] = s.stacks[r].filter(x => x !== id) })
  s.panels[id].state = 'float'
  s.panels[id].region = null
  return s
}

export function closePanel(state, id) {
  const s = clone(state)
  s.panels[id].open = false
  Object.keys(s.stacks).forEach(r => { s.stacks[r] = s.stacks[r].filter(x => x !== id) })
  Object.keys(s.active).forEach(r => { if (s.active[r] === id) s.active[r] = (s.stacks[r][0] || null) })
  return s
}

export function restorePanel(state, id, region='left') {
  const s = clone(state)
  s.panels[id].open = true
  return dock(s, id, region)
}

export function persist(state) {
  return JSON.stringify(state)
}
export function revive(json) {
  return JSON.parse(json)
}

function clone(obj) { return JSON.parse(JSON.stringify(obj)) }

