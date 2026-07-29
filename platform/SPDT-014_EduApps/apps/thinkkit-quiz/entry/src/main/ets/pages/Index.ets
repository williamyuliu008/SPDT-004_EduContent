/**
 * Index.ets — ThinkKit Quiz 互动测验主页
 *
 * 功能：选择测验类别 → 限时答题 → 交卷打分
 * 品牌色：ThinkKit 森绿 #5B8C5A
 */

import { AppConfig } from '../app.config';
import {
  Question, Option, AnswerRecord, QuizResult,
  SAMPLE_QUESTIONS
} from '../model/Question';

/** 测验状态 */
enum QuizState {
  HOME,
  ANSWERING,
  RESULT,
}

@Entry
@Component
struct Index {
  @Provide('navPathStack') navPathStack: NavPathStack = new NavPathStack();
  @State quizState: QuizState = QuizState.HOME;
  @State currentIndex: number = 0;
  @State selectedOptionId: string = '';
  @State timeRemaining: number = AppConfig.defaultQuizTime;
  @State answers: AnswerRecord[] = [];
  @State quizResult: QuizResult = new QuizResult(0, 0, 0, 0, 0, 0, []);
  @State questionProgress: number = 0;
  @State showExplanation: boolean = false;
  private timerId: number = -1;

  /** 当前题目 */
  private get currentQuestion(): Question {
    return SAMPLE_QUESTIONS[this.currentIndex];
  }

  build() {
    Navigation(this.navPathStack) {
      Column() {
        if (this.quizState === QuizState.HOME) {
          this.buildHomeScreen()
        } else if (this.quizState === QuizState.ANSWERING) {
          this.buildQuizScreen()
        } else if (this.quizState === QuizState.RESULT) {
          // 嵌入 ResultPage
          this.buildResultScreen()
        }
      }
      .width('100%')
      .height('100%')
      .backgroundColor(AppConfig.bgColor)
    }
    .hideTitleBar(true)
    .navBarWidth('0')
    .mode(NavigationMode.Stack)
  }

