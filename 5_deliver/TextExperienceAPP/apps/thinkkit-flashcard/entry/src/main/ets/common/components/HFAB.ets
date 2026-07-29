/**
 * HFAB — 浮动按钮 (API 26 strict mode - no position prop conflict)
 */
import { ThemeTokens } from '../theme/tokens';

export type FABPosition = 'bottomRight' | 'bottomCenter';

@Component
export struct HFAB {
  @Prop label: string = '';
  @Prop fabPos: FABPosition = 'bottomRight';
  @Prop color: string = '';
  icon?: Resource;
  onTap?: () => void;
  @StorageProp('theme') theme: ThemeTokens | null = null;

  build() {
    Stack({ alignContent: this.fabPos === 'bottomCenter' ? Alignment.Bottom : Alignment.BottomEnd }) {
      Button() {
        Row({ space: 6 }) {
          if (this.icon !== undefined) { Image(this.icon).width(24).height(24).fillColor('#FFFFFF') }
          else { Text('+').fontSize(28).fontColor('#FFFFFF').fontWeight(this.theme?.fontWeightRegular ?? 400) }
          if (this.label) { Text(this.label).fontSize(this.theme?.fontSizeBody ?? 14).fontColor('#FFFFFF').fontWeight(this.theme?.fontWeightMedium ?? 500).padding({ right: 4 }) }
        }.justifyContent(FlexAlign.Center)
      }
      .height(56).borderRadius(28).padding({ left: this.label ? 20 : 0, right: this.label ? 20 : 0 })
      .backgroundColor(this.color || this.theme?.primary || '#5B8C5A')
      .shadow({ radius: 8, color: `${this.color || this.theme?.primary || '#5B8C5A'}40`, offsetX: 0, offsetY: 4 })
      .onClick(() => { if (this.onTap) this.onTap(); })
    }
    .width('100%').height('100%').hitTestBehavior(HitTestMode.Transparent).padding({ right: 16, bottom: 24 })
  }
}
