/**
 * HNavBar — 顶部导航栏组件
 *
 * ============================================================================
 * Props 类型定义
 * ============================================================================
 * interface HNavBarProps {
 *   title: string;                   // 标题文字（必填）
 *   showBack?: boolean;              // 是否显示返回按钮，默认 true
 *   backLabel?: string;              // 返回按钮文字，默认 ''（仅显示图标）
 *   rightActions?: NavBarAction[];   // 右侧操作按钮组
 *   backgroundColor?: string;        // 导航栏背景色，默认从 theme.surface 读取
 *   onBack?: () => void;             // 返回回调（通常调用 NavPathStack.pop()）
 * }
 *
 * interface NavBarAction {
 *   icon?: Resource;                 // 图标资源
 *   label?: string;                  // 文字标签
 *   onTap: () => void;               // 点击回调
 * }
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * HNavBar({
 *   title: '笔记详情',
 *   onBack: () => { this.navPathStack.pop() },
 *   rightActions: [
 *     { icon: $r('app.media.ic_edit'), onTap: () => { this.edit() } },
 *     { icon: $r('app.media.ic_delete'), onTap: () => { this.confirmDelete() } }
 *   ]
 * })
 */

import { ThemeTokens } from '../theme/tokens';

// ---- 类型定义 ----

export interface NavBarAction {
  icon?: Resource;
  label?: string;
  onTap: () => void;
}

// ---- 组件 ----

@Component
export struct HNavBar {
  @Prop title: string = '';
  @Prop showBack: boolean = true;
  @Prop backLabel: string = '';
  rightActions?: NavBarAction[];
  backgroundColor?: string;
  onBack?: () => void;

  @StorageProp('theme') theme: ThemeTokens | null = null;

  private handleBack(): void {
    if (this.onBack) {
      this.onBack();
    }
  }

  build() {
    Row() {
      // ---- 左侧：返回按钮 ----
      if (this.showBack) {
        Row({ space: 4 }) {
          Text('←')
            .fontSize(20)
            .fontColor(this.theme?.primary ?? '#5B8C5A')
          if (this.backLabel) {
            Text(this.backLabel)
              .fontSize(this.theme?.fontSizeBody ?? 14)
              .fontColor(this.theme?.primary ?? '#5B8C5A')
              .fontWeight(this.theme?.fontWeightMedium ?? 500)
          }
        }
        .padding({ left: 4, right: 12, top: 8, bottom: 8 })
        .onClick(() => {
          this.handleBack();
        })
      }

      // ---- 中间：标题 ----
      Text(this.title)
        .fontSize(this.theme?.fontSizeTitle ?? 18)
        .fontWeight(this.theme?.fontWeightBold ?? 700)
        .fontColor(this.theme?.onSurface ?? '#1C1C1E')
        .layoutWeight(1)
        .textAlign(this.showBack ? TextAlign.Center : TextAlign.Start)
        .maxLines(1)
        .textOverflow({ overflow: TextOverflow.Ellipsis })

      // ---- 右侧：操作按钮组 ----
      if (this.rightActions && this.rightActions.length > 0) {
        Row({ space: this.theme?.spacingSmall ?? 8 }) {
          ForEach(
            this.rightActions,
            (action: NavBarAction, index: number) => {
              Row({ space: 4 }) {
                if (action.icon !== undefined) {
                  Image(action.icon)
                    .width(24)
                    .height(24)
                }
                if (action.label) {
                  Text(action.label)
                    .fontSize(this.theme?.fontSizeBody ?? 14)
                    .fontColor(this.theme?.primary ?? '#5B8C5A')
                }
              }
              .padding({ left: 8, right: 8, top: 8, bottom: 8 })
              .onClick(() => {
                action.onTap();
              })
            },
            (action: NavBarAction, index: number) => `${index}`
          )
        }
        .padding({ right: 4 })
      }
    }
    .width('100%')
    .height(56)
    .padding({ left: this.theme?.spacingMedium ?? 12, right: this.theme?.spacingMedium ?? 12 })
    .backgroundColor(this.backgroundColor ?? this.theme?.surface ?? '#FFFFFF')
    .border({
      width: { bottom: 0.5 },
      color: this.theme?.outline ?? '#DCDCDC'
    })
  }
}