  // ==================== 首页 ====================
  @Builder buildHomeScreen() {
    Column() {
      // 头部
      Column() {
        Column() {
          Text('📝')
            .fontSize(40)
            .margin({ bottom: 8 })
          Text(AppConfig.appName)
            .fontSize(24)
            .fontWeight(700)
            .fontColor('#FFFFFF')
          Text(AppConfig.shortDesc)
            .fontSize(14)
            .fontColor('#FFFFFF')
            .opacity(0.8)
            .margin({ top: 4 })
        }
        .width('100%')
        .alignItems(HorizontalAlign.Center)
      }
      .width('100%')
      .padding({ top: 60, bottom: 40 })
      .backgroundColor(AppConfig.primaryColor)

      Scroll() {
        Column({ space: 14 }) {
          // 测验信息卡片
          Column() {
            Row() {
              Text('📊')
                .fontSize(20)
              Text('本次测验')
                .fontSize(16)
                .fontWeight(600)
                .fontColor(AppConfig.textPrimary)
                .margin({ left: 8 })
            }
            .width('100%')
            .margin({ bottom: 12 })

            Row() {
              Column({ space: 4 }) {
                Text(SAMPLE_QUESTIONS.length.toString())
                  .fontSize(20)
                  .fontWeight(700)
                  .fontColor(AppConfig.primaryColor)
                Text('题目数量')
                  .fontSize(11)
                  .fontColor(AppConfig.textSecondary)
              }
              .layoutWeight(1)
              .alignItems(HorizontalAlign.Center)

              Column({ space: 4 }) {
                Text(AppConfig.defaultQuizTime + 's')
                  .fontSize(20)
                  .fontWeight(700)
                  .fontColor(AppConfig.primaryColor)
                Text('限时')
                  .fontSize(11)
                  .fontColor(AppConfig.textSecondary)
              }
              .layoutWeight(1)
              .alignItems(HorizontalAlign.Center)

              Column({ space: 4 }) {
                Text('10题')
                  .fontSize(20)
                  .fontWeight(700)
                  .fontColor(AppConfig.primaryColor)
                Text('多选一')
                  .fontSize(11)
                  .fontColor(AppConfig.textSecondary)
              }
              .layoutWeight(1)
              .alignItems(HorizontalAlign.Center)
            }
          }
          .width('100%')
          .padding(18)
          .backgroundColor(AppConfig.cardBg)
          .borderRadius(AppConfig.radius)
          .border({ width: 1, color: AppConfig.cardBorder })

          // 学习技巧
          Column() {
            Text('💡 答题技巧')
              .fontSize(15)
              .fontWeight(600)
              .fontColor(AppConfig.textPrimary)
              .margin({ bottom: 10 })
              .alignSelf(ItemAlign.Start)

            Column({ space: 8 }) {
              Row() {
                Text('•')
                  .fontSize(14)
                  .fontColor(AppConfig.primaryColor)
                  .width(20)
                Text('每题选择后自动进入下一题')
                  .fontSize(13)
                  .fontColor(AppConfig.textSecondary)
                  .layoutWeight(1)
              }

              Row() {
                Text('•')
                  .fontSize(14)
                  .fontColor(AppConfig.primaryColor)
                  .width(20)
                Text('时间耗尽将自动交卷')
                  .fontSize(13)
                  .fontColor(AppConfig.textSecondary)
                  .layoutWeight(1)
              }

              Row() {
                Text('•')
                  .fontSize(14)
                  .fontColor(AppConfig.primaryColor)
                  .width(20)
                Text('答完后可查看详细解析')
                  .fontSize(13)
                  .fontColor(AppConfig.textSecondary)
                  .layoutWeight(1)
              }

              Row() {
                Text('•')
                  .fontSize(14)
                  .fontColor(AppConfig.primaryColor)
                  .width(20)
                Text('正确率 ≥ 60% 为通过')
                  .fontSize(13)
                  .fontColor(AppConfig.textSecondary)
                  .layoutWeight(1)
              }
            }
          }
          .width('100%')
          .padding(18)
          .backgroundColor(AppConfig.cardBg)
          .borderRadius(AppConfig.radius)
          .border({ width: 1, color: AppConfig.cardBorder })

          // 开始按钮
          Button('🚀 开始答题')
            .fontSize(17)
            .fontWeight(600)
            .width('100%')
            .height(52)
            .borderRadius(AppConfig.radius)
            .backgroundColor(AppConfig.primaryColor)
            .fontColor('#FFFFFF')
            .shadow({ radius: 8, color: '#5B8C5A40', offsetX: 0, offsetY: 4 })
            .onClick(() => { this.startQuiz(); })

          Blank().height(20)
        }
        .width('100%')
        .padding({ left: 16, right: 16, top: 16 })
      }
      .layoutWeight(1)
    }
    .width('100%')
    .height('100%')
  }

