/**
 * HCard — 卡片容器组件
 *
 * 从 common/theme/tokens 统一引用 ThemeTokens，禁止组件内重复定义。
 *
 * ============================================================================
 * Props 类型定义
 * ============================================================================
 * interface HCardProps {
 *   title: string;              // 卡片标题（必填）
 *   subtitle?: string;          // 副标题（可选）
 *   icon?: Resource;            // 左侧图标资源（可选）
 *   trailing?: string;          // 右侧辅助文字（可选），如时间 / 标签
 *   enabled?: boolean;          // 是否可点击，默认 true
 *   swipeEnabled?: boolean;     // 是否支持右滑操作，默认 false
 *   swipeActionLabel?: string;  // 右滑操作文案，如 "删除" / "完成"
 *   swipeActionColor?: string;  // 右滑操作区颜色，默认红色
 *   onTap?: () => void;         // 点击卡片回调
 *   onSwipeAction?: () => void; // 右滑操作回调
 * }
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * HCard({ title: '鸿蒙元服务学习', subtitle: '12月15日', onTap: () => { ... } })
 * HCard({ title: '复习卡片', icon: $r('app.media.ic_flashcard'), trailing: '12条' })
 * HCard({ title: '临时笔记', swipeEnabled: true, swipeActionLabel: '删除', onSwipeAction: () => { ... } })
 *
 * ============================================================================
 * 注意事项
 * ============================================================================
 * 1. 右滑通过 PanGesture 实现，位移阈值 80vp 触发 onSwipeAction
 * 2. 右滑后自动回弹或触发回调后复位
 * 3. 卡片整体圆角/间距从 theme 读取，禁止硬编码
 */

import { ThemeTokens } from '../theme/tokens';

// ---- 类型定义 ----

export interface HCardSwipeConfig {
  enabled: boolean;
  actionLabel: string;
  actionColor: string;
}

enum SwipeState {
  IDLE,
  SWIPING,
  REVEALED
}

// ---- 组件 ----

@Component
export struct HCard {
  @Prop title: string = '';
  @Prop subtitle: string = '';
  @Prop trailing: string = '';
  @Prop enabled: boolean = true;
  @Prop swipeEnabled: boolean = false;
  @Prop swipeActionLabel: string = '删除';
  @Prop swipeActionColor: string = '#FF3B30';
  icon?: Resource;
  onTap?: () => void;
  onSwipeAction?: () => void;

  @StorageProp('theme') theme: ThemeTokens | null = null;

  /** 右滑相关内部状态 */
  @State private swipeOffsetX: number = 0;
  @State private swipeState: SwipeState = SwipeState.IDLE;

  /** 右滑动作区宽度 */
  private readonly swipeActionWidth: number = 80;
  /** 触发阈值 */
  private readonly swipeThreshold: number = 50;

  private handleTap(): void {
    if (!this.enabled) {
      return;
    }
    if (this.onTap) {
      this.onTap();
    }
  }

  private handleSwipeAction(): void {
    if (this.onSwipeAction) {
      this.onSwipeAction();
    }
    this.swipeOffsetX = 0;
    this.swipeState = SwipeState.IDLE;
  }

  build() {
    Stack({ alignContent: Alignment.End }) {
      // ---- 右滑背后的操作区 ----
      if (this.swipeEnabled) {
        Row() {
          Text(this.swipeActionLabel)
            .fontSize(this.theme?.fontSizeBody ?? 14)
            .fontColor('#FFFFFF')
            .fontWeight(this.theme?.fontWeightMedium ?? 500)
        }
        .width(this.swipeActionWidth)
        .height('100%')
        .justifyContent(FlexAlign.Center)
        .backgroundColor(this.swipeActionColor)
        .borderRadius({
          topRight: this.theme?.radiusMedium ?? 12,
          bottomRight: this.theme?.radiusMedium ?? 12
        })
        .onClick(() => {
          this.handleSwipeAction();
        })
      }

      // ---- 卡片主体 ----
      Row() {
        // 左侧图标（可选）
        if (this.icon !== undefined) {
          Image(this.icon)
            .width(40)
            .height(40)
            .borderRadius(8)
            .margin({ right: this.theme?.spacingMedium ?? 12 })
        }

        // 中间标题区
        Column({ space: 4 }) {
          Text(this.title)
            .fontSize(this.theme?.fontSizeTitle ?? 18)
            .fontWeight(this.theme?.fontWeightBold ?? 700)
            .fontColor(this.theme?.onSurface ?? '#1C1C1E')
            .maxLines(1)
            .textOverflow({ overflow: TextOverflow.Ellipsis })

          if (this.subtitle) {
            Text(this.subtitle)
              .fontSize(this.theme?.fontSizeCaption ?? 12)
              .fontColor('#888888')
              .maxLines(1)
              .textOverflow({ overflow: TextOverflow.Ellipsis })
          }
        }
        .layoutWeight(1)
        .alignItems(HorizontalAlign.Start)

        // 右侧辅助文字
        if (this.trailing) {
          Text(this.trailing)
            .fontSize(this.theme?.fontSizeCaption ?? 12)
            .fontColor('#888888')
            .margin({ left: this.theme?.spacingSmall ?? 8 })
        }
      }
      .width('100%')
      .padding(this.theme?.spacingLarge ?? 16)
      .backgroundColor(this.theme?.surface ?? '#FFFFFF')
      .borderRadius(this.theme?.radiusMedium ?? 12)
      .offset({ x: this.swipeOffsetX, y: 0 })
      .onClick(() => {
        this.handleTap();
      })
      .gesture(
        this.swipeEnabled
          ? PanGesture({ fingers: 1, direction: PanDirection.Horizontal, distance: 5 })
              .onActionStart(() => {
                this.swipeState = SwipeState.SWIPING;
              })
              .onActionUpdate((event: GestureEvent) => {
                this.swipeOffsetX = Math.min(0, Math.max(-this.swipeActionWidth, event.offsetX));
              })
              .onActionEnd((event: GestureEvent) => {
                if (Math.abs(this.swipeOffsetX) >= this.swipeThreshold) {
                  this.swipeOffsetX = -this.swipeActionWidth;
                  this.swipeState = SwipeState.REVEALED;
                } else {
                  this.swipeOffsetX = 0;
                  this.swipeState = SwipeState.IDLE;
                }
              })
          : undefined
      )
    }
    .width('100%')
    .margin({ bottom: this.theme?.spacingSmall ?? 8 })
  }
}
