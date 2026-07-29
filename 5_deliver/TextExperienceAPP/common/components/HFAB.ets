/**
 * HFAB — 浮动操作按钮 (Floating Action Button)
 *
 * ============================================================================
 * Props 类型定义
 * ============================================================================
 * interface HFABProps {
 *   icon?: Resource;               // 图标资源，默认使用 '+' 文字
 *   label?: string;                // 扩展标签文字（可选，有 label 时按钮拉长）
 *   position?: FABPosition;        // 屏幕位置：'bottomRight' | 'bottomCenter'，默认 'bottomRight'
 *   color?: string;                // 按钮颜色，默认 theme.primary
 *   onTap: () => void;             // 点击回调（必填）
 * }
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * HFAB({ onTap: () => { this.navPathStack.pushPathByName('FormPage', undefined) } })
 * HFAB({ label: '新建笔记', onTap: () => { this.createNote() } })
 * HFAB({ icon: $r('app.media.ic_add'), position: 'bottomCenter', onTap: () => { ... } })
 */

import { ThemeTokens } from '../theme/tokens';

// ---- 类型定义 ----

export type FABPosition = 'bottomRight' | 'bottomCenter';

// ---- 组件 ----

@Component
export struct HFAB {
  @Prop label: string = '';
  @Prop position: FABPosition = 'bottomRight';
  @Prop color: string = '';
  icon?: Resource;
  onTap?: () => void;

  @StorageProp('theme') theme: ThemeTokens | null = null;

  private getActiveColor(): string {
    return this.color || this.theme?.primary || '#5B8C5A';
  }

  private handleTap(): void {
    if (this.onTap) {
      this.onTap();
    }
  }

  build() {
    Stack({ alignContent: this.position === 'bottomCenter' ? Alignment.Bottom : Alignment.BottomEnd }) {
      Button() {
        Row({ space: 6 }) {
          if (this.icon !== undefined) {
            Image(this.icon)
              .width(24)
              .height(24)
              .fillColor('#FFFFFF')
          } else {
            Text('+')
              .fontSize(28)
              .fontColor('#FFFFFF')
              .fontWeight(this.theme?.fontWeightRegular ?? 400)
          }

          if (this.label) {
            Text(this.label)
              .fontSize(this.theme?.fontSizeBody ?? 14)
              .fontColor('#FFFFFF')
              .fontWeight(this.theme?.fontWeightMedium ?? 500)
              .padding({ right: 4 })
          }
        }
        .justifyContent(FlexAlign.Center)
      }
      .height(56)
      .borderRadius(28)
      .padding({ left: this.label ? 20 : 0, right: this.label ? 20 : 0 })
      .backgroundColor(this.getActiveColor())
      .shadow({
        radius: 8,
        color: `${this.getActiveColor()}40`,
        offsetX: 0,
        offsetY: 4
      })
      .onClick(() => {
        this.handleTap();
      })
    }
    .width('100%')
    .height('100%')
    .hitTestBehavior(HitTestMode.Transparent)
    .padding({ right: 16, bottom: 24 })
  }
}