  // ==================== 答题界面 ====================
  @Builder buildQuizScreen() {
    Column() {
      // 顶部：进度 + 计时
      Column() {
        // 进度条
        Row() {
          Row()
            .height(4)
            .borderRadius(2)
            .backgroundColor(AppConfig.primaryColor)
            .width((this.currentIndex / SAMPLE_QUESTIONS.length * 100).toString() + '%')
        }
        .width('100%')
        .height(4)
        .backgroundColor('#E0E8E0')
        .borderRadius(2)

        Row() {
          // 题号
          Text('第 ' + (this.currentIndex + 1) + ' / ' + SAMPLE_QUESTIONS.length + ' 题')
            .fontSize(14)
            .fontColor('#FFFFFF')
            .opacity(0.9)

          Blank()

          // 计时器
          Row({ space: 4 }) {
            Text('⏱')
              .fontSize(14)
            Text(this.formatTime(this.timeRemaining))
              .fontSize(16)
              .fontWeight(700)
              .fontColor(this.timeRemaining <= AppConfig.timeWarning ? '#FF6B6B' : '#FFFFFF')
          }
        }
        .width('100%')
        .margin({ top: 10 })
      }
      .width('100%')
      .padding({ left: 16, right: 16, top: 48, bottom: 14 })
      .backgroundColor(AppConfig.primaryColor)

      // 题目区
      Scroll() {
        Column({ space: 14 }) {
          // 类别标签
          Row() {
            Text(this.currentQuestion.category)
              .fontSize(12)
              .fontColor(AppConfig.primaryColor)
              .fontWeight(600)
              .padding({ left: 10, right: 10, top: 4, bottom: 4 })
              .backgroundColor('#E8F0E8')
              .borderRadius(10)
          }
          .width('100%')

          // 题目文本
          Column() {
            Text(this.currentQuestion.question)
              .fontSize(18)
              .fontWeight(600)
              .fontColor(AppConfig.textPrimary)
              .lineHeight(26)
              .width('100%')
          }
          .width('100%')
          .padding(16)
          .backgroundColor(AppConfig.cardBg)
          .borderRadius(AppConfig.radius)
          .border({ width: 1, color: AppConfig.cardBorder })

          // 选项列表
          Column({ space: 10 }) {
            ForEach(this.currentQuestion.options, (option: Option) => {
              this.buildOptionButton(option)
            }, (option: Option) => option.id)
          }
          .width('100%')

          // 解析区（答题后显示）
          if (this.showExplanation) {
            Column() {
              Row() {
                Text(this.selectedOptionId === this.currentQuestion.correctId ? '✅ 回答正确！' : '❌ 回答错误')
                  .fontSize(14)
                  .fontWeight(600)
                  .fontColor(this.selectedOptionId === this.currentQuestion.correctId
                    ? AppConfig.correctColor : AppConfig.wrongColor)
              }
              .width('100%')
              .margin({ bottom: 8 })

              Text(this.currentQuestion.explanation)
                .fontSize(13)
                .fontColor(AppConfig.textSecondary)
                .lineHeight(20)
                .width('100%')
                .padding(12)
                .backgroundColor('#F0F6F0')
                .borderRadius(AppConfig.radiusSm)
            }
            .width('100%')
            .margin({ top: 4 })
          }

          // 导航按钮
          if (this.showExplanation) {
            Row({ space: 10 }) {
              if (this.currentIndex > 0) {
                Button('← 上一题')
                  .fontSize(14)
                  .layoutWeight(1)
                  .height(44)
                  .borderRadius(AppConfig.radius)
                  .backgroundColor('#FFFFFF')
                  .fontColor(AppConfig.primaryColor)
                  .border({ width: 1, color: AppConfig.primaryColor })
                  .onClick(() => { this.goToPrevious(); })
              }

              if (this.currentIndex < SAMPLE_QUESTIONS.length - 1) {
                Button('下一题 →')
                  .fontSize(14)
                  .layoutWeight(1)
                  .height(44)
                  .borderRadius(AppConfig.radius)
                  .backgroundColor(AppConfig.primaryColor)
                  .fontColor('#FFFFFF')
                  .onClick(() => { this.goToNext(); })
              }

              if (this.currentIndex === SAMPLE_QUESTIONS.length - 1) {
                Button('🏁 查看成绩')
                  .fontSize(14)
                  .layoutWeight(1)
                  .height(44)
                  .borderRadius(AppConfig.radius)
                  .backgroundColor(AppConfig.accentColor)
                  .fontColor('#FFFFFF')
                  .onClick(() => { this.finishQuiz(); })
              }
            }
            .width('100%')
          }

          Blank().height(20)
        }
        .width('100%')
        .padding({ left: 16, right: 16, top: 16 })
      }
      .layoutWeight(1)
    }
    .width('100%')
    .height('100%')
  }

