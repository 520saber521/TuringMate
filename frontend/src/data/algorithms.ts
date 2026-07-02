// ============================================================
// 408 Algorithm Definitions — step generators for visualization
// ============================================================

export type AlgoCategory = 'sorting' | 'searching' | 'linked-list' | 'tree' | 'graph' | 'heap'

export interface ArrayElement {
  value: number
  status: 'default' | 'pivot' | 'comparing' | 'swapped' | 'sorted'
}

export interface ListNode {
  value: number
  status: 'default' | 'pre' | 'cur' | 'deleted'
}

export interface TreeNode {
  value: number
  status: 'default' | 'current' | 'visited'
  left: number | null
  right: number | null
  x: number
  y: number
}

export interface GraphNodeEl {
  label: string
  x: number
  y: number
  status: 'default' | 'current' | 'visiting' | 'visited' | 'queued'
  distance: number // for Dijkstra
}

export interface GraphEdge {
  from: number
  to: number
  weight: number
  status: 'default' | 'active' | 'considered' | 'shortest'
  directed: boolean
}

export interface AlgorithmStep {
  lineNumber: number
  description: string
  variables: Record<string, string>
  visualType: 'array' | 'linked-list' | 'tree' | 'graph' | 'heap'
  elements: (ArrayElement | ListNode | TreeNode | GraphNodeEl)[]
  highlights: number[]
  edges?: GraphEdge[] // for graph visualization
}

export interface AlgorithmDef {
  id: string
  name: string
  category: AlgoCategory
  description: string
  timeComplexity: string
  pseudocode: string[]
  cCode?: string
  pythonCode?: string
  defaultInput: string    // JSON string
  inputLabel: string
  inputHint: string
  generateSteps: (input: unknown) => Generator<AlgorithmStep, void, unknown>
}

// ── Helpers ──

function makeEls(values: number[], status: ArrayElement['status'] = 'default'): ArrayElement[] {
  return values.map(v => ({ value: v, status }))
}

function cloneArr(els: ArrayElement[]): ArrayElement[] {
  return els.map(e => ({ ...e }))
}

function markArr(els: ArrayElement[], indices: number[], status: ArrayElement['status']): ArrayElement[] {
  const res = cloneArr(els)
  for (const i of indices) {
    if (i >= 0 && i < res.length) res[i] = { ...res[i], status }
  }
  return res
}

// ════════════════════════════════════════════
// 1. Quick Sort — 快速排序
// ════════════════════════════════════════════

function* quickSortGen(arr: number[]): Generator<AlgorithmStep> {
  const els = makeEls(arr)

  yield {
    lineNumber: 1,
    description: `初始数组：[${arr.join(', ')}]`,
    variables: { 'low': '0', 'high': String(arr.length - 1) },
    visualType: 'array',
    elements: cloneArr(els),
    highlights: [],
  }

  const stack: [number, number][] = [[0, arr.length - 1]]

  while (stack.length > 0) {
    const [low, high] = stack.pop()!
    if (low >= high) {
      // Mark single element as sorted
      if (low === high) {
        for (let k = 0; k < els.length; k++) {
          if (els[k].status === 'default' && k === low) els[k] = { ...els[k], status: 'sorted' }
        }
        yield {
          lineNumber: 4,
          description: `区间 [${low}] 已有序`,
          variables: { 'low': String(low), 'high': String(high) },
          visualType: 'array',
          elements: cloneArr(els),
          highlights: [low],
        }
      }
      continue
    }

    const pivotIdx = high
    const pivotVal = els[pivotIdx].value

    yield {
      lineNumber: 3,
      description: `选取基准 pivot = ${pivotVal}，对 [${low}, ${high}] 分区`,
      variables: { 'pivot': String(pivotVal), 'low': String(low), 'high': String(high) },
      visualType: 'array',
      elements: markArr(els, [pivotIdx], 'pivot'),
      highlights: [pivotIdx],
    }

    let i = low - 1
    for (let j = low; j < high; j++) {
      yield {
        lineNumber: 6,
        description: `比较 arr[${j}]=${els[j].value} 与 pivot=${pivotVal}`,
        variables: { 'j': String(j), 'i': String(i), 'pivot': String(pivotVal) },
        visualType: 'array',
        elements: markArr(els, [pivotIdx, j], j === pivotIdx ? 'pivot' : 'comparing'),
        highlights: [j, pivotIdx],
      }

      if (els[j].value <= pivotVal) {
        i++
        if (i !== j) {
          yield {
            lineNumber: 7,
            description: `arr[${j}]=${els[j].value} ≤ pivot，交换 arr[${i}] 与 arr[${j}]`,
            variables: { 'i': String(i), 'j': String(j), '交换': `${els[i].value} ↔ ${els[j].value}` },
            visualType: 'array',
            elements: markArr(els, [i, j, pivotIdx], 'swapped'),
            highlights: [i, j],
          }
          ;[els[i], els[j]] = [els[j], els[i]]
        } else {
          yield {
            lineNumber: 7,
            description: `arr[${j}]=${els[j].value} ≤ pivot，i 自增至 ${i}（无需交换）`,
            variables: { 'i': String(i), 'j': String(j) },
            visualType: 'array',
            elements: markArr(els, [i, pivotIdx], 'comparing'),
            highlights: [i, j],
          }
        }
      }
    }

    // Swap pivot to correct position
    i++
    if (i !== high) {
      yield {
        lineNumber: 9,
        description: `交换 pivot 到正确位置：arr[${i}] ↔ arr[${high}]`,
        variables: { 'pivot归位': `位置 ${i}` },
        visualType: 'array',
        elements: markArr(els, [i, high], 'swapped'),
        highlights: [i, high],
      }
      ;[els[i], els[high]] = [els[high], els[i]]
    }

    els[i] = { ...els[i], status: 'sorted' }

    yield {
      lineNumber: 10,
      description: `pivot 归位到 arr[${i}]，左侧 ≤ ${pivotVal}，右侧 ≥ ${pivotVal}`,
      variables: { 'pivot位置': String(i), 'pivot值': String(pivotVal) },
      visualType: 'array',
      elements: cloneArr(els),
      highlights: [i],
    }

    // Push subproblems (right first so left is processed first in stack)
    stack.push([i + 1, high])
    stack.push([low, i - 1])
  }

  // All sorted
  yield {
    lineNumber: 1,
    description: `排序完成：[${els.map(e => e.value).join(', ')}]`,
    variables: { '结果': '已完成' },
    visualType: 'array',
    elements: makeEls(els.map(e => e.value), 'sorted'),
    highlights: [],
  }
}

