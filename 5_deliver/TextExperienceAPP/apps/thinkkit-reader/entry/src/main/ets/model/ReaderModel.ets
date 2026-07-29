// ============================================================
// model/ReaderModel.ets — 深度阅读器数据模型
// ============================================================

/**
 * 书籍记录
 */
export class BookRecord {
  id: string;            // 唯一 ID
  title: string;         // 书名（从文件名/标题推导）
  fileUri: string;       // 文件 URI
  fileType: string;      // 'txt' | 'md' | 'markdown'
  totalChars: number;    // 总字符数
  progress: number;      // 阅读进度 (0-1)
  lastReadChar: number;  // 上次读到第几个字符
  addTime: number;       // 添加时间戳
  coverColor: string;    // 封面颜色（预设色板循环）

  constructor(id: string, title: string, fileUri: string, fileType: string, totalChars: number) {
    this.id = id;
    this.title = title;
    this.fileUri = fileUri;
    this.fileType = fileType;
    this.totalChars = totalChars;
    this.progress = 0;
    this.lastReadChar = 0;
    this.addTime = Date.now();
    this.coverColor = BOOK_COVER_COLORS[Math.floor(Math.random() * BOOK_COVER_COLORS.length)];
  }
}

/** 书架封面色板 */
export const BOOK_COVER_COLORS: string[] = [
  '#5B8C5A', '#4A90D9', '#E67E22', '#9B59B6',
  '#1ABC9C', '#E74C3C', '#3498DB', '#F39C12',
];

/** 章节信息 */
export class Chapter {
  index: number;       // 章节序号（从0开始）
  title: string;       // 章节标题
  startChar: number;   // 起始字符位置
  endChar: number;     // 结束字符位置
  level: number;       // 标题级别 (1-3)

  constructor(index: number, title: string, startChar: number, endChar: number, level: number = 1) {
    this.index = index;
    this.title = title;
    this.startChar = startChar;
    this.endChar = endChar;
    this.level = level;
  }
}

/**
 * 摘录/批注
 */
export class Annotation {
  id: string;           // 唯一 ID
  bookId: string;       // 所属书籍 ID
  chapterIndex: number; // 所属章节
  selectedText: string; // 选中原文
  note: string;         // 批注文字
  charStart: number;    // 原文起始字符位置
  charEnd: number;      // 原文结束字符位置
  color: string;        // 高亮颜色
  createTime: number;   // 创建时间

  constructor(
    id: string, bookId: string, chapterIndex: number,
    selectedText: string, note: string,
    charStart: number, charEnd: number,
  ) {
    this.id = id;
    this.bookId = bookId;
    this.chapterIndex = chapterIndex;
    this.selectedText = selectedText;
    this.note = note;
    this.charStart = charStart;
    this.charEnd = charEnd;
    this.color = ANNOTATION_COLORS[Math.floor(Math.random() * ANNOTATION_COLORS.length)];
    this.createTime = Date.now();
  }
}

/** 批注高亮色板 */
export const ANNOTATION_COLORS: string[] = [
  '#FFEB3B80', '#FF980080', '#4CAF5080', '#2196F380', '#9C27B080',
];

/**
 * 阅读器设置
 */
export class ReaderSettings {
  fontSizeLevel: number;   // 字号档位 0=小 1=中 2=大
  nightMode: boolean;      // 夜间模式
  fontFamily: string;      // 字体（暂用默认）

  constructor() {
    this.fontSizeLevel = 1;  // 默认中号
    this.nightMode = false;
    this.fontFamily = '';
  }
}

/**
 * 阅读进度记录
 */
export class ReadingProgress {
  bookId: string;
  chapterIndex: number;
  charOffset: number;    // 当前章节内字符偏移
  globalCharPos: number; // 全书字符位置
  percentage: number;    // 百分比 0-100
  updateTime: number;

  constructor(bookId: string) {
    this.bookId = bookId;
    this.chapterIndex = 0;
    this.charOffset = 0;
    this.globalCharPos = 0;
    this.percentage = 0;
    this.updateTime = Date.now();
  }
}

/** 字号映射 */
export const FONT_SIZE_MAP: Record<number, number> = {
  0: 14,  // 小
  1: 18,  // 中
  2: 22,  // 大
};

export const FONT_SIZE_LABELS: Record<number, string> = {
  0: '小',
  1: '中',
  2: '大',
};