  // ==================== 选项按钮 ====================
  @Builder buildOptionButton(option: Option) {
    Column() {
      Row({ space: 10 }) {
        // 选项标识
        Column() {
          Text(option.id.toUpperCase())
            .fontSize(14)
            .fontWeight(700)
            .fontColor(this.getOptionColor(option.id))
        }
        .width(36)
        .height(36)
        .borderRadius(18)
        .backgroundColor(this.getOptionBg(option.id))
        .justifyContent(FlexAlign.Center)
        .alignItems(HorizontalAlign.Center)

        // 选项文本
        Text(option.text)
          .fontSize(15)
          .fontColor(this.showExplanation && this.selectedOptionId === option.id
            ? (option.id === this.currentQuestion.correctId ? AppConfig.correctColor : AppConfig.wrongColor)
            : AppConfig.textPrimary)
          .lineHeight(22)
          .layoutWeight(1)

        // 选中/正确答案标记
        if (this.showExplanation) {
          if (option.id === this.currentQuestion.correctId) {
            Text('✓')
              .fontSize(18)
              .fontColor(AppConfig.correctColor)
              .fontWeight(700)
          } else if (this.selectedOptionId === option.id && option.id !== this.currentQuestion.correctId) {
            Text('✗')
              .fontSize(18)
              .fontColor(AppConfig.wrongColor)
              .fontWeight(700)
          }
        } else if (this.selectedOptionId === option.id) {
          Text('✓')
            .fontSize(18)
            .fontColor(AppConfig.primaryColor)
            .fontWeight(700)
        }
      }
      .width('100%')
    }
    .width('100%')
    .padding(14)
    .backgroundColor(this.getOptionCardBg(option.id))
    .borderRadius(AppConfig.radiusSm)
    .border({
      width: this.selectedOptionId === option.id ? 2 : 1,
      color: this.getOptionBorder(option.id)
    })
    .onClick(() => {
      if (!this.showExplanation) {
        this.selectOption(option);
      }
    })
  }