// ════════════════════════════════════════════
// 2. Binary Search — 二分查找
// ════════════════════════════════════════════

function* binarySearchGen(arr: number[], target: number): Generator<AlgorithmStep> {
  // arr must be sorted
  const sorted = [...arr].sort((a, b) => a - b)
  const els = makeEls(sorted)

  yield {
    lineNumber: 1,
    description: `有序数组：[${sorted.join(', ')}]，查找 target = ${target}`,
    variables: { 'target': String(target) },
    visualType: 'array',
    elements: cloneArr(els),
    highlights: [],
  }

  let low = 0
  let high = sorted.length - 1

  while (low <= high) {
    const mid = Math.floor((low + high) / 2)

    yield {
      lineNumber: 3,
      description: `low=${low}, high=${high}，mid = ⌊(${low}+${high})/2⌋ = ${mid}`,
      variables: { 'low': String(low), 'high': String(high), 'mid': String(mid), 'arr[mid]': String(sorted[mid]) },
      visualType: 'array',
      elements: markArr(els, [mid], 'pivot'),
      highlights: [low, mid, high],
    }

    if (sorted[mid] === target) {
      yield {
        lineNumber: 5,
        description: `arr[${mid}] = ${sorted[mid]} = target，找到！`,
        variables: { '结果': `位置 ${mid}` },
        visualType: 'array',
        elements: markArr(els, [mid, low, high], 'sorted'),
        highlights: [mid],
      }
      return
    } else if (sorted[mid] < target) {
      yield {
        lineNumber: 8,
        description: `arr[${mid}] = ${sorted[mid]} < ${target}，在右半区查找`,
        variables: { 'low': `${mid} + 1 = ${mid + 1}`, 'high': String(high) },
        visualType: 'array',
        elements: markArr(els, [mid], 'comparing'),
        highlights: [mid, low, high],
      }
      low = mid + 1
    } else {
      yield {
        lineNumber: 10,
        description: `arr[${mid}] = ${sorted[mid]} > ${target}，在左半区查找`,
        variables: { 'low': String(low), 'high': `${mid} - 1 = ${mid - 1}` },
        visualType: 'array',
        elements: markArr(els, [mid], 'comparing'),
        highlights: [mid, low, high],
      }
      high = mid - 1
    }
  }

  yield {
    lineNumber: 12,
    description: `low(${low}) > high(${high})，未找到 target = ${target}`,
    variables: { '结果': '不存在' },
    visualType: 'array',
    elements: cloneArr(els),
    highlights: [],
  }
}

// ════════════════════════════════════════════
// 3. Linked List Delete — 链表删除
// ════════════════════════════════════════════

function* linkedListDeleteGen(values: number[], x: number): Generator<AlgorithmStep> {
  const nodes: ListNode[] = values.map((v, i) => ({
    value: v,
    status: 'default' as ListNode['status'],
  }))

  yield {
    lineNumber: 1,
    description: `链表：[${values.join(' → ')} → NULL]，删除所有值为 ${x} 的结点`,
    variables: { 'x': String(x) },
    visualType: 'linked-list',
    elements: [...nodes],
    highlights: [],
  }

  // Add dummy head
  const all = [{ value: -1, status: 'default' as ListNode['status'] }, ...nodes]

  let pre = 0  // dummy head
  let cur = 1

  while (cur < all.length) {
    // Mark current pre and cur
    const state = all.map(n => ({ ...n, status: 'default' as ListNode['status'] }))
    state[pre].status = 'pre'
    state[cur].status = 'cur'

    yield {
      lineNumber: 4,
      description: `检查结点 arr[${cur}] = ${all[cur].value}${all[cur].value === -1 ? ' (哨兵)' : ''}`,
      variables: { 'pre': String(pre), 'cur': String(cur), 'pre.val': String(all[pre].value), 'cur.val': String(all[cur].value) },
      visualType: 'linked-list',
      elements: [...state],
      highlights: [pre, cur],
    }

    if (all[cur].value === x) {
      // Delete node
      yield {
        lineNumber: 5,
        description: `arr[${cur}].val = ${all[cur].value} = x，删除此结点`,
        variables: { '操作': `跳过结点 ${cur}` },
        visualType: 'linked-list',
        elements: state.map((n, i) => i === cur ? { ...n, status: 'deleted' as const } : n),
        highlights: [cur],
      }

      all.splice(cur, 1)
      // cur now points to next element (no need to increment)
    } else {
      yield {
        lineNumber: 7,
        description: `arr[${cur}].val = ${all[cur].value} ≠ x，pre 和 cur 后移`,
        variables: { 'pre': `${pre} → ${pre + 1}`, 'cur': `${cur} → ${cur + 1}` },
        visualType: 'linked-list',
        elements: [...state],
        highlights: [pre, cur],
      }
      pre = cur
      cur++
    }
  }

  // Remove dummy head for display
  const finalList = all.slice(1)

  yield {
    lineNumber: 1,
    description: `删除完成：[${finalList.map(n => n.value).join(' → ') || '空链表'} → NULL]`,
    variables: { '结果': '已完成' },
    visualType: 'linked-list',
    elements: finalList.map(n => ({ ...n, status: 'sorted' as const })),
    highlights: [],
  }
}

// ════════════════════════════════════════════
// 4. Tree Pre-order Traversal — 先序遍历
// ════════════════════════════════════════════

interface TreeNodeData {
  value: number
  left: TreeNodeData | null
  right: TreeNodeData | null
}

function buildTreeLayout(root: TreeNodeData | null): TreeNode[] {
  if (!root) return []
  const result: TreeNode[] = []
  let id = 0

  function walk(
    node: TreeNodeData | null,
    depth: number,
    xOffset: number,
  ): number | null {
    if (!node) return null
    const myId = id++
    // Calculate x position based on complete tree layout
    const leafCount = 1 << (4 - depth) // approximate
    const x = xOffset

    result.push({
      value: node.value,
      status: 'default',
      left: null,
      right: null,
      x: 0,
      y: depth,
    })

    const childCount = 1 << (3 - depth)
    const leftIdx = walk(node.left, depth + 1, xOffset - childCount * 40)
    const rightIdx = walk(node.right, depth + 1, xOffset + childCount * 40)

    result[myId].left = leftIdx
    result[myId].right = rightIdx

    // Adjust x positions after children are placed
    const leftX = leftIdx !== null ? result[leftIdx].x : xOffset - 40
    const rightX = rightIdx !== null ? result[rightIdx].x : xOffset + 40
    result[myId].x = Math.round((leftX + rightX) / 2)

    return myId
  }

  walk(root, 0, 0)
  return result
}

