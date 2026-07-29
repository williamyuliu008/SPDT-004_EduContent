/**
 * HToast — 轻提示 (API 26 strict mode)
 */
import { ThemeTokens } from '../theme/tokens';

export type ToastType = 'info' | 'success' | 'warning' | 'error';
export type ToastPosition = 'top' | 'center' | 'bottom';

export interface HToastConfig {
  message: string;
  type?: ToastType;
  duration?: number;
  position?: ToastPosition;
  icon?: Resource;
}

class ToastMgr {
  visible: boolean = false;
  config: HToastConfig = { message: '' };
  show(c: HToastConfig): void { this.config = c; this.visible = true; setTimeout(() => { this.visible = false; }, c.duration ?? 2000); }
}
const tm = new ToastMgr();

@Component
export struct HToast {
  @StorageProp('theme') theme: ThemeTokens | null = null;

  build() {
    Stack({ alignContent: tm.config.position === 'top' ? Alignment.Top : tm.config.position === 'bottom' ? Alignment.Bottom : Alignment.Center }) {
      if (tm.visible) {
        Row({ space: 8 }) {
          if (tm.config.icon !== undefined) { Image(tm.config.icon).width(20).height(20).fillColor('#FFFFFF') }
          else { Text(((): string => { const t = tm.config.type ?? 'info'; return t === 'success' ? '✓' : t === 'warning' ? '⚠' : t === 'error' ? '✕' : 'ℹ'; })()).fontSize(18).fontColor('#FFFFFF') }
          Text(tm.config.message).fontSize(this.theme?.fontSizeBody ?? 14).fontColor('#FFFFFF').fontWeight(this.theme?.fontWeightMedium ?? 500).maxLines(2)
        }
        .padding({ left: this.theme?.spacingMedium ?? 16, right: this.theme?.spacingMedium ?? 16, top: 10, bottom: 10 })
        .backgroundColor(((): string => { const t = tm.config.type ?? 'info'; return t === 'success' ? (this.theme?.success ?? '#4CAF50') : t === 'warning' ? (this.theme?.warning ?? '#FF9800') : t === 'error' ? (this.theme?.error ?? '#F44336') : (this.theme?.onSurface ?? '#323232'); })())
        .borderRadius(this.theme?.radiusMedium ?? 12).shadow({ radius: 8, color: '#00000020', offsetX: 0, offsetY: 2 })
      } else {
        Text('').width(0).height(0).fontSize(0)
      }
    }
    .width('100%').height('100%').hitTestBehavior(HitTestMode.Transparent)
    .padding({ top: tm.config.position === 'top' ? 60 : 0, bottom: tm.config.position === 'bottom' ? 60 : 0 })
  }

  static show(config: HToastConfig): void { tm.show(config); }
  static hide(): void { tm.visible = false; }
}
