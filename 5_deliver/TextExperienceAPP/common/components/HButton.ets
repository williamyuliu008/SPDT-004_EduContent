/**
 * HButton — 标准化按钮组件
 *
 * 从 common/theme/tokens 统一引用 ThemeTokens，禁止组件内重复定义。
 *
 * ============================================================================
 * Props 类型定义
 * ============================================================================
 * interface HButtonProps {
 *   label: string;           // 按钮文字
 *   type: ButtonType;        // 按钮样式：'primary' | 'secondary' | 'ghost'
 *   size?: ButtonSize;       // 按钮尺寸：'small' | 'medium' | 'large'，默认 'medium'
 *   disabled?: boolean;      // 是否禁用，默认 false
 *   loading?: boolean;       // 是否加载中，默认 false（loading 时自动禁用点击）
 *   fullWidth?: boolean;     // 是否撑满父容器宽度，默认 false
 *   onTap?: () => void;      // 点击回调
 * }
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * HButton({ label: '保存', type: 'primary', onTap: () => { this.saveNote() } })
 * HButton({ label: '提交', type: 'secondary', loading: this.isSubmitting })
 * HButton({ label: '已删除', type: 'ghost', disabled: true })
 *
 * ============================================================================
 * 注意事项
 * ============================================================================
 * 1. loading 为 true 时内部自动阻止点击，无需在 onTap 中额外判断
 * 2. 颜色、圆角、字号统一从 @StorageProp('theme') 读取
 * 3. 按钮最小点击热区 40vp，符合鸿蒙适老化要求
 */

import { ThemeTokens } from '../theme/tokens';

// ---- 类型定义 ----

export type ButtonType = 'primary' | 'secondary' | 'ghost';
export type ButtonSize = 'small' | 'medium' | 'large';

export interface HButtonProps {
  label: string;
  type: ButtonType;
  size?: ButtonSize;
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  onTap?: () => void;
}

// ---- 组件 ----

@Component
export struct HButton {
  @Prop label: string = '';
  @Prop type: ButtonType = 'primary';
  @Prop size: ButtonSize = 'medium';
  @Prop disabled: boolean = false;
  @Prop loading: boolean = false;
  @Prop fullWidth: boolean = false;
  onTap?: () => void;

  @StorageProp('theme') theme: ThemeTokens | null = null;

  /** 根据 type 返回背景色 */
  private getBackgroundColor(): string {
    if (this.disabled) {
      return this.theme?.outline ?? '#DCDCDC';
    }
    switch (this.type) {
      case 'primary':
        return this.theme?.primary ?? '#5B8C5A';
      case 'secondary':
        return this.theme?.surfaceVariant ?? '#F0F0F0';
      case 'ghost':
        return 'transparent';
      default:
        return this.theme?.primary ?? '#5B8C5A';
    }
  }

  /** 根据 type 返回文字颜色 */
  private getFontColor(): string {
    if (this.disabled) {
      return '#A0A0A0';
    }
    switch (this.type) {
      case 'primary':
        return this.theme?.onPrimary ?? '#FFFFFF';
      case 'secondary':
        return this.theme?.onSurface ?? '#1C1C1E';
      case 'ghost':
        return this.theme?.primary ?? '#5B8C5A';
      default:
        return this.theme?.onPrimary ?? '#FFFFFF';
    }
  }

  /** 根据 size 返回高度 */
  private getHeight(): number {
    switch (this.size) {
      case 'small': return 36;
      case 'medium': return 44;
      case 'large': return 52;
      default: return 44;
    }
  }

  /** 根据 size 返回字号 */
  private getFontSize(): number {
    switch (this.size) {
      case 'small': return 13;
      case 'medium': return 15;
      case 'large': return 17;
      default: return 15;
    }
  }

  /** 实际点击处理：loading/disabled 时不响应 */
  private handleTap(): void {
    if (this.loading || this.disabled) {
      return;
    }
    if (this.onTap) {
      this.onTap();
    }
  }

  build() {
    Button() {
      if (this.loading) {
        Row({ space: 6 }) {
          LoadingProgress()
            .width(16)
            .height(16)
            .color(this.getFontColor())
          Text(this.label)
            .fontSize(this.getFontSize())
            .fontColor(this.getFontColor())
            .fontWeight(this.theme?.fontWeightMedium ?? 500)
        }
        .justifyContent(FlexAlign.Center)
      } else {
        Text(this.label)
          .fontSize(this.getFontSize())
          .fontColor(this.getFontColor())
          .fontWeight(this.theme?.fontWeightMedium ?? 500)
      }
    }
    .width(this.fullWidth ? '100%' : undefined)
    .height(this.getHeight())
    .backgroundColor(this.getBackgroundColor())
    .borderRadius(this.theme?.radiusMedium ?? 12)
    .border(
      this.type === 'ghost' && !this.disabled
        ? { width: 1, color: this.theme?.primary ?? '#5B8C5A' }
        : { width: 0, color: 'transparent' }
    )
    .enabled(!this.disabled)
    .opacity(this.disabled ? 0.5 : 1.0)
    .onClick(() => {
      this.handleTap();
    })
  }
}