function* preorderGen(root: TreeNodeData): Generator<AlgorithmStep> {
  const nodes = buildTreeLayout(root)

  yield {
    lineNumber: 1,
    description: '先序遍历（根 → 左 → 右）开始',
    variables: {},
    visualType: 'tree',
    elements: nodes.map(n => ({ ...n })),
    highlights: [],
  }

  const stack: number[] = [0] // root is always index 0
  const visited: number[] = []

  while (stack.length > 0) {
    const nodeIdx = stack.pop()!
    const updated = nodes.map((n, i) => ({
      ...n,
      status: visited.includes(i) ? 'visited' as const : i === nodeIdx ? 'current' as const : 'default' as const,
    }))

    yield {
      lineNumber: 3,
      description: `访问结点 ${nodes[nodeIdx].value}`,
      variables: { '当前': String(nodes[nodeIdx].value), '栈': `[${stack.map(i => nodes[i].value).join(', ')}]` },
      visualType: 'tree',
      elements: [...updated],
      highlights: [nodeIdx],
    }

    visited.push(nodeIdx)
    nodes[nodeIdx].status = 'visited'

    // Push right first so left is processed first
    if (nodes[nodeIdx].right !== null) {
      stack.push(nodes[nodeIdx].right)
    }
    if (nodes[nodeIdx].left !== null) {
      stack.push(nodes[nodeIdx].left)
    }
  }

  yield {
    lineNumber: 1,
    description: `先序遍历完成：[${visited.map(i => nodes[i].value).join(', ')}]`,
    variables: { '结果': visited.map(i => nodes[i].value).join(', ') },
    visualType: 'tree',
    elements: nodes.map(n => ({ ...n, status: 'visited' as const })),
    highlights: [],
  }
}

// ════════════════════════════════════════════
// 5. Tree In-order Traversal — 中序遍历
// ════════════════════════════════════════════

function* inorderGen(root: TreeNodeData): Generator<AlgorithmStep> {
  const nodes = buildTreeLayout(root)
  const visited: number[] = []

  yield {
    lineNumber: 1,
    description: '中序遍历（左 → 根 → 右）开始',
    variables: {},
    visualType: 'tree',
    elements: nodes.map(n => ({ ...n })),
    highlights: [],
  }

  const stack: number[] = []
  let cur: number | null = 0 // root

  while (stack.length > 0 || cur !== null) {
    // Go left as far as possible
    while (cur !== null) {
      stack.push(cur)

      const updated = nodes.map((n, i) => ({
        ...n,
        status: visited.includes(i) ? 'visited' as const : i === cur ? 'current' as const : 'default' as const,
      }))

      yield {
        lineNumber: 3,
        description: `沿左子树深入：入栈 ${nodes[cur].value}`,
        variables: { '入栈': String(nodes[cur].value), '栈深度': String(stack.length) },
        visualType: 'tree',
        elements: [...updated],
        highlights: [cur],
      }

      cur = nodes[cur].left
    }

    cur = stack.pop()!
    visited.push(cur)

    const updated2 = nodes.map((n, i) => ({
      ...n,
      status: visited.includes(i) ? 'visited' as const : i === cur ? 'current' as const : 'default' as const,
    }))

    yield {
      lineNumber: 6,
      description: `出栈并访问结点 ${nodes[cur].value}`,
      variables: { '访问': String(nodes[cur].value), '栈': `[${stack.map(i => nodes[i].value).join(', ')}]` },
      visualType: 'tree',
      elements: [...updated2],
      highlights: [cur],
    }

    cur = nodes[cur].right
  }

  yield {
    lineNumber: 1,
    description: `中序遍历完成：[${visited.map(i => nodes[i].value).join(', ')}]`,
    variables: { '结果': visited.map(i => nodes[i].value).join(', ') },
    visualType: 'tree',
    elements: nodes.map(n => ({ ...n, status: 'visited' as const })),
    highlights: [],
  }
}

// ════════════════════════════════════════════
// 6. Level-order Traversal — 层序遍历
// ════════════════════════════════════════════

function* levelorderGen(root: TreeNodeData): Generator<AlgorithmStep> {
  const nodes = buildTreeLayout(root)
  const visited: number[] = []
  const queue: number[] = [0] // root

  yield {
    lineNumber: 1,
    description: '层序遍历（BFS）开始，根结点入队',
    variables: { '队列': `[${nodes[0].value}]` },
    visualType: 'tree',
    elements: nodes.map(n => ({ ...n })),
    highlights: [0],
  }

  while (queue.length > 0) {
    const nodeIdx = queue.shift()!
    visited.push(nodeIdx)

    const updated = nodes.map((n, i) => ({
      ...n,
      status: visited.includes(i) ? 'visited' as const : i === nodeIdx ? 'current' as const : 'default' as const,
    }))

    yield {
      lineNumber: 4,
      description: `出队并访问结点 ${nodes[nodeIdx].value}`,
      variables: { '访问': String(nodes[nodeIdx].value), '队列': `[${queue.map(i => nodes[i].value).join(', ')}]` },
      visualType: 'tree',
      elements: [...updated],
      highlights: [nodeIdx],
    }

    if (nodes[nodeIdx].left !== null) {
      queue.push(nodes[nodeIdx].left)
    }
    if (nodes[nodeIdx].right !== null) {
      queue.push(nodes[nodeIdx].right)
    }

    if (queue.length > 0) {
      const updated2 = nodes.map((n, i) => ({
        ...n,
        status: visited.includes(i) ? 'visited' as const : queue.includes(i) ? 'current' as const : 'default' as const,
      }))
      yield {
        lineNumber: 6,
        description: `子节点入队，队列：[${queue.map(i => nodes[i].value).join(', ')}]`,
        variables: { '队列': `[${queue.map(i => nodes[i].value).join(', ')}]` },
        visualType: 'tree',
        elements: [...updated2],
        highlights: queue,
      }
    }
  }

  yield {
    lineNumber: 1,
    description: `层序遍历完成：[${visited.map(i => nodes[i].value).join(', ')}]`,
    variables: { '结果': visited.map(i => nodes[i].value).join(', ') },
    visualType: 'tree',
    elements: nodes.map(n => ({ ...n, status: 'visited' as const })),
    highlights: [],
  }
}

