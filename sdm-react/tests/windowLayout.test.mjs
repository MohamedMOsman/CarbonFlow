import assert from 'node:assert'
import { initialLayout, dock, floaty, closePanel, restorePanel, persist, revive } from '../src/ui/windowLayout.js'

function run() {
  let s = initialLayout()
  // Dock to same region should tab
  s = dock(s, 'c', 'left')
  assert.equal(s.stacks.left.includes('c'), true, 'panel c docked to left')
  assert.ok(s.stacks.left.length === 3, 'left has three tabs')
  assert.equal(s.active.left, 'c', 'active tab switched to c')

  // Float a panel removes it from stack
  s = floaty(s, 'a')
  assert.equal(s.stacks.left.includes('a'), false, 'floated removed from stack')
  assert.equal(s.panels.a.state, 'float', 'state float')

  // Close panel and ensure it disappears
  s = closePanel(s, 'b')
  assert.equal(s.panels.b.open, false, 'panel b closed')
  assert.equal(s.stacks.left.includes('b'), false, 'closed removed from stack')

  // Restore panel into region and becomes tab
  s = restorePanel(s, 'b', 'right')
  assert.equal(s.panels.b.open, true, 'panel b restored')
  assert.equal(s.stacks.right.includes('b'), true, 'restored into right stack')

  // Persistence round trip
  const json = persist(s)
  const re = revive(json)
  assert.deepEqual(re, s, 'persistence round-trip preserves state')

  console.log('windowLayout tests: OK')
}

run()

