/**
 * HNavBar — 导航栏 (API 26 strict mode - no backgroundColor prop conflict)
 */
import { ThemeTokens } from '../theme/tokens';

export interface NavBarAction { icon?: Resource; label?: string; onTap: () => void; }

@Component
export struct HNavBar {
  @Prop title: string = '';
  @Prop showBack: boolean = true;
  @Prop backLabel: string = '';
  rightActions?: NavBarAction[];
  navBgColor?: string;
  onBack?: () => void;
  @StorageProp('theme') theme: ThemeTokens | null = null;

  build() {
    Row() {
      if (this.showBack) {
        Row({ space: 4 }) {
          Text('←').fontSize(20).fontColor(this.theme?.primary ?? '#5B8C5A')
          if (this.backLabel) { Text(this.backLabel).fontSize(this.theme?.fontSizeBody ?? 14).fontColor(this.theme?.primary ?? '#5B8C5A').fontWeight(this.theme?.fontWeightMedium ?? 500) }
        }.padding({ left: 4, right: 12, top: 8, bottom: 8 }).onClick(() => { if (this.onBack) this.onBack(); })
      }
      Text(this.title).fontSize(this.theme?.fontSizeTitle ?? 18).fontWeight(this.theme?.fontWeightBold ?? 700).fontColor(this.theme?.onSurface ?? '#1C1C1E').layoutWeight(1).textAlign(this.showBack ? TextAlign.Center : TextAlign.Start).maxLines(1).textOverflow({ overflow: TextOverflow.Ellipsis })
      if (this.rightActions && this.rightActions.length > 0) {
        Row({ space: this.theme?.spacingSmall ?? 8 }) {
          ForEach(this.rightActions, (a: NavBarAction, i: number) => {
            Row({ space: 4 }) {
              if (a.icon !== undefined) { Image(a.icon).width(24).height(24) }
              if (a.label) { Text(a.label).fontSize(this.theme?.fontSizeBody ?? 14).fontColor(this.theme?.primary ?? '#5B8C5A') }
            }.padding({ left: 8, right: 8, top: 8, bottom: 8 }).onClick(() => { a.onTap(); })
          }, (a: NavBarAction, i: number): string => i.toString())
        }.padding({ right: 4 })
      }
    }
    .width('100%').height(56).padding({ left: this.theme?.spacingMedium ?? 12, right: this.theme?.spacingMedium ?? 12 })
    .backgroundColor(this.navBgColor ?? this.theme?.surface ?? '#FFFFFF')
    .border({ width: { bottom: 0.5 }, color: this.theme?.outline ?? '#DCDCDC' })
  }
}