// ════════════════════════════════════════════
// 7. Bubble Sort — 冒泡排序（简单直观）
// ════════════════════════════════════════════

function* bubbleSortGen(arr: number[]): Generator<AlgorithmStep> {
  const els = makeEls(arr)

  yield {
    lineNumber: 1,
    description: `初始数组：[${arr.join(', ')}]`,
    variables: { 'n': String(arr.length) },
    visualType: 'array',
    elements: cloneArr(els),
    highlights: [],
  }

  for (let i = 0; i < els.length - 1; i++) {
    let swapped = false
    for (let j = 0; j < els.length - 1 - i; j++) {
      yield {
        lineNumber: 3,
        description: `比较 arr[${j}]=${els[j].value} 与 arr[${j + 1}]=${els[j + 1].value}`,
        variables: { 'i': String(i), 'j': String(j) },
        visualType: 'array',
        elements: markArr(els, [j, j + 1], 'comparing'),
        highlights: [j, j + 1],
      }

      if (els[j].value > els[j + 1].value) {
        yield {
          lineNumber: 4,
          description: `${els[j].value} > ${els[j + 1].value}，交换`,
          variables: { '交换': `${els[j].value} ↔ ${els[j + 1].value}` },
          visualType: 'array',
          elements: markArr(els, [j, j + 1], 'swapped'),
          highlights: [j, j + 1],
        }
        ;[els[j], els[j + 1]] = [els[j + 1], els[j]]
        swapped = true
      }
    }
    // Mark last i+1 elements as sorted
    for (let k = els.length - 1 - i; k < els.length; k++) {
      els[k] = { ...els[k], status: 'sorted' }
    }

    yield {
      lineNumber: 7,
      description: `第 ${i + 1} 轮结束，arr[${els.length - 1 - i}] 已归位`,
      variables: { '轮次': String(i + 1), '已有序': String(i + 1) },
      visualType: 'array',
      elements: cloneArr(els),
      highlights: Array.from({ length: i + 1 }, (_, k) => els.length - 1 - k),
    }

    if (!swapped) {
      // Mark all as sorted
      for (let k = 0; k < els.length; k++) els[k] = { ...els[k], status: 'sorted' }
      yield {
        lineNumber: 8,
        description: `本轮无交换，排序提前结束`,
        variables: { '结果': '已有序' },
        visualType: 'array',
        elements: cloneArr(els),
        highlights: [],
      }
      break
    }
  }
}

// ════════════════════════════════════════════
// 8. Merge Sort — 归并排序
// ════════════════════════════════════════════

function* mergeSortGen(arr: number[]): Generator<AlgorithmStep> {
  const els = makeEls(arr)
  const working = makeEls([...arr])

  yield {
    lineNumber: 1,
    description: `初始数组：[${arr.join(', ')}]`,
    variables: { 'n': String(arr.length) },
    visualType: 'array',
    elements: cloneArr(els),
    highlights: [],
  }

  yield* mergeSortRecursive(working, els, 0, arr.length - 1)
}

function* mergeSortRecursive(
  working: ArrayElement[],
  original: ArrayElement[],
  left: number,
  right: number,
): Generator<AlgorithmStep> {
  if (left >= right) return

  const mid = Math.floor((left + right) / 2)

  yield {
    lineNumber: 3,
    description: `分解：[${left}, ${right}] → [${left}, ${mid}] 和 [${mid + 1}, ${right}]`,
    variables: { 'left': String(left), 'mid': String(mid), 'right': String(right) },
    visualType: 'array',
    elements: markArr(original, Array.from({ length: right - left + 1 }, (_, i) => left + i), 'comparing'),
    highlights: [left, mid, right],
  }

  yield* mergeSortRecursive(working, original, left, mid)
  yield* mergeSortRecursive(working, original, mid + 1, right)

  // Merge
  yield {
    lineNumber: 7,
    description: `合并：[${left}, ${mid}] 和 [${mid + 1}, ${right}]`,
    variables: { '操作': '归并两个有序子数组' },
    visualType: 'array',
    elements: markArr(original, Array.from({ length: right - left + 1 }, (_, i) => left + i), 'pivot'),
    highlights: [left, mid, right],
  }

  const temp: ArrayElement[] = []
  let i = left, j = mid + 1

  while (i <= mid && j <= right) {
    if ((working[i]?.value ?? 0) <= (working[j]?.value ?? 0)) {
      temp.push({ ...working[i], status: 'sorted' })
      i++
    } else {
      temp.push({ ...working[j], status: 'sorted' })
      j++
    }
  }
  while (i <= mid) temp.push({ ...working[i++], status: 'sorted' })
  while (j <= right) temp.push({ ...working[j++], status: 'sorted' })

  for (let k = 0; k < temp.length; k++) {
    working[left + k] = { ...temp[k] }
    original[left + k] = { ...temp[k] }
  }

  yield {
    lineNumber: 10,
    description: `合并结果：[${temp.map(e => e.value).join(', ')}]`,
    variables: { '区间': `[${left}, ${right}]` },
    visualType: 'array',
    elements: cloneArr(original),
    highlights: Array.from({ length: right - left + 1 }, (_, i) => left + i),
  }
}

// ════════════════════════════════════════════
// 9. DFS — 深度优先搜索
// ════════════════════════════════════════════

interface GraphDef {
  n: number
  nodeLabels: string[]
  edges: [number, number, number][] // [from, to, weight]
  directed: boolean
}

function layoutGraph(n: number): { x: number; y: number }[] {
  const positions: { x: number; y: number }[] = []
  const r = 120
  const cx = 0
  const cy = 0
  for (let i = 0; i < n; i++) {
    const angle = (2 * Math.PI * i) / n - Math.PI / 2
    positions.push({ x: Math.round(cx + r * Math.cos(angle)), y: Math.round(cy + r * Math.sin(angle)) })
  }
  return positions
}

function buildGraphNodes(graph: GraphDef, status: GraphNodeEl['status'] = 'default'): GraphNodeEl[] {
  const pos = layoutGraph(graph.n)
  return graph.nodeLabels.map((label, i) => ({ label, x: pos[i].x, y: pos[i].y, status, distance: Infinity }))
}

function buildGraphEdges(graph: GraphDef, status: GraphEdge['status'] = 'default'): GraphEdge[] {
  return graph.edges.map(([from, to, weight]) => ({ from, to, weight, status, directed: graph.directed }))
}

