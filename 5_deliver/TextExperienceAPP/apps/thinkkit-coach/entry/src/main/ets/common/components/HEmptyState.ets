/**
 * HEmptyState — 空状态占位组件
 *
 * 从 common/theme/tokens 统一引用 ThemeTokens。
 * 修复：SymbolGlyph 兼容性问题 → 使用 Text + 系统 emoji 兜底。
 *
 * ============================================================================
 * Props 类型定义
 * ============================================================================
 * interface HEmptyStateProps {
 *   message: string;           // 空状态提示文案（必填）
 *   actionLabel?: string;      // 操作按钮文案（可选，不传则不显示按钮）
 *   description?: string;      // 补充说明文案（可选）
 *   icon?: Resource;           // 自定义插图图标（可选），默认使用占位图
 *   onAction?: () => void;     // 操作按钮点击回调
 * }
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * HEmptyState({ message: '还没有笔记' })
 * HEmptyState({ message: '还没有习惯', description: '点击下方按钮创建', actionLabel: '添加习惯', onAction: () => { ... } })
 * HEmptyState({ message: '暂无闪卡', icon: $r('app.media.ic_empty_flashcard'), actionLabel: '创建闪卡' })
 */

import { ThemeTokens } from '../theme/tokens';

// ---- 组件 ----

@Component
export struct HEmptyState {
  @Prop message: string = '';
  @Prop actionLabel: string = '';
  @Prop description: string = '';
  icon?: Resource;
  onAction?: () => void;

  @StorageProp('theme') theme: ThemeTokens | null = null;

  build() {
    Column({ space: this.theme?.spacingMedium ?? 12 }) {
      // 插图占位区
      Column() {
        if (this.icon !== undefined) {
          Image(this.icon)
            .width(80)
            .height(80)
            .objectFit(ImageFit.Contain)
        } else {
          // 默认占位：虚线框 + 文件夹图标（使用 Text emoji 兜底，兼容所有鸿蒙版本）
          Column() {
            Text('📁')
              .fontSize(36)
          }
          .width(80)
          .height(80)
          .border({ width: 2, color: '#E0E0E0', style: BorderStyle.Dashed })
          .borderRadius(16)
          .justifyContent(FlexAlign.Center)
        }
      }
      .height(120)
      .justifyContent(FlexAlign.Center)

      // 主文案
      Text(this.message)
        .fontSize(this.theme?.fontSizeTitle ?? 18)
        .fontWeight(this.theme?.fontWeightBold ?? 700)
        .fontColor(this.theme?.onSurface ?? '#1C1C1E')
        .textAlign(TextAlign.Center)

      // 补充说明
      if (this.description) {
        Text(this.description)
          .fontSize(this.theme?.fontSizeCaption ?? 12)
          .fontColor('#888888')
          .textAlign(TextAlign.Center)
          .maxLines(3)
      }

      // 操作按钮（直接使用 HButton 类型的内联 Button，保持自包含）
      if (this.actionLabel && this.onAction) {
        Button(this.actionLabel)
          .fontSize(this.theme?.fontSizeBody ?? 14)
          .fontColor('#FFFFFF')
          .backgroundColor(this.theme?.primary ?? '#5B8C5A')
          .height(44)
          .borderRadius(this.theme?.radiusMedium ?? 12)
          .padding({ left: 24, right: 24 })
          .onClick(() => {
            if (this.onAction) {
              this.onAction();
            }
          })
          .margin({ top: 4 })
      }
    }
    .width('100%')
    .padding({ left: 32, right: 32, top: 40, bottom: 40 })
    .justifyContent(FlexAlign.Center)
  }
}
