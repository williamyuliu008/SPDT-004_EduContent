/**
 * HTag — 标签 (API 26 strict mode - no size prop conflict)
 */
import { ThemeTokens } from '../theme/tokens';

export type HTagSize = 'small' | 'medium';

@Component
export struct HTag {
  @Prop label: string = '';
  @Prop selected: boolean = false;
  @Prop color: string = '';
  @Prop tagSize: HTagSize = 'medium';
  @Prop removable: boolean = false;
  onTap?: () => void;
  onRemove?: () => void;
  @StorageProp('theme') theme: ThemeTokens | null = null;

  build() {
    Row({ space: 4 }) {
      Text(this.label).fontSize(this.tagSize === 'small' ? 11 : 13).fontColor(this.selected ? '#FFFFFF' : (this.color || this.theme?.primary || '#5B8C5A')).fontWeight(this.theme?.fontWeightMedium ?? 500).maxLines(1)
      if (this.removable) {
        Text('×').fontSize(this.tagSize === 'small' ? 13 : 15).fontColor(this.selected ? '#FFFFFF' : (this.color || this.theme?.primary || '#5B8C5A')).onClick(() => { if (this.onRemove) this.onRemove(); })
      }
    }
    .height(this.tagSize === 'small' ? 24 : 32).padding({ left: this.tagSize === 'small' ? 8 : 12, right: this.tagSize === 'small' ? 8 : 12 })
    .backgroundColor(this.selected ? (this.color || this.theme?.primary || '#5B8C5A') : 'transparent')
    .border({ width: 1, color: this.color || this.theme?.primary || '#5B8C5A' }).borderRadius(this.tagSize === 'small' ? 12 : 16)
    .onClick(() => { if (this.onTap) this.onTap(); })
  }
}
