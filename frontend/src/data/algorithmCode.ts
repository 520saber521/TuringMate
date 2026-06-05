// C and Python implementations for each algorithm
export const codeMap: Record<string, { c: string; python: string }> = {
  'bubble-sort': {
    c: `void bubbleSort(int arr[], int n) {
  for (int i = 0; i < n-1; i++) {
    int swapped = 0;
    for (int j = 0; j < n-1-i; j++) {
      if (arr[j] > arr[j+1]) {
        int tmp = arr[j];
        arr[j] = arr[j+1];
        arr[j+1] = tmp;
        swapped = 1;
      }
    }
    if (!swapped) break;
  }
}`,
    python: `def bubble_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break`,
  },
  'quick-sort': {
    c: `int partition(int arr[], int low, int high) {
  int pivot = arr[high];
  int i = low - 1;
  for (int j = low; j < high; j++) {
    if (arr[j] <= pivot) {
      i++;
      int tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
    }
  }
  int tmp = arr[i+1]; arr[i+1] = arr[high]; arr[high] = tmp;
  return i + 1;
}
void quickSort(int arr[], int low, int high) {
  if (low < high) {
    int pi = partition(arr, low, high);
    quickSort(arr, low, pi - 1);
    quickSort(arr, pi + 1, high);
  }
}`,
    python: `def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

def quick_sort(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quick_sort(arr, low, pi - 1)
        quick_sort(arr, pi + 1, high)`,
  },
  'binary-search': {
    c: `int binarySearch(int arr[], int n, int target) {
  int low = 0, high = n - 1;
  while (low <= high) {
    int mid = low + (high - low) / 2;
    if (arr[mid] == target)
      return mid;
    else if (arr[mid] < target)
      low = mid + 1;
    else
      high = mid - 1;
  }
  return -1;
}`,
    python: `def binary_search(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1`,
  },
  'linked-list-delete': {
    c: `typedef struct Node {
  int val;
  struct Node *next;
} Node;

Node* deleteAllX(Node *head, int x) {
  Node dummy = {0, head};
  Node *pre = &dummy, *cur = head;
  while (cur) {
    if (cur->val == x)
      pre->next = cur->next;  // delete
    else
      pre = cur;
    cur = cur->next;
  }
  return dummy.next;
}`,
    python: `class Node:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def delete_all_x(head, x):
    dummy = Node(0, head)
    pre, cur = dummy, head
    while cur:
        if cur.val == x:
            pre.next = cur.next
        else:
            pre = cur
        cur = cur.next
    return dummy.next`,
  },
  'preorder': {
    c: `typedef struct TreeNode {
  int val;
  struct TreeNode *left, *right;
} TreeNode;

void preOrder(TreeNode *root) {
  if (!root) return;
  visit(root);
  preOrder(root->left);
  preOrder(root->right);
}`,
    python: `def pre_order(root):
    if not root:
        return
    visit(root)
    pre_order(root.left)
    pre_order(root.right)`,
  },
  'inorder': {
    c: `void inOrder(TreeNode *root) {
  if (!root) return;
  inOrder(root->left);
  visit(root);
  inOrder(root->right);
}`,
    python: `def in_order(root):
    if not root:
        return
    in_order(root.left)
    visit(root)
    in_order(root.right)`,
  },
  'levelorder': {
    c: `void levelOrder(TreeNode *root) {
  if (!root) return;
  Queue *q = createQueue();
  enqueue(q, root);
  while (!isEmpty(q)) {
    TreeNode *node = dequeue(q);
    visit(node);
    if (node->left) enqueue(q, node->left);
    if (node->right) enqueue(q, node->right);
  }
}`,
    python: `from collections import deque

def level_order(root):
    if not root:
        return
    q = deque([root])
    while q:
        node = q.popleft()
        visit(node)
        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)`,
  },
  'dfs': {
    c: `void dfs(int graph[][N], int n, int start) {
  int visited[N] = {0};
  int stack[N], top = 0;
  stack[top++] = start;
  while (top > 0) {
    int v = stack[--top];
    if (visited[v]) continue;
    visited[v] = 1;
    visit(v);
    for (int w = n-1; w >= 0; w--)
      if (graph[v][w] && !visited[w])
        stack[top++] = w;
  }
}`,
    python: `def dfs(graph, start):
    visited = set()
    stack = [start]
    while stack:
        v = stack.pop()
        if v in visited:
            continue
        visited.add(v)
        visit(v)
        for w in reversed(graph[v]):
            if w not in visited:
                stack.append(w)`,
  },
  'bfs': {
    c: `void bfs(int graph[][N], int n, int start) {
  int visited[N] = {0};
  int queue[N], front = 0, rear = 0;
  queue[rear++] = start;
  visited[start] = 1;
  while (front < rear) {
    int v = queue[front++];
    visit(v);
    for (int w = 0; w < n; w++)
      if (graph[v][w] && !visited[w]) {
        visited[w] = 1;
        queue[rear++] = w;
      }
  }
}`,
    python: `from collections import deque

def bfs(graph, start):
    visited = {start}
    q = deque([start])
    while q:
        v = q.popleft()
        visit(v)
        for w in graph[v]:
            if w not in visited:
                visited.add(w)
                q.append(w)`,
  },
  'dijkstra': {
    c: `void dijkstra(int graph[][N], int n, int start) {
  int dist[N], visited[N] = {0};
  for (int i = 0; i < n; i++) dist[i] = INT_MAX;
  dist[start] = 0;
  for (int k = 0; k < n; k++) {
    int u = -1, minD = INT_MAX;
    for (int i = 0; i < n; i++)
      if (!visited[i] && dist[i] < minD)
        u = i, minD = dist[i];
    if (u == -1) break;
    visited[u] = 1;
    for (int v = 0; v < n; v++)
      if (graph[u][v] && !visited[v])
        if (dist[u] + graph[u][v] < dist[v])
          dist[v] = dist[u] + graph[u][v];
  }
}`,
    python: `def dijkstra(graph, n, start):
    dist = [float('inf')] * n
    visited = [False] * n
    dist[start] = 0
    for _ in range(n):
        u = min((i for i in range(n) if not visited[i]),
                key=lambda i: dist[i], default=-1)
        if u == -1: break
        visited[u] = True
        for v, w in graph[u]:
            if not visited[v]:
                dist[v] = min(dist[v], dist[u] + w)`,
  },
  'build-heap': {
    c: `void heapify(int arr[], int n, int i) {
  int largest = i;
  int l = 2*i + 1, r = 2*i + 2;
  if (l < n && arr[l] > arr[largest]) largest = l;
  if (r < n && arr[r] > arr[largest]) largest = r;
  if (largest != i) {
    int tmp = arr[i]; arr[i] = arr[largest];
    arr[largest] = tmp;
    heapify(arr, n, largest);
  }
}
void buildMaxHeap(int arr[], int n) {
  for (int i = n/2 - 1; i >= 0; i--)
    heapify(arr, n, i);
}`,
    python: `def heapify(arr, n, i):
    largest = i
    l, r = 2 * i + 1, 2 * i + 2
    if l < n and arr[l] > arr[largest]:
        largest = l
    if r < n and arr[r] > arr[largest]:
        largest = r
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)

def build_max_heap(arr):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)`,
  },
}
