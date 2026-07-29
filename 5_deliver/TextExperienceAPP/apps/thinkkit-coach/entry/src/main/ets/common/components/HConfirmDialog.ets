/**
 * HConfirmDialog — 确认弹窗组件
 *
 * 封装 AlertDialog.show()，提供统一的确认/取消弹窗交互。
 *
 * ============================================================================
 * Props 类型定义
 * ============================================================================
 * interface HConfirmDialogConfig {
 *   title: string;                // 弹窗标题（必填）
 *   message: string;              // 弹窗内容（必填）
 *   confirmLabel?: string;        // 确认按钮文字，默认 '确定'
 *   cancelLabel?: string;         // 取消按钮文字，默认 '取消'
 *   confirmColor?: string;        // 确认按钮颜色，默认使用 theme.error（危险操作红）
 *   cancelColor?: string;         // 取消按钮颜色，默认灰色
 *   danger?: boolean;             // 是否为危险操作（确认按钮变红），默认 true
 *   onConfirm?: () => void;       // 确认回调
 *   onCancel?: () => void;        // 取消回调
 * }
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * HConfirmDialog.show({
 *   title: '确认删除',
 *   message: '删除后不可恢复，确定要删除吗？',
 *   danger: true,
 *   onConfirm: () => { this.deleteNote(); }
 * })
 *
 * HConfirmDialog.show({
 *   title: '放弃编辑',
 *   message: '当前内容尚未保存，确定要放弃吗？',
 *   danger: false,
 *   confirmLabel: '放弃',
 *   cancelLabel: '继续编辑',
 *   onConfirm: () => { this.navPathStack.pop(); }
 * })
 */

import { ThemeTokens } from '../theme/tokens';

// ---- 类型定义 ----

export interface HConfirmDialogConfig {
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  confirmColor?: string;
  cancelColor?: string;
  danger?: boolean;
  onConfirm?: () => void;
  onCancel?: () => void;
}

// ---- 静态工具类 ----

export class HConfirmDialog {
  /**
   * 显示确认弹窗
   *
   * @param config 弹窗配置
   *
   * @example
   * HConfirmDialog.show({
   *   title: '确认删除',
   *   message: '删除后不可恢复',
   *   onConfirm: () => { this.deleteItem() }
   * })
   */
  static show(config: HConfirmDialogConfig): void {
    const isDanger = config.danger ?? true;

    AlertDialog.show({
      title: config.title,
      message: config.message,
      autoCancel: true,
      alignment: DialogAlignment.Center,
      primaryButton: {
        value: config.cancelLabel ?? '取消',
        fontColor: config.cancelColor ?? '#888888',
        action: () => {
          if (config.onCancel) {
            config.onCancel();
          }
        }
      },
      secondaryButton: {
        value: config.confirmLabel ?? '确定',
        fontColor: config.confirmColor ?? (isDanger ? '#FF3B30' : '#5B8C5A'),
        action: () => {
          if (config.onConfirm) {
            config.onConfirm();
          }
        }
      }
    });
  }

  /**
   * 显示信息提示弹窗（单按钮）
   *
   * @param title 标题
   * @param message 内容
   * @param buttonLabel 按钮文字，默认 '知道了'
   * @param onConfirm 点击回调
   */
  static alert(
    title: string,
    message: string,
    buttonLabel: string = '知道了',
    onConfirm?: () => void
  ): void {
    AlertDialog.show({
      title,
      message,
      autoCancel: true,
      alignment: DialogAlignment.Center,
      primaryButton: {
        value: buttonLabel,
        fontColor: '#5B8C5A',
        action: () => {
          if (onConfirm) {
            onConfirm();
          }
        }
      }
    });
  }
}
