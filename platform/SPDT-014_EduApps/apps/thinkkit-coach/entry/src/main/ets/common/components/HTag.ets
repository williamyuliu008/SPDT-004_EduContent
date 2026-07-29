/**
 * HTag — 标签组件（单标签）
 *
 * ============================================================================
 * Props 类型定义
 * ============================================================================
 * interface HTagProps {
 *   label: string;                // 标签文字（必填）
 *   selected?: boolean;           // 是否选中态，默认 false
 *   color?: string;               // 自定义颜色（优先级高于 theme.primary）
 *   size?: 'small' | 'medium';    // 标签尺寸，默认 'medium'
 *   removable?: boolean;          // 是否显示删除按钮，默认 false
 *   onTap?: () => void;           // 点击回调
 *   onRemove?: () => void;        // 删除回调（removable=true 时有效）
 * }
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * HTag({ label: '技术', selected: true, onTap: () => { ... } })
 * HTag({ label: '鸿蒙', removable: true, onRemove: () => { this.removeTag('鸿蒙') } })
 */

import { ThemeTokens } from '../theme/tokens';

// ---- 类型定义 ----

export type HTagSize = 'small' | 'medium';

// ---- 组件 ----

@Component
export struct HTag {
  @Prop label: string = '';
  @Prop selected: boolean = false;
  @Prop color: string = '';
  @Prop size: HTagSize = 'medium';
  @Prop removable: boolean = false;
  onTap?: () => void;
  onRemove?: () => void;

  @StorageProp('theme') theme: ThemeTokens | null = null;

  private getActiveColor(): string {
    return this.color || this.theme?.primary || '#5B8C5A';
  }

  private getFontSize(): number {
    return this.size === 'small' ? 11 : 13;
  }

  private getHeight(): number {
    return this.size === 'small' ? 24 : 32;
  }

  private getPaddingH(): number {
    return this.size === 'small' ? 8 : 12;
  }

  private handleTap(): void {
    if (this.onTap) {
      this.onTap();
    }
  }

  private handleRemove(): void {
    if (this.onRemove) {
      this.onRemove();
    }
  }

  build() {
    Row({ space: 4 }) {
      Text(this.label)
        .fontSize(this.getFontSize())
        .fontColor(this.selected ? '#FFFFFF' : this.getActiveColor())
        .fontWeight(this.theme?.fontWeightMedium ?? 500)
        .maxLines(1)

      if (this.removable) {
        Text('×')
          .fontSize(this.getFontSize() + 2)
          .fontColor(this.selected ? '#FFFFFF' : this.getActiveColor())
          .onClick(() => {
            this.handleRemove();
          })
      }
    }
    .height(this.getHeight())
    .padding({ left: this.getPaddingH(), right: this.getPaddingH() })
    .backgroundColor(this.selected ? this.getActiveColor() : 'transparent')
    .border({
      width: 1,
      color: this.getActiveColor(),
      style: BorderStyle.Solid
    })
    .borderRadius(this.getHeight() / 2)
    .onClick(() => {
      this.handleTap();
    })
  }
}
