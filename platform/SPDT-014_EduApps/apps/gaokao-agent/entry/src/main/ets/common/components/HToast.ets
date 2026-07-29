/**
 * HToast — 轻提示组件
 *
 * 从 common/theme/tokens 统一引用 ThemeTokens。
 * 注意：_ToastManager 模块级单例在 ArkTS 严格模式下可能受限，
 *       若编译器报错可改为通过 AppStorage 传递状态。
 *
 * ============================================================================
 * Props 类型定义
 * ============================================================================
 * interface HToastConfig {
 *   message: string;              // 提示文字（必填）
 *   type?: ToastType;             // 提示类型：'info' | 'success' | 'warning' | 'error'，默认 'info'
 *   duration?: number;            // 显示时长(ms)，默认 2000
 *   position?: ToastPosition;     // 显示位置：'top' | 'center' | 'bottom'，默认 'center'
 *   icon?: Resource;              // 自定义图标（可选），默认按 type 自动匹配
 * }
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * HToast.show({ message: '笔记已保存' })
 * HToast.show({ message: '删除成功', type: 'success' })
 * HToast.show({ message: '网络连接失败', type: 'error', duration: 3000 })
 */

import { ThemeTokens } from '../theme/tokens';

// ---- 类型定义 ----

export type ToastType = 'info' | 'success' | 'warning' | 'error';
export type ToastPosition = 'top' | 'center' | 'bottom';

export interface HToastConfig {
  message: string;
  type?: ToastType;
  duration?: number;
  position?: ToastPosition;
  icon?: Resource;
}

// ---- Toast 管理器（模块级单例） ----

class _ToastManager {
  visible: boolean = false;
  config: HToastConfig = { message: '' };

  show(config: HToastConfig): void {
    this.config = config;
    this.visible = true;
    const dur = config.duration ?? 2000;
    setTimeout(() => {
      this.visible = false;
    }, dur);
  }
}

const toastManager = new _ToastManager();

// ---- 组件 ----

@Component
export struct HToast {
  @StorageProp('theme') theme: ThemeTokens | null = null;

  /** 根据 type 返回背景色 */
  private getBackgroundColor(type: ToastType): string {
    switch (type) {
      case 'success': return this.theme?.success ?? '#4CAF50';
      case 'warning': return this.theme?.warning ?? '#FF9800';
      case 'error':   return this.theme?.error ?? '#F44336';
      case 'info':
      default:        return this.theme?.onSurface ?? '#323232';
    }
  }

  /** 根据 type 返回默认图标字符 */
  private getDefaultIcon(type: ToastType): string {
    switch (type) {
      case 'success': return '✓';
      case 'warning': return '⚠';
      case 'error':   return '✕';
      case 'info':
      default:        return 'ℹ';
    }
  }

  build() {
    if (!toastManager.visible) {
      Column().width(0).height(0)
      return;
    }

    Column() {
      Row({ space: 8 }) {
        if (toastManager.config.icon !== undefined) {
          Image(toastManager.config.icon)
            .width(20)
            .height(20)
            .fillColor('#FFFFFF')
        } else {
          Text(this.getDefaultIcon(toastManager.config.type ?? 'info'))
            .fontSize(18)
            .fontColor('#FFFFFF')
        }

        Text(toastManager.config.message)
          .fontSize(this.theme?.fontSizeBody ?? 14)
          .fontColor('#FFFFFF')
          .fontWeight(this.theme?.fontWeightMedium ?? 500)
          .maxLines(2)
      }
      .padding({
        left: this.theme?.spacingMedium ?? 16,
        right: this.theme?.spacingMedium ?? 16,
        top: 10,
        bottom: 10
      })
      .backgroundColor(this.getBackgroundColor(toastManager.config.type ?? 'info'))
      .borderRadius(this.theme?.radiusMedium ?? 12)
      .shadow({
        radius: 8,
        color: '#00000020',
        offsetX: 0,
        offsetY: 2
      })
      .opacity(toastManager.visible ? 1 : 0)
      .transition(
        toastManager.visible
          ? TransitionEffect.OPACITY.animation({ duration: 200, curve: Curve.EaseOut })
          : TransitionEffect.OPACITY.animation({ duration: 200, curve: Curve.EaseIn })
      )
    }
    .width('100%')
    .height('100%')
    .hitTestBehavior(HitTestMode.Transparent)
    .justifyContent(
      toastManager.config.position === 'top' ? FlexAlign.Start :
      toastManager.config.position === 'bottom' ? FlexAlign.End :
      FlexAlign.Center
    )
    .alignItems(HorizontalAlign.Center)
    .padding({
      top: toastManager.config.position === 'top' ? 60 : 0,
      bottom: toastManager.config.position === 'bottom' ? 60 : 0
    })
  }

  /**
   * 静态方法：显示轻提示
   */
  static show(config: HToastConfig): void {
    toastManager.show(config);
  }

  /**
   * 静态方法：隐藏当前 Toast
   */
  static hide(): void {
    toastManager.visible = false;
  }
}