  // ==================== 结果页（内嵌） ====================
  @Builder buildResultScreen() {
    Column() {
      // 头部
      Column() {
        Text('🎉')
          .fontSize(48)
          .margin({ bottom: 8 })
        Text('测验完成！')
          .fontSize(22)
          .fontWeight(700)
          .fontColor('#FFFFFF')
      }
      .width('100%')
      .padding({ top: 60, bottom: 30 })
      .backgroundColor(AppConfig.primaryColor)
      .alignItems(HorizontalAlign.Center)

      Scroll() {
        Column({ space: 14 }) {
          // 成绩卡片
          Column() {
            // 圆环分数
            Column() {
              Text(this.quizResult.accuracy.toFixed(0) + '%')
                .fontSize(48)
                .fontWeight(800)
                .fontColor(this.quizResult.accuracy >= 60 ? AppConfig.correctColor : AppConfig.wrongColor)
              Text(this.getScoreLabel())
                .fontSize(14)
                .fontColor(AppConfig.textSecondary)
                .margin({ top: 4 })
            }
            .width(140)
            .height(140)
            .borderRadius(70)
            .backgroundColor('#F5F9F5')
            .justifyContent(FlexAlign.Center)
            .margin({ bottom: 16 })

            // 统计行
            Row() {
              Column() {
                Text(this.quizResult.correctCount.toString())
                  .fontSize(24)
                  .fontWeight(700)
                  .fontColor(AppConfig.correctColor)
                Text('正确')
                  .fontSize(11)
                  .fontColor(AppConfig.textSecondary)
              }
              .layoutWeight(1)
              .alignItems(HorizontalAlign.Center)

              Column() {
                Text(this.quizResult.wrongCount.toString())
                  .fontSize(24)
                  .fontWeight(700)
                  .fontColor(AppConfig.wrongColor)
                Text('错误')
                  .fontSize(11)
                  .fontColor(AppConfig.textSecondary)
              }
              .layoutWeight(1)
              .alignItems(HorizontalAlign.Center)

              Column() {
                Text(this.quizResult.skippedCount.toString())
                  .fontSize(24)
                  .fontWeight(700)
                  .fontColor('#FF9800')
                Text('未答')
                  .fontSize(11)
                  .fontColor(AppConfig.textSecondary)
              }
              .layoutWeight(1)
              .alignItems(HorizontalAlign.Center)

              Column() {
                Text(this.formatTime(this.quizResult.timeUsed))
                  .fontSize(24)
                  .fontWeight(700)
                  .fontColor(AppConfig.primaryColor)
                Text('耗时')
                  .fontSize(11)
                  .fontColor(AppConfig.textSecondary)
              }
              .layoutWeight(1)
              .alignItems(HorizontalAlign.Center)
            }
            .width('100%')
            .margin({ top: 4 })
          }
          .width('100%')
          .padding(20)
          .backgroundColor(AppConfig.cardBg)
          .borderRadius(AppConfig.radius)
          .border({ width: 1, color: AppConfig.cardBorder })

          // 逐题回顾
          Column() {
            Text('📋 答题回顾')
              .fontSize(15)
              .fontWeight(600)
              .fontColor(AppConfig.textPrimary)
              .margin({ bottom: 10 })
              .alignSelf(ItemAlign.Start)

            ForEach(this.quizResult.records, (record: AnswerRecord, idx: number) => {
              Row() {
                // 序号 + 正确/错误
                Row({ space: 6 }) {
                  Text((idx + 1).toString())
                    .fontSize(12)
                    .fontWeight(700)
                    .fontColor('#FFFFFF')
                    .width(24)
                    .height(24)
                    .borderRadius(12)
                    .backgroundColor(record.isCorrect ? AppConfig.correctColor : AppConfig.wrongColor)
                    .textAlign(TextAlign.Center)

                  Text(record.isCorrect ? '✓' : '✗')
                    .fontSize(14)
                    .fontColor(record.isCorrect ? AppConfig.correctColor : AppConfig.wrongColor)
                }

                Blank()

                if (record.selectedId !== '__SKIP__') {
                  Text(record.selectedId.toUpperCase())
                    .fontSize(12)
                    .fontColor(AppConfig.textSecondary)
                } else {
                  Text('未答')
                    .fontSize(12)
                    .fontColor('#FF9800')
                }
              }
              .width('100%')
              .padding({ top: 10, bottom: 10 })
              .border({
                width: { bottom: idx < this.quizResult.records.length - 1 ? 0.5 : 0 },
                color: AppConfig.cardBorder
              })
            }, (record: AnswerRecord, idx: number) => idx.toString())
          }
          .width('100%')
          .padding(18)
          .backgroundColor(AppConfig.cardBg)
          .borderRadius(AppConfig.radius)
          .border({ width: 1, color: AppConfig.cardBorder })

          // 操作按钮
          Column({ space: 10 }) {
            Button('🔄 再来一次')
              .fontSize(16)
              .fontWeight(600)
              .width('100%')
              .height(50)
              .borderRadius(AppConfig.radius)
              .backgroundColor(AppConfig.primaryColor)
              .fontColor('#FFFFFF')
              .onClick(() => { this.restartQuiz(); })

            Button('🏠 返回首页')
              .fontSize(16)
              .width('100%')
              .height(50)
              .borderRadius(AppConfig.radius)
              .backgroundColor('#FFFFFF')
              .fontColor(AppConfig.primaryColor)
              .border({ width: 1.5, color: AppConfig.primaryColor })
              .onClick(() => { this.goHome(); })
          }
          .width('100%')

          Blank().height(20)
        }
        .width('100%')
        .padding({ left: 16, right: 16, top: 16 })
      }
      .layoutWeight(1)
    }
    .width('100%')
    .height('100%')
  }

  // ==================== 业务逻辑 ====================
  private startQuiz(): void {
    this.quizState = QuizState.ANSWERING;
    this.currentIndex = 0;
    this.selectedOptionId = '';
    this.answers = [];
    this.timeRemaining = AppConfig.defaultQuizTime;
    this.showExplanation = false;
    this.startTimer();
  }

  private selectOption(option: Option): void {
    this.selectedOptionId = option.id;
    const isCorrect = option.id === this.currentQuestion.correctId;
    this.answers.push(new AnswerRecord(this.currentQuestion.id, option.id, isCorrect));
    this.showExplanation = true;
  }

  private goToPrevious(): void {
    if (this.currentIndex > 0) {
      this.currentIndex--;
      // 恢复上一题的答案状态
      const prevAnswer = this.answers[this.currentIndex];
      if (prevAnswer) {
        this.selectedOptionId = prevAnswer.selectedId;
        this.showExplanation = true;
      } else {
        this.selectedOptionId = '';
        this.showExplanation = false;
      }
    }
  }

