/**
 * HButton — 标准化按钮组件 (API 26 strict mode)
 */
import { ThemeTokens } from '../theme/tokens';

export type ButtonType = 'primary' | 'secondary' | 'ghost';
export type ButtonSize = 'small' | 'medium' | 'large';

export interface HButtonProps {
  label: string;
  type: ButtonType;
  buttonSize?: ButtonSize;
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  onTap?: () => void;
}

@Component
export struct HButton {
  @Prop label: string = '';
  @Prop type: ButtonType = 'primary';
  @Prop buttonSize: ButtonSize = 'medium';
  @Prop disabled: boolean = false;
  @Prop loading: boolean = false;
  @Prop fullWidth: boolean = false;
  onTap?: () => void;
  @StorageProp('theme') theme: ThemeTokens | null = null;

  private getBgColor(): string {
    if (this.disabled) { return this.theme?.outline ?? '#DCDCDC'; }
    switch (this.type) {
      case 'primary': return this.theme?.primary ?? '#5B8C5A';
      case 'secondary': return this.theme?.surfaceVariant ?? '#F0F0F0';
      case 'ghost': return 'transparent';
      default: return this.theme?.primary ?? '#5B8C5A';
    }
  }
  private getFontColor(): string {
    if (this.disabled) { return '#A0A0A0'; }
    switch (this.type) {
      case 'primary': return this.theme?.onPrimary ?? '#FFFFFF';
      case 'secondary': return this.theme?.onSurface ?? '#1C1C1E';
      case 'ghost': return this.theme?.primary ?? '#5B8C5A';
      default: return this.theme?.onPrimary ?? '#FFFFFF';
    }
  }
  private getH(): number { return this.buttonSize === 'small' ? 36 : this.buttonSize === 'large' ? 52 : 44; }
  private getFS(): number { return this.buttonSize === 'small' ? 13 : this.buttonSize === 'large' ? 17 : 15; }

  build() {
    Button() {
      if (this.loading) {
        Row({ space: 6 }) {
          LoadingProgress().width(16).height(16).color(this.getFontColor())
          Text(this.label).fontSize(this.getFS()).fontColor(this.getFontColor()).fontWeight(this.theme?.fontWeightMedium ?? 500)
        }.justifyContent(FlexAlign.Center)
      } else {
        Text(this.label).fontSize(this.getFS()).fontColor(this.getFontColor()).fontWeight(this.theme?.fontWeightMedium ?? 500)
      }
    }
    .width(this.fullWidth ? '100%' : undefined)
    .height(this.getH())
    .backgroundColor(this.getBgColor())
    .borderRadius(this.theme?.radiusMedium ?? 12)
    .border(this.type === 'ghost' && !this.disabled ? { width: 1, color: this.theme?.primary ?? '#5B8C5A' } : { width: 0, color: 'transparent' })
    .enabled(!this.disabled)
    .opacity(this.disabled ? 0.5 : 1.0)
    .onClick(() => { if (!this.loading && !this.disabled && this.onTap) this.onTap(); })
  }
}
