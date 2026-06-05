// 408 历年真题链接 — 按算法分类
export interface ExamQuestion {
  year: number
  number: number
  description: string
  answer?: string
}

export const examQuestions: Record<string, ExamQuestion[]> = {
  'bubble-sort': [
    { year: 2010, number: 41, description: '直接插入排序，分析比较次数与移动次数' },
    { year: 2016, number: 10, description: '冒泡排序过程中元素状态变化' },
  ],
  'quick-sort': [
    { year: 2011, number: 10, description: '快速排序的递归深度与基准选择关系' },
    { year: 2013, number: 10, description: '快速排序第一趟划分结果' },
    { year: 2019, number: 10, description: '快速排序在基本有序数组上的性能' },
  ],
  'binary-search': [
    { year: 2012, number: 9, description: '折半查找判定树与查找长度分析' },
    { year: 2015, number: 9, description: '二分查找的平均查找长度 ASL' },
    { year: 2020, number: 9, description: '有序表折半查找的比较路径' },
  ],
  'linked-list-delete': [
    { year: 2010, number: 42, description: '单链表删除所有值为 x 的结点（408 真题）' },
    { year: 2014, number: 42, description: '单链表结点的查找与删除操作' },
    { year: 2021, number: 42, description: '带头结点单链表的就地逆置' },
  ],
  'preorder': [
    { year: 2011, number: 6, description: '根据遍历序列构造二叉树' },
    { year: 2017, number: 6, description: '先序 + 中序确定二叉树结构' },
  ],
  'inorder': [
    { year: 2012, number: 6, description: '二叉排序树的中序遍历性质' },
    { year: 2018, number: 7, description: '中序线索二叉树的遍历' },
  ],
  'levelorder': [
    { year: 2015, number: 6, description: '层序遍历与队列的关系' },
    { year: 2022, number: 6, description: '完全二叉树的层序存储与下标计算' },
  ],
  'dfs': [
    { year: 2013, number: 8, description: '图的 DFS 遍历序列与生成树' },
    { year: 2016, number: 7, description: '有向图 DFS 的强连通分量' },
    { year: 2021, number: 8, description: 'DFS 与拓扑排序的关系' },
  ],
  'bfs': [
    { year: 2012, number: 7, description: '图的 BFS 遍历与最短路径' },
    { year: 2019, number: 7, description: 'BFS 生成树与层次关系' },
  ],
  'dijkstra': [
    { year: 2014, number: 8, description: 'Dijkstra 算法求单源最短路径过程' },
    { year: 2017, number: 8, description: '最短路径与关键路径的区别' },
    { year: 2022, number: 8, description: 'Dijkstra 算法在负权边上的适用性' },
  ],
  'build-heap': [
    { year: 2011, number: 8, description: '堆的插入与删除调整过程' },
    { year: 2015, number: 8, description: '建堆过程与时间复杂度的分析' },
    { year: 2018, number: 8, description: '堆排序与选择排序的比较' },
  ],
}

export function getQuestionsForAlgo(algoId: string): ExamQuestion[] {
  return examQuestions[algoId] || []
}
