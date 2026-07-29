/**
 * HProgressBar — 进度条 / 习惯链组件
 *
 * 从 common/theme/tokens 统一引用 ThemeTokens。
 * 修复：ForEach 在 @Builder 中的 key generator 改用稳定标识，避免 ArkTS 严格模式告警。
 *
 * ============================================================================
 * Props 类型定义
 * ============================================================================
 * interface HProgressBarProps {
 *   current: number;              // 当前值（必填）
 *   total: number;                // 最大值（必填），默认 1
 *   type?: ProgressBarType;       // 进度条类型：'linear' | 'segments'，默认 'linear'
 *   segments?: number;            // 分段数量（type='segments' 时必填）
 *   completedSegments?: number;   // 已完成分段数（type='segments' 时使用）
 *   showLabel?: boolean;          // 是否显示百分比/分数文字，默认 true
 *   showAnimation?: boolean;      // 是否显示进度动画，默认 true
 *   color?: string;               // 进度条颜色
 *   trackColor?: string;          // 轨道颜色
 *   height?: number;              // 进度条高度(vp)
 *   labelFormat?: 'percent' | 'fraction'; // 文字格式，默认 'fraction'
 * }
 */

import { ThemeTokens } from '../theme/tokens';

// ---- 类型定义 ----

export type ProgressBarType = 'linear' | 'segments';
export type LabelFormat = 'percent' | 'fraction';

// ---- 分段数据源（ArkTS LazyForEach / ForEach 兼容） ----

class SegmentItem {
  index: number;
  constructor(index: number) { this.index = index; }
}

// ---- 组件 ----

@Component
export struct HProgressBar {
  @Prop current: number = 0;
  @Prop total: number = 1;
  @Prop type: ProgressBarType = 'linear';
  @Prop segments: number = 7;
  @Prop completedSegments: number = 0;
  @Prop showLabel: boolean = true;
  @Prop showAnimation: boolean = true;
  @Prop color: string = '';
  @Prop trackColor: string = '';
  @Prop height: number = 0;
  @Prop labelFormat: LabelFormat = 'fraction';

  @StorageProp('theme') theme: ThemeTokens | null = null;

  /** 动画进度值 */
  @State private animatedProgress: number = 0;

  aboutToAppear(): void {
    if (this.showAnimation) {
      setTimeout(() => {
        animateTo({ duration: 600, curve: Curve.EaseOut }, () => {
          this.animatedProgress = this.getProgressRatio();
        });
      }, 100);
    } else {
      this.animatedProgress = this.getProgressRatio();
    }
  }

  /** 计算进度比例 (0.0 ~ 1.0) */
  private getProgressRatio(): number {
    if (this.total <= 0) {
      return 0;
    }
    return Math.min(1, Math.max(0, this.current / this.total));
  }

  /** 获取实际进度条颜色 */
  private getProgressColor(): string {
    return this.color || this.theme?.primary || '#5B8C5A';
  }

  /** 获取轨道颜色 */
  private getTrackColor(): string {
    return this.trackColor || this.theme?.surfaceVariant || '#E8E8E8';
  }

  /** 获取进度条高度 */
  private getHeight(): number {
    if (this.height > 0) {
      return this.height;
    }
    return this.type === 'segments' ? 12 : 8;
  }

  /** 生成标签文字 */
  private getLabelText(): string {
    if (this.type === 'segments') {
      return `${this.completedSegments}/${this.segments}`;
    }
    if (this.labelFormat === 'percent') {
      return `${Math.round(this.getProgressRatio() * 100)}%`;
    }
    return `${this.current}/${this.total}`;
  }

  /** 构建分段进度（习惯打卡链） */
  @Builder
  buildSegments() {
    Row({ space: 2 }) {
      ForEach(
        Array.from({ length: this.segments }, (_: unknown, i: number) => new SegmentItem(i)),
        (item: SegmentItem, index: number) => {
          Row()
            .width(`${100 / this.segments - 1}%`)
            .height(this.getHeight())
            .borderRadius(this.theme?.radiusSmall ?? 4)
            .backgroundColor(
              index < this.completedSegments ? this.getProgressColor() : this.getTrackColor()
            )
        },
        (item: SegmentItem) => item.index.toString()
      )
    }
    .width('100%')
    .borderRadius(this.theme?.radiusSmall ?? 4)
  }

  /** 构建线性进度条 */
  @Builder
  buildLinear() {
    Stack({ alignContent: Alignment.Start }) {
      Row()
        .width('100%')
        .height(this.getHeight())
        .backgroundColor(this.getTrackColor())
        .borderRadius(this.getHeight() / 2)

      Row()
        .width(`${this.animatedProgress * 100}%`)
        .height(this.getHeight())
        .backgroundColor(this.getProgressColor())
        .borderRadius(this.getHeight() / 2)
    }
    .width('100%')
  }

  build() {
    Column({ space: this.theme?.spacingSmall ?? 4 }) {
      if (this.type === 'segments') {
        this.buildSegments();
      } else {
        this.buildLinear();
      }

      if (this.showLabel) {
        Text(this.getLabelText())
          .fontSize(this.theme?.fontSizeCaption ?? 12)
          .fontColor('#888888')
          .fontWeight(this.theme?.fontWeightMedium ?? 500)
      }
    }
    .width('100%')
    .alignItems(HorizontalAlign.End)
  }
}