function* dfsGen(graph: GraphDef, start: number): Generator<AlgorithmStep> {
  const nodes = buildGraphNodes(graph)
  const edges = buildGraphEdges(graph)
  const adj: number[][] = Array.from({ length: graph.n }, () => [])
  for (const [f, t] of graph.edges) {
    adj[f].push(t)
    if (!graph.directed) adj[t].push(f)
  }

  yield {
    lineNumber: 1,
    description: `从结点 ${graph.nodeLabels[start]} 开始 DFS`,
    variables: { '起始': graph.nodeLabels[start] },
    visualType: 'graph',
    elements: nodes.map((n, i) => ({ ...n, status: i === start ? 'current' : 'default' })),
    highlights: [start],
    edges: [...edges],
  }

  const visited: boolean[] = Array(graph.n).fill(false)
  const stack: number[] = [start]
  const order: number[] = []

  while (stack.length > 0) {
    const v = stack.pop()!
    if (visited[v]) continue

    visited[v] = true
    order.push(v)

    yield {
      lineNumber: 4,
      description: `访问结点 ${graph.nodeLabels[v]}`,
      variables: { '访问': graph.nodeLabels[v], '栈': `[${stack.map(i => graph.nodeLabels[i]).join(', ')}]`, '访问顺序': order.map(i => graph.nodeLabels[i]).join(' → ') },
      visualType: 'graph',
      elements: nodes.map((n, i) => ({
        ...n,
        status: i === v ? 'current' : visited[i] ? 'visited' : stack.includes(i) ? 'visiting' : 'default',
      })),
      highlights: [v],
      edges: [...edges],
    }

    // Push neighbors in reverse order for correct traversal
    const neighbors = adj[v].slice().reverse()
    for (const w of neighbors) {
      if (!visited[w]) {
        stack.push(w)
        yield {
          lineNumber: 7,
          description: `邻接点 ${graph.nodeLabels[w]} 入栈`,
          variables: { '入栈': graph.nodeLabels[w], '栈': `[${stack.map(i => graph.nodeLabels[i]).join(', ')}]` },
          visualType: 'graph',
          elements: nodes.map((n, i) => ({
            ...n,
            status: visited[i] ? 'visited' : stack.includes(i) ? 'visiting' : 'default',
          })),
          highlights: [w],
          edges: edges.map(e => e.from === v && e.to === w || e.to === v && e.from === w ? { ...e, status: 'considered' as const } : e),
        }
      }
    }
  }

  yield {
    lineNumber: 1,
    description: `DFS 完成，访问顺序：${order.map(i => graph.nodeLabels[i]).join(' → ')}`,
    variables: { '结果': order.map(i => graph.nodeLabels[i]).join(' → ') },
    visualType: 'graph',
    elements: nodes.map(n => ({ ...n, status: 'visited' })),
    highlights: [],
    edges: [...edges],
  }
}

// ════════════════════════════════════════════
// 10. BFS — 广度优先搜索
// ════════════════════════════════════════════

function* bfsGen(graph: GraphDef, start: number): Generator<AlgorithmStep> {
  const nodes = buildGraphNodes(graph)
  const edges = buildGraphEdges(graph)
  const adj: number[][] = Array.from({ length: graph.n }, () => [])
  for (const [f, t] of graph.edges) {
    adj[f].push(t)
    if (!graph.directed) adj[t].push(f)
  }

  yield {
    lineNumber: 1,
    description: `从结点 ${graph.nodeLabels[start]} 开始 BFS`,
    variables: { '起始': graph.nodeLabels[start] },
    visualType: 'graph',
    elements: nodes.map((n, i) => ({ ...n, status: i === start ? 'current' : 'default' })),
    highlights: [start],
    edges: [...edges],
  }

  const visited: boolean[] = Array(graph.n).fill(false)
  const queue: number[] = [start]
  visited[start] = true
  const order: number[] = []

  while (queue.length > 0) {
    const v = queue.shift()!
    order.push(v)

    yield {
      lineNumber: 4,
      description: `出队并访问结点 ${graph.nodeLabels[v]}`,
      variables: { '访问': graph.nodeLabels[v], '队列': `[${queue.map(i => graph.nodeLabels[i]).join(', ')}]`, '访问顺序': order.map(i => graph.nodeLabels[i]).join(' → ') },
      visualType: 'graph',
      elements: nodes.map((n, i) => ({
        ...n,
        status: i === v ? 'current' : visited[i] ? 'visited' : queue.includes(i) ? 'queued' : 'default',
      })),
      highlights: [v],
      edges: [...edges],
    }

    for (const w of adj[v]) {
      if (!visited[w]) {
        visited[w] = true
        queue.push(w)
        yield {
          lineNumber: 7,
          description: `邻接点 ${graph.nodeLabels[w]} 入队`,
          variables: { '入队': graph.nodeLabels[w], '队列': `[${queue.map(i => graph.nodeLabels[i]).join(', ')}]` },
          visualType: 'graph',
          elements: nodes.map((n, i) => ({
            ...n,
            status: visited[i] ? (i === v ? 'current' : i === w ? 'queued' : 'visited') : 'default',
          })),
          highlights: [w],
          edges: edges.map(e => e.from === v && e.to === w || e.to === v && e.from === w ? { ...e, status: 'considered' as const } : e),
        }
      }
    }

    // Update current to visited
    const idx = order.length - 1
    nodes[idx] = { ...nodes[idx], status: 'visited' }
  }

  yield {
    lineNumber: 1,
    description: `BFS 完成，访问顺序：${order.map(i => graph.nodeLabels[i]).join(' → ')}`,
    variables: { '结果': order.map(i => graph.nodeLabels[i]).join(' → ') },
    visualType: 'graph',
    elements: nodes.map(n => ({ ...n, status: 'visited' })),
    highlights: [],
    edges: [...edges],
  }
}

// ════════════════════════════════════════════
// 11. Dijkstra — 最短路径
// ════════════════════════════════════════════

