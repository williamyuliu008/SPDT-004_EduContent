/**
 * HCard — 卡片容器 (API 26 strict mode)
 */
import { ThemeTokens } from '../theme/tokens';

enum SwipeState { IDLE, SWIPING, REVEALED }

@Component
export struct HCard {
  @Prop title: string = '';
  @Prop subtitle: string = '';
  @Prop trailing: string = '';
  @Prop isEnabled: boolean = true;
  @Prop swipeEnabled: boolean = false;
  @Prop swipeActionLabel: string = '删除';
  @Prop swipeActionColor: string = '#FF3B30';
  icon?: Resource;
  onTap?: () => void;
  onSwipeAction?: () => void;
  @StorageProp('theme') theme: ThemeTokens | null = null;
  @State private swipeOffsetX: number = 0;
  @State private swipeState: SwipeState = SwipeState.IDLE;
  private readonly swipeActionWidth: number = 80;
  private readonly swipeThreshold: number = 50;

  build() {
    Stack({ alignContent: Alignment.End }) {
      if (this.swipeEnabled) {
        Row() {
          Text(this.swipeActionLabel).fontSize(this.theme?.fontSizeBody ?? 14).fontColor('#FFFFFF').fontWeight(this.theme?.fontWeightMedium ?? 500)
        }.width(this.swipeActionWidth).height('100%').justifyContent(FlexAlign.Center).backgroundColor(this.swipeActionColor)
        .borderRadius({ topRight: this.theme?.radiusMedium ?? 12, bottomRight: this.theme?.radiusMedium ?? 12 })
        .onClick(() => { if (this.onSwipeAction) this.onSwipeAction(); this.swipeOffsetX = 0; })
      }
      Row() {
        if (this.icon !== undefined) { Image(this.icon).width(40).height(40).borderRadius(8).margin({ right: this.theme?.spacingMedium ?? 12 }) }
        Column({ space: 4 }) {
          Text(this.title).fontSize(this.theme?.fontSizeTitle ?? 18).fontWeight(this.theme?.fontWeightBold ?? 700).fontColor(this.theme?.onSurface ?? '#1C1C1E').maxLines(1).textOverflow({ overflow: TextOverflow.Ellipsis })
          if (this.subtitle) { Text(this.subtitle).fontSize(this.theme?.fontSizeCaption ?? 12).fontColor('#888888').maxLines(1).textOverflow({ overflow: TextOverflow.Ellipsis }) }
        }.layoutWeight(1).alignItems(HorizontalAlign.Start)
        if (this.trailing) { Text(this.trailing).fontSize(this.theme?.fontSizeCaption ?? 12).fontColor('#888888').margin({ left: this.theme?.spacingSmall ?? 8 }) }
      }
      .width('100%').padding(this.theme?.spacingLarge ?? 16).backgroundColor(this.theme?.surface ?? '#FFFFFF').borderRadius(this.theme?.radiusMedium ?? 12)
      .offset({ x: this.swipeOffsetX, y: 0 })
      .onClick(() => { if (this.isEnabled && this.onTap) this.onTap(); })
      .gesture(this.swipeEnabled ? PanGesture({ fingers: 1, direction: PanDirection.Horizontal, distance: 5 })
        .onActionUpdate((event: GestureEvent) => { this.swipeOffsetX = Math.min(0, Math.max(-this.swipeActionWidth, event.offsetX)); })
        .onActionEnd((event: GestureEvent) => { this.swipeOffsetX = Math.abs(this.swipeOffsetX) >= this.swipeThreshold ? -this.swipeActionWidth : 0; })
        : undefined)
    }.width('100%').margin({ bottom: this.theme?.spacingSmall ?? 8 })
  }
}