  private goToNext(): void {
    if (this.currentIndex < SAMPLE_QUESTIONS.length - 1) {
      this.currentIndex++;
      const nextAnswer = this.answers[this.currentIndex];
      if (nextAnswer) {
        this.selectedOptionId = nextAnswer.selectedId;
        this.showExplanation = true;
      } else {
        this.selectedOptionId = '';
        this.showExplanation = false;
      }
    }
  }

  private startTimer(): void {
    this.timerId = setInterval(() => {
      if (this.quizState !== QuizState.ANSWERING) {
        return;
      }
      if (this.timeRemaining <= 0) {
        this.finishQuiz();
        return;
      }
      this.timeRemaining--;
    }, 1000);
  }

  private finishQuiz(): void {
    // 停止计时
    clearInterval(this.timerId);

    // 补充未答题目
    const total = SAMPLE_QUESTIONS.length;
    while (this.answers.length < total) {
      this.answers.push(new AnswerRecord(
        SAMPLE_QUESTIONS[this.answers.length].id,
        '__SKIP__',
        false
      ));
    }

    // 统计结果
    let correct = 0;
    let wrong = 0;
    let skipped = 0;
    for (const record of this.answers) {
      if (record.selectedId === '__SKIP__') {
        skipped++;
      } else if (record.isCorrect) {
        correct++;
      } else {
        wrong++;
      }
    }

    const timeUsed = AppConfig.defaultQuizTime - this.timeRemaining;
    const accuracy = total > 0 ? (correct / total) * 100 : 0;

    this.quizResult = new QuizResult(
      total, correct, wrong, skipped, timeUsed, accuracy, this.answers
    );

    this.quizState = QuizState.RESULT;
  }

  private restartQuiz(): void {
    this.startQuiz();
  }

  private goHome(): void {
    this.quizState = QuizState.HOME;
    clearInterval(this.timerId);
  }

  // ==================== 辅助方法 ====================
  private formatTime(seconds: number): string {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return m.toString().padStart(2, '0') + ':' + s.toString().padStart(2, '0');
  }

  private getScoreLabel(): string {
    if (this.quizResult.accuracy >= 90) return '🎖 优秀';
    if (this.quizResult.accuracy >= 70) return '👍 良好';
    if (this.quizResult.accuracy >= 60) return '✅ 通过';
    return '📚 加油';
  }

  private getOptionColor(optId: string): string {
    if (this.showExplanation && optId === this.currentQuestion.correctId) {
      return AppConfig.correctColor;
    }
    if (this.showExplanation && this.selectedOptionId === optId
      && optId !== this.currentQuestion.correctId) {
      return AppConfig.wrongColor;
    }
    return AppConfig.primaryColor;
  }

  private getOptionBg(optId: string): string {
    if (this.showExplanation && optId === this.currentQuestion.correctId) {
      return '#E8F5E9';
    }
    if (this.showExplanation && this.selectedOptionId === optId
      && optId !== this.currentQuestion.correctId) {
      return '#FFEBEE';
    }
    return '#E8F0E8';
  }

  private getOptionCardBg(optId: string): string {
    if (this.showExplanation && optId === this.currentQuestion.correctId) {
      return '#F0FFF0';
    }
    if (this.showExplanation && this.selectedOptionId === optId
      && optId !== this.currentQuestion.correctId) {
      return '#FFF0F0';
    }
    return AppConfig.cardBg;
  }

  private getOptionBorder(optId: string): string {
    if (this.showExplanation && optId === this.currentQuestion.correctId) {
      return AppConfig.correctColor;
    }
    if (this.showExplanation && this.selectedOptionId === optId
      && optId !== this.currentQuestion.correctId) {
      return AppConfig.wrongColor;
    }
    if (this.selectedOptionId === optId) {
      return AppConfig.primaryColor;
    }
    return AppConfig.cardBorder;
  }
}