function* dijkstraGen(graph: GraphDef, start: number): Generator<AlgorithmStep> {
  const nodes = buildGraphNodes(graph)
  const edges = buildGraphEdges(graph)
  const adj: [number, number][][] = Array.from({ length: graph.n }, () => [])
  for (const [f, t, w] of graph.edges) {
    adj[f].push([t, w])
    if (!graph.directed) adj[t].push([f, w])
  }

  const dist: number[] = Array(graph.n).fill(Infinity)
  const visited: boolean[] = Array(graph.n).fill(false)
  const prev: (number | null)[] = Array(graph.n).fill(null)
  dist[start] = 0

  yield {
    lineNumber: 1,
    description: `从 ${graph.nodeLabels[start]} 开始，初始化距离为 0，其他为 ∞`,
    variables: { '起点': graph.nodeLabels[start], ...Object.fromEntries(graph.nodeLabels.map((l, i) => [l, i === start ? '0' : '∞'])) },
    visualType: 'graph',
    elements: nodes.map((n, i) => ({ ...n, distance: i === start ? 0 : Infinity, status: i === start ? 'current' : 'default' })),
    highlights: [start],
    edges: [...edges],
  }

  for (let round = 0; round < graph.n; round++) {
    // Find unvisited node with min distance
    let u = -1
    let minDist = Infinity
    for (let i = 0; i < graph.n; i++) {
      if (!visited[i] && dist[i] < minDist) {
        minDist = dist[i]
        u = i
      }
    }
    if (u === -1) break

    visited[u] = true

    yield {
      lineNumber: 4,
      description: `选取距离最小的未访问结点 ${graph.nodeLabels[u]}（距离=${dist[u]}）`,
      variables: { '选中': graph.nodeLabels[u], 'dist': String(dist[u]) },
      visualType: 'graph',
      elements: nodes.map((n, i) => ({
        ...n,
        distance: dist[i],
        status: i === u ? 'current' : visited[i] ? 'visited' : 'default',
      })),
      highlights: [u],
      edges: [...edges],
    }

    // Relax edges
    for (const [v, w] of adj[u]) {
      if (!visited[v]) {
        yield {
          lineNumber: 7,
          description: `检查边 ${graph.nodeLabels[u]}→${graph.nodeLabels[v]}（权重 ${w}），当前 dist[${graph.nodeLabels[v]}]=${dist[v] === Infinity ? '∞' : dist[v]}`,
          variables: { '考察': `${graph.nodeLabels[u]}→${graph.nodeLabels[v]}`, '权': String(w), '原距离': dist[v] === Infinity ? '∞' : String(dist[v]) },
          visualType: 'graph',
          elements: nodes.map((n, i) => ({ ...n, distance: dist[i], status: i === v ? 'visiting' : visited[i] ? 'visited' : i === u ? 'current' : 'default' })),
          highlights: [u, v],
          edges: edges.map(e => e.from === u && e.to === v || e.to === u && e.from === v ? { ...e, status: 'considered' as const } : e),
        }

        if (dist[u] + w < dist[v]) {
          const oldDist = dist[v]
          dist[v] = dist[u] + w
          prev[v] = u
          yield {
            lineNumber: 8,
            description: `${dist[u]} + ${w} = ${dist[v]} < ${oldDist === Infinity ? '∞' : oldDist}，更新 dist[${graph.nodeLabels[v]}] = ${dist[v]}`,
            variables: { '更新': graph.nodeLabels[v], '新距离': String(dist[v]) },
            visualType: 'graph',
            elements: nodes.map((n, i) => ({ ...n, distance: dist[i], status: i === v ? 'visiting' : visited[i] ? 'visited' : 'default' })),
            highlights: [v],
            edges: edges.map(e => e.from === u && e.to === v || e.to === u && e.from === v ? { ...e, status: 'active' as const } : e),
          }
        }
      }
    }
  }

  // Mark shortest path edges
  const spEdges = edges.map(e => {
    const isSp = prev[e.from] === e.to || prev[e.to] === e.from
    return { ...e, status: isSp ? 'shortest' as const : 'default' as const }
  })

  yield {
    lineNumber: 1,
    description: `Dijkstra 完成！最短距离：[${dist.map((d, i) => `${graph.nodeLabels[i]}:${d === Infinity ? '∞' : d}`).join(', ')}]`,
    variables: Object.fromEntries(graph.nodeLabels.map((l, i) => [l, dist[i] === Infinity ? '∞' : String(dist[i])])),
    visualType: 'graph',
    elements: nodes.map((n, i) => ({ ...n, distance: dist[i], status: 'visited' })),
    highlights: [],
    edges: spEdges,
  }
}

// ════════════════════════════════════════════
// 12. Build Max Heap — 建堆
// ════════════════════════════════════════════

function* buildMaxHeapGen(arr: number[]): Generator<AlgorithmStep> {
  const els = makeEls(arr)
  const n = arr.length

  yield {
    lineNumber: 1,
    description: `初始数组：[${arr.join(', ')}]，开始建大根堆`,
    variables: { 'n': String(n) },
    visualType: 'heap',
    elements: cloneArr(els),
    highlights: [],
  }

  // Start from last non-leaf node
  for (let i = Math.floor(n / 2) - 1; i >= 0; i--) {
    yield* heapifyGen(els, n, i, String(i))
  }

  yield {
    lineNumber: 1,
    description: `建堆完成：[${els.map(e => e.value).join(', ')}]`,
    variables: { '结果': '大根堆' },
    visualType: 'heap',
    elements: els.map(e => ({ ...e, status: 'sorted' })),
    highlights: [],
  }
}

function* heapifyGen(els: ArrayElement[], n: number, i: number, label: string): Generator<AlgorithmStep> {
  let largest = i
  const left = 2 * i + 1
  const right = 2 * i + 2

  yield {
    lineNumber: 3,
    description: `调整以 arr[${i}]=${els[i].value} 为根的子树`,
    variables: { '根': `arr[${i}]=${els[i].value}`, '左子': left < n ? `arr[${left}]=${els[left].value}` : '无', '右子': right < n ? `arr[${right}]=${els[right].value}` : '无' },
    visualType: 'heap',
    elements: markArr(els, [i], 'pivot'),
    highlights: [i, left, right].filter(x => x < n),
  }

  if (left < n && els[left].value > els[largest].value) {
    largest = left
  }
  if (right < n && els[right].value > els[largest].value) {
    largest = right
  }

  if (largest !== i) {
    yield {
      lineNumber: 6,
      description: `${els[i].value} < ${els[largest].value}，交换 arr[${i}] 与 arr[${largest}]`,
      variables: { '交换': `${els[i].value} ↔ ${els[largest].value}` },
      visualType: 'heap',
      elements: markArr(els, [i, largest], 'swapped'),
      highlights: [i, largest],
    }
    ;[els[i], els[largest]] = [els[largest], els[i]]
    yield* heapifyGen(els, n, largest, `${label}→${largest}`)
  } else {
    yield {
      lineNumber: 8,
      description: `arr[${i}]=${els[i].value} 已满足大根堆性质`,
      variables: { '稳定': `arr[${i}]` },
      visualType: 'heap',
      elements: markArr(els, [i], 'sorted'),
      highlights: [i],
    }
  }
}

