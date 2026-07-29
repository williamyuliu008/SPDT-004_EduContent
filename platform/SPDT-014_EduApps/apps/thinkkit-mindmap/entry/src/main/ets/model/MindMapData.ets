// ============================================================
// model/MindMapData.ets — 思维导图数据模型
// ============================================================

/** 导图节点 */
export class MindMapNode {
  id: string;
  label: string;
  children: MindMapNode[];
  expanded: boolean;
  /** 0-5 颜色标记索引: 0=无, 1=红, 2=橙, 3=黄, 4=绿, 5=蓝 */
  color: number;

  constructor(id: string, label: string) {
    this.id = id;
    this.label = label;
    this.children = [];
    this.expanded = true;
    this.color = 0;
  }
}

/** 颜色标记色板 */
export const COLOR_PALETTE: string[] = [
  '#FFFFFF', // 0 - 无色
  '#FF6B6B', // 1 - 红
  '#FFA94D', // 2 - 橙
  '#FFD43B', // 3 - 黄
  '#69DB7C', // 4 - 绿
  '#74C0FC', // 5 - 蓝
];

/** 颜色名称 */
export const COLOR_NAMES: string[] = ['无', '红', '橙', '黄', '绿', '蓝'];

/** 导图引擎: 管理节点树、选择状态、导出 */
export class MindMapEngine {
  root: MindMapNode;
  selectedNodeId: string;
  private nodeIdCounter: number;

  constructor(rootLabel: string) {
    this.nodeIdCounter = 0;
    this.selectedNodeId = '';
    this.root = new MindMapNode(this.nextId(), rootLabel);
    // 预置示例子节点
    this.root.children.push(new MindMapNode(this.nextId(), '子主题 1'));
    let sub2 = new MindMapNode(this.nextId(), '子主题 2');
    sub2.children.push(new MindMapNode(this.nextId(), '孙主题 2.1'));
    sub2.children.push(new MindMapNode(this.nextId(), '孙主题 2.2'));
    this.root.children.push(sub2);
    this.root.children.push(new MindMapNode(this.nextId(), '子主题 3'));
  }

  private nextId(): string {
    return 'node_' + (++this.nodeIdCounter);
  }

  /** 根据ID查找节点(递归) */
  findNode(id: string, node?: MindMapNode): MindMapNode | null {
    let current = node ?? this.root;
    if (current.id === id) {
      return current;
    }
    for (let child of current.children) {
      let found = this.findNode(id, child);
      if (found !== null) {
        return found;
      }
    }
    return null;
  }

  /** 根据ID查找父节点 */
  findParent(id: string, node?: MindMapNode, parent?: MindMapNode): MindMapNode | null {
    let current = node ?? this.root;
    let p = parent ?? null;
    if (current.id === id) {
      return p;
    }
    for (let child of current.children) {
      let found = this.findParent(id, child, current);
      if (found !== null) {
        return found;
      }
    }
    return null;
  }

  /** 添加子节点 */
  addChild(parentId: string, label: string): MindMapNode | null {
    let parent = this.findNode(parentId);
    if (parent !== null) {
      let child = new MindMapNode(this.nextId(), label);
      parent.children.push(child);
      parent.expanded = true;
      return child;
    }
    return null;
  }

  /** 删除节点(不能删根) */
  deleteNode(id: string): boolean {
    if (id === this.root.id) {
      return false;
    }
    let parent = this.findParent(id);
    if (parent !== null) {
      let idx = parent.children.findIndex((n: MindMapNode) => n.id === id);
      if (idx >= 0) {
        parent.children.splice(idx, 1);
        if (this.selectedNodeId === id) {
          this.selectedNodeId = '';
        }
        return true;
      }
    }
    return false;
  }

  /** 修改节点文本 */
  setLabel(id: string, label: string): void {
    let node = this.findNode(id);
    if (node !== null) {
      node.label = label;
    }
  }

  /** 切换展开/折叠 */
  toggleExpand(id: string): void {
    let node = this.findNode(id);
    if (node !== null && node.children.length > 0) {
      node.expanded = !node.expanded;
    }
  }

  /** 设置颜色标记 */
  setColor(id: string, color: number): void {
    let node = this.findNode(id);
    if (node !== null) {
      node.color = color % COLOR_PALETTE.length;
    }
  }

  /** 计算节点可见深度(展开路径上的深度) */
  getVisibleDepth(id: string): number {
    let depth = 0;
    let current = this.findNode(id);
    while (current !== null && current.id !== this.root.id) {
      depth++;
      let parent = this.findParent(current.id);
      current = parent;
    }
    return depth;
  }

  /** 收集所有可见节点(扁平列表, 带深度和父子关系) */
  collectVisibleNodes(): VisibleNode[] {
    let result: VisibleNode[] = [];
    this.collectRecursive(this.root, 0, result);
    return result;
  }

  private collectRecursive(node: MindMapNode, depth: number, result: VisibleNode[]): void {
    result.push(new VisibleNode(node, depth));
    if (node.expanded) {
      for (let child of node.children) {
        this.collectRecursive(child, depth + 1, result);
      }
    }
  }

  /** 导出为文本大纲 */
  exportOutline(): string {
    let lines: string[] = [];
    this.exportRecursive(this.root, 0, lines);
    return lines.join('\n');
  }

  private exportRecursive(node: MindMapNode, indent: number, lines: string[]): void {
    let prefix = '  '.repeat(indent);
    let colorTag = node.color > 0 ? ' [' + COLOR_NAMES[node.color] + ']' : '';
    lines.push(prefix + '- ' + node.label + colorTag);
    if (node.expanded) {
      for (let child of node.children) {
        this.exportRecursive(child, indent + 1, lines);
      }
    }
  }
}

/** 可见节点(带渲染深度) */
export class VisibleNode {
  node: MindMapNode;
  depth: number;

  constructor(node: MindMapNode, depth: number) {
    this.node = node;
    this.depth = depth;
  }
}
