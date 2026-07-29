/**
 * Question.ts — ThinkKit Quiz 测验数据模型
 *
 * 定义题目结构、选项、答题记录和计分逻辑。
 */

/** 选项 */
export class Option {
  id: string;
  text: string;

  constructor(id: string, text: string) {
    this.id = id;
    this.text = text;
  }
}

/** 题目 */
export class Question {
  id: string;
  category: string;
  question: string;
  options: Option[];
  correctId: string;
  explanation: string;

  constructor(
    id: string,
    category: string,
    question: string,
    options: Option[],
    correctId: string,
    explanation: string
  ) {
    this.id = id;
    this.category = category;
    this.question = question;
    this.options = options;
    this.correctId = correctId;
    this.explanation = explanation;
  }
}

/** 答题记录 */
export class AnswerRecord {
  questionId: string;
  selectedId: string;
  isCorrect: boolean;

  constructor(questionId: string, selectedId: string, isCorrect: boolean) {
    this.questionId = questionId;
    this.selectedId = selectedId;
    this.isCorrect = isCorrect;
  }
}

/** 测验结果 */
export class QuizResult {
  totalQuestions: number;
  correctCount: number;
  wrongCount: number;
  skippedCount: number;
  timeUsed: number;
  accuracy: number;
  records: AnswerRecord[];

  constructor(
    totalQuestions: number,
    correctCount: number,
    wrongCount: number,
    skippedCount: number,
    timeUsed: number,
    accuracy: number,
    records: AnswerRecord[]
  ) {
    this.totalQuestions = totalQuestions;
    this.correctCount = correctCount;
    this.wrongCount = wrongCount;
    this.skippedCount = skippedCount;
    this.timeUsed = timeUsed;
    this.accuracy = accuracy;
    this.records = records;
  }
}

/** 示例题库 */
export const SAMPLE_QUESTIONS: Question[] = [
  new Question(
    'q1', '鸿蒙基础',
    'HarmonyOS 使用的编程语言是？',
    [
      new Option('a', 'Kotlin'),
      new Option('b', 'ArkTS'),
      new Option('c', 'Swift'),
      new Option('d', 'Dart'),
    ],
    'b',
    'ArkTS 是 HarmonyOS 主推的声明式 UI 编程语言，基于 TypeScript 扩展。'
  ),
  new Question(
    'q2', '鸿蒙基础',
    'HarmonyOS 应用的入口组件是？',
    [
      new Option('a', 'UIAbility'),
      new Option('b', 'Activity'),
      new Option('c', 'ViewController'),
      new Option('d', 'AppDelegate'),
    ],
    'a',
    'UIAbility 是 HarmonyOS 应用的入口点，管理界面的创建和生命周期。'
  ),
  new Question(
    'q3', 'ArkUI',
    'ArkUI 中声明响应式状态的装饰器是？',
    [
      new Option('a', '@Bind'),
      new Option('b', '@State'),
      new Option('c', '@Observe'),
      new Option('d', '@Watch'),
    ],
    'b',
    '@State 装饰器标记组件内的私有状态变量，值变化时 UI 自动更新。'
  ),
  new Question(
    'q4', 'ArkUI',
    'ArkUI 组件树中，哪个是正确的父子关系层级？',
    [
      new Option('a', 'Column > Text'),
      new Option('b', 'Text > Column'),
      new Option('c', 'Button > Row'),
      new Option('d', 'Image > Column'),
    ],
    'a',
    'Column 是容器组件，Text 是基础组件，Column 可以作为 Text 的父容器。'
  ),
  new Question(
    'q5', '鸿蒙基础',
    'HarmonyOS 应用的包后缀格式是？',
    [
      new Option('a', '.apk'),
      new Option('b', '.hap'),
      new Option('c', '.ipa'),
      new Option('d', '.app'),
    ],
    'b',
    'HAP (HarmonyOS Ability Package) 是鸿蒙应用的安装包格式。'
  ),
  new Question(
    'q6', '开发工具',
    'HarmonyOS 官方 IDE 是？',
    [
      new Option('a', 'Android Studio'),
      new Option('b', 'Xcode'),
      new Option('c', 'DevEco Studio'),
      new Option('d', 'VS Code'),
    ],
    'c',
    'DevEco Studio 是华为提供的 HarmonyOS 一站式开发环境。'
  ),
  new Question(
    'q7', 'ArkUI',
    '以下哪个不是 ArkUI 的布局组件？',
    [
      new Option('a', 'Row'),
      new Option('b', 'Stack'),
      new Option('c', 'Grid'),
      new Option('d', 'Fragment'),
    ],
    'd',
    'Fragment 是 Android 的概念。ArkUI 布局组件包括 Row、Column、Stack、Grid、Flex 等。'
  ),
  new Question(
    'q8', '鸿蒙基础',
    'HarmonyOS NEXT 中跨设备流转需要哪个能力？',
    [
      new Option('a', 'Intent'),
      new Option('b', 'Distributed'),
      new Option('c', 'AppLink'),
      new Option('d', 'URLScheme'),
    ],
    'b',
    'HarmonyOS 的分布式能力（Distributed）是实现跨设备协同的核心。'
  ),
  new Question(
    'q9', '数据存储',
    'HarmonyOS 轻量级 KV 存储使用的 API 是？',
    [
      new Option('a', 'SharedPreferences'),
      new Option('b', 'UserDefaults'),
      new Option('c', 'Preferences'),
      new Option('d', 'NSUserDefaults'),
    ],
    'c',
    'HarmonyOS 使用 @ohos.data.preferences 模块进行轻量级 KV 存储。'
  ),
  new Question(
    'q10', '开发工具',
    '鸿蒙应用上架到哪个平台？',
    [
      new Option('a', 'Google Play'),
      new Option('b', 'App Store'),
      new Option('c', 'AppGallery'),
      new Option('d', 'Galaxy Store'),
    ],
    'c',
    'AppGallery（华为应用市场）是鸿蒙应用的分发平台。'
  ),
];