// ════════════════════════════════════════════
// Default Graphs
// ════════════════════════════════════════════

const defaultGraph: GraphDef = {
  n: 6,
  nodeLabels: ['A', 'B', 'C', 'D', 'E', 'F'],
  edges: [[0, 1, 4], [0, 2, 2], [1, 2, 1], [1, 3, 5], [2, 3, 8], [2, 4, 10], [3, 4, 2], [3, 5, 6], [4, 5, 3]],
  directed: false,
}

function parseGraphInput(raw: string): GraphDef {
  try {
    return JSON.parse(raw)
  } catch {
    return defaultGraph
  }
}

// ════════════════════════════════════════════
// Algorithm Registry
// ════════════════════════════════════════════

export const algorithmRegistry: AlgorithmDef[] = [
  {
    id: 'bubble-sort',
    name: '冒泡排序',
    category: 'sorting',
    description: '相邻元素两两比较，每轮将最大元素"浮"到末尾',
    timeComplexity: 'O(n²)',
    pseudocode: [
      'for i ← 0 to n-2 do',
      '  for j ← 0 to n-2-i do',
      '    if arr[j] > arr[j+1] then',
      '      交换 arr[j] 和 arr[j+1]',
      '    end if',
      '  end for',
      '  // arr[n-1-i] 已归位',
      'end for',
    ],
    defaultInput: JSON.stringify({ arr: [5, 2, 9, 1, 5, 6] }),
    inputLabel: '数组（逗号分隔）',
    inputHint: '输入数字用逗号分隔，如：5,2,9,1,5,6',
    generateSteps: (input: unknown) => {
      const { arr } = input as { arr: number[] }
      return bubbleSortGen(arr)
    },
  },
  {
    id: 'quick-sort',
    name: '快速排序',
    category: 'sorting',
    description: '选取基准 pivot，分区递归排序',
    timeComplexity: 'O(n log n)',
    pseudocode: [
      'function QuickSort(arr, low, high)',
      '  if low ≥ high then return',
      '  pivot ← arr[high]',
      '  分区：将 arr 分为 ≤pivot 和 >pivot',
      '  for j ← low to high-1 do',
      '    if arr[j] ≤ pivot then',
      '      交换 arr[i] 和 arr[j]',
      '    end if',
      '  end for',
      '  交换 arr[i+1] 和 arr[high]',
      '  QuickSort(arr, low, i)',
      '  QuickSort(arr, i+2, high)',
      'end function',
    ],
    defaultInput: JSON.stringify({ arr: [3, 7, 8, 5, 2, 1, 9, 4] }),
    inputLabel: '数组（逗号分隔）',
    inputHint: '输入数字用逗号分隔，如：3,7,8,5,2,1,9,4',
    generateSteps: (input: unknown) => {
      const { arr } = input as { arr: number[] }
      return quickSortGen(arr)
    },
  },
  {
    id: 'binary-search',
    name: '二分查找',
    category: 'searching',
    description: '在有序数组中折半查找目标值',
    timeComplexity: 'O(log n)',
    pseudocode: [
      'function BinarySearch(arr, target)',
      '  low ← 0, high ← n-1',
      '  while low ≤ high do',
      '    mid ← ⌊(low + high) / 2⌋',
      '    if arr[mid] = target then',
      '      return mid',
      '    else if arr[mid] < target then',
      '      low ← mid + 1',
      '    else',
      '      high ← mid - 1',
      '    end if',
      '  end while',
      '  return -1',
      'end function',
    ],
    defaultInput: JSON.stringify({ arr: [1, 3, 5, 7, 9, 11, 13, 15], target: 7 }),
    inputLabel: '有序数组 + 目标值',
    inputHint: '数组（逗号分隔）和查找目标，如：数组 1,3,5,7,9,11,13,15 查找 7',
    generateSteps: (input: unknown) => {
      const { arr, target } = input as { arr: number[]; target: number }
      return binarySearchGen(arr, target)
    },
  },
  {
    id: 'linked-list-delete',
    name: '链表删除',
    category: 'linked-list',
    description: '删除链表中所有值为 x 的结点',
    timeComplexity: 'O(n)',
    pseudocode: [
      'pre ← 哨兵头结点',
      'cur ← 第一个数据结点',
      'while cur ≠ NULL do',
      '  if cur.val = x then',
      '    pre.next ← cur.next  // 删除cur',
      '  else',
      '    pre ← cur',
      '  end if',
      '  cur ← cur.next',
      'end while',
    ],
    defaultInput: JSON.stringify({ values: [1, 2, 6, 3, 4, 5, 6], x: 6 }),
    inputLabel: '链表值 + 要删除的值',
    inputHint: '链表值（逗号分隔）和要删除的值，如：链表 1,2,6,3,4,5,6 删除 6',
    generateSteps: (input: unknown) => {
      const { values, x } = input as { values: number[]; x: number }
      return linkedListDeleteGen(values, x)
    },
  },
  {
    id: 'preorder',
    name: '先序遍历',
    category: 'tree',
    description: '根 → 左 → 右 顺序遍历二叉树',
    timeComplexity: 'O(n)',
    pseudocode: [
      'function PreOrder(root)',
      '  if root = NULL then return',
      '  visit(root)',
      '  PreOrder(root.left)',
      '  PreOrder(root.right)',
      'end function',
    ],
    defaultInput: JSON.stringify({
      value: 1,
      left: { value: 2, left: { value: 4, left: null, right: null }, right: { value: 5, left: null, right: null } },
      right: { value: 3, left: { value: 6, left: null, right: null }, right: { value: 7, left: null, right: null } },
    }),
    inputLabel: '二叉树（JSON结构）',
    inputHint: '使用 JSON 结构：{value:1, left:{value:2,...}, right:{value:3,...}}',
    generateSteps: (input: unknown) => preorderGen(input as TreeNodeData),
  },
  {
    id: 'inorder',
    name: '中序遍历',
    category: 'tree',
    description: '左 → 根 → 右 顺序遍历二叉树',
    timeComplexity: 'O(n)',
    pseudocode: [
      'function InOrder(root)',
      '  if root = NULL then return',
      '  InOrder(root.left)',
      '  visit(root)',
      '  InOrder(root.right)',
      'end function',
    ],
    defaultInput: JSON.stringify({
      value: 4,
      left: { value: 2, left: { value: 1, left: null, right: null }, right: { value: 3, left: null, right: null } },
      right: { value: 6, left: { value: 5, left: null, right: null }, right: { value: 7, left: null, right: null } },
    }),
    inputLabel: '二叉树（JSON结构）',
    inputHint: '使用 JSON 结构描述二叉树',
    generateSteps: (input: unknown) => inorderGen(input as TreeNodeData),
  },
  {
    id: 'levelorder',
    name: '层序遍历',
    category: 'tree',
    description: '逐层从上到下、从左到右遍历二叉树',
    timeComplexity: 'O(n)',
    pseudocode: [
      'function LevelOrder(root)',
      '  queue ← [root]',
      '  while queue 非空 do',
      '    node ← queue 出队',
      '    visit(node)',
      '    if node.left then 入队(node.left)',
      '    if node.right then 入队(node.right)',
      '  end while',
      'end function',
    ],
    defaultInput: JSON.stringify({
      value: 1,
      left: { value: 2, left: { value: 4, left: null, right: null }, right: { value: 5, left: null, right: null } },
      right: { value: 3, left: { value: 6, left: null, right: null }, right: { value: 7, left: null, right: null } },
    }),
    inputLabel: '二叉树（JSON结构）',
    inputHint: '使用 JSON 结构描述二叉树',
    generateSteps: (input: unknown) => levelorderGen(input as TreeNodeData),
  },
  // ── Graph ──
  {
    id: 'dfs',
    name: 'DFS 深度优先搜索',
    category: 'graph',
    description: '栈实现，沿着一条路径走到底再回溯',
    timeComplexity: 'O(V+E)',
    pseudocode: [
      'function DFS(graph, start)',
      '  stack ← [start]',
      '  while stack 非空 do',
      '    v ← stack.pop()',
      '    if v 未访问 then',
      '      标记 v 已访问',
      '      for each w in adj[v] do',
      '        if w 未访问 then stack.push(w)',
      '      end for',
      '    end if',
      '  end while',
      'end function',
    ],
    defaultInput: JSON.stringify(defaultGraph),
    inputLabel: '图结构（JSON）',
    inputHint: '{ n: 6, nodeLabels: ["A","B",...], edges: [[from,to,weight],...], directed: false }',
    generateSteps: (input: unknown) => {
      const g = input as GraphDef
      return dfsGen(g, 0)
    },
  },
  {
    id: 'bfs',
    name: 'BFS 广度优先搜索',
    category: 'graph',
    description: '队列实现，逐层扩展访问',
    timeComplexity: 'O(V+E)',
    pseudocode: [
      'function BFS(graph, start)',
      '  queue ← [start]',
      '  标记 start 已访问',
      '  while queue 非空 do',
      '    v ← queue.dequeue()',
      '    访问 v',
      '    for each w in adj[v] do',
      '      if w 未访问 then',
      '        标记 w 已访问',
      '        queue.enqueue(w)',
      '      end if',
      '    end for',
      '  end while',
      'end function',
    ],
    defaultInput: JSON.stringify(defaultGraph),
    inputLabel: '图结构（JSON）',
    inputHint: '{ n: 6, nodeLabels: ["A","B",...], edges: [[from,to,weight],...], directed: false }',
    generateSteps: (input: unknown) => {
      const g = input as GraphDef
      return bfsGen(g, 0)
    },
  },
  {
    id: 'dijkstra',
    name: 'Dijkstra 最短路径',
    category: 'graph',
    description: '贪心策略，逐步确定最短距离',
    timeComplexity: 'O(V²)',
    pseudocode: [
      'function Dijkstra(graph, start)',
      '  dist[v] ← ∞, dist[start] ← 0',
      '  while 存在未访问结点 do',
      '    u ← 距离最小的未访问结点',
      '    标记 u 已访问',
      '    for each 邻接边 (u,v,w) do',
      '      if dist[u] + w < dist[v] then',
      '        dist[v] ← dist[u] + w',
      '      end if',
      '    end for',
      '  end while',
      'end function',
    ],
    defaultInput: JSON.stringify(defaultGraph),
    inputLabel: '图结构（JSON）',
    inputHint: '{ n: 6, nodeLabels: ["A","B",...], edges: [[from,to,weight],...], directed: false }',
    generateSteps: (input: unknown) => {
      const g = input as GraphDef
      return dijkstraGen(g, 0)
    },
  },
  // ── Heap ──
  {
    id: 'build-heap',
    name: '建堆（Build Max Heap）',
    category: 'heap',
    description: '从最后一个非叶结点开始，自底向上调整',
    timeComplexity: 'O(n)',
    pseudocode: [
      'function BuildMaxHeap(arr)',
      '  for i ← ⌊n/2⌋-1 downto 0 do',
      '    Heapify(arr, n, i)',
      '  end for',
      '',
      'function Heapify(arr, n, i)',
      '  largest ← i',
      '  l ← 2i+1, r ← 2i+2',
      '  if l < n and arr[l] > arr[largest] then largest ← l',
      '  if r < n and arr[r] > arr[largest] then largest ← r',
      '  if largest ≠ i then',
      '    交换 arr[i] 和 arr[largest]',
      '    Heapify(arr, n, largest)',
      '  end if',
      'end function',
    ],
    defaultInput: JSON.stringify({ arr: [4, 10, 3, 5, 1, 7, 8] }),
    inputLabel: '数组（逗号分隔）',
    inputHint: '输入数字用逗号分隔，如：4,10,3,5,1,7,8',
    generateSteps: (input: unknown) => {
      const { arr } = input as { arr: number[] }
      return buildMaxHeapGen(arr)
    },
  },
]

export function getAlgorithmById(id: string): AlgorithmDef | undefined {
  return algorithmRegistry.find(a => a.id === id)
}

export function getAlgorithmsByCategory(): Record<AlgoCategory, AlgorithmDef[]> {
  const map: Record<string, AlgorithmDef[]> = {}
  for (const algo of algorithmRegistry) {
    if (!map[algo.category]) map[algo.category] = []
    map[algo.category].push(algo)
  }
  return map
}

export const categoryLabels: Record<AlgoCategory, string> = {
  'sorting': '排序',
  'searching': '查找',
  'linked-list': '链表',
  'tree': '二叉树',
  'graph': '图',
  'heap': '堆',
}
