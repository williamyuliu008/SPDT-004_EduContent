/**
 * HSearchBar — 搜索栏组件
 *
 * ============================================================================
 * Props 类型定义
 * ============================================================================
 * interface HSearchBarProps {
 *   placeholder?: string;         // 占位提示文字，默认 '搜索'
 *   value?: string;               // 当前输入值
 *   autoFocus?: boolean;          // 是否自动聚焦，默认 false
 *   showCancel?: boolean;         // 是否显示取消按钮，默认 true
 *   debounceMs?: number;          // 防抖毫秒，默认 300（0 = 不防抖）
 *   onChange?: (value: string) => void; // 输入变更回调
 *   onSearch?: (value: string) => void; // 搜索提交回调
 *   onCancel?: () => void;        // 取消回调
 * }
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * HSearchBar({
 *   placeholder: '搜索笔记...',
 *   onChange: (val: string) => { this.searchKeyword = val; this.filterNotes(); },
 *   onCancel: () => { this.showSearch = false; }
 * })
 */

import { ThemeTokens } from '../theme/tokens';

// ---- 组件 ----

@Component
export struct HSearchBar {
  @Prop placeholder: string = '搜索';
  @Prop autoFocus: boolean = false;
  @Prop showCancel: boolean = true;
  @Prop debounceMs: number = 300;
  @Link value: string;
  onChange?: (value: string) => void;
  onSearch?: (value: string) => void;
  onCancel?: () => void;

  @StorageProp('theme') theme: ThemeTokens | null = null;

  /** 内部防抖定时器 ID */
  private debounceTimer: number = -1;

  aboutToDisappear(): void {
    if (this.debounceTimer >= 0) {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = -1;
    }
  }

  private handleChange(newValue: string): void {
    if (this.debounceMs > 0) {
      // 防抖模式：延迟触发 onChange
      if (this.debounceTimer >= 0) {
        clearTimeout(this.debounceTimer);
      }
      this.debounceTimer = setTimeout(() => {
        if (this.onChange) {
          this.onChange(newValue);
        }
      }, this.debounceMs);
    } else {
      // 无防抖：立即触发
      if (this.onChange) {
        this.onChange(newValue);
      }
    }
  }

  private handleSubmit(): void {
    if (this.onSearch) {
      this.onSearch(this.value);
    }
  }

  private handleCancel(): void {
    if (this.onCancel) {
      this.onCancel();
    }
    this.value = '';
    if (this.onChange) {
      this.onChange('');
    }
  }

  build() {
    Row({ space: this.theme?.spacingSmall ?? 8 }) {
      // ---- 搜索输入区 ----
      Row({ space: 6 }) {
        Text('🔍')
          .fontSize(16)

        TextInput({ placeholder: this.placeholder, text: this.value })
          .layoutWeight(1)
          .height(36)
          .backgroundColor('transparent')
          .border({ width: 0 })
          .fontSize(this.theme?.fontSizeBody ?? 14)
          .onChange((value: string) => {
            this.handleChange(value);
          })
          .onSubmit(() => {
            this.handleSubmit();
          })
      }
      .width('100%')
      .height(40)
      .padding({ left: this.theme?.spacingMedium ?? 12, right: this.theme?.spacingMedium ?? 12 })
      .backgroundColor(this.theme?.surfaceVariant ?? '#F0F0F0')
      .borderRadius(this.theme?.radiusMedium ?? 12)
      .layoutWeight(1)

      // ---- 取消按钮 ----
      if (this.showCancel) {
        Text('取消')
          .fontSize(this.theme?.fontSizeBody ?? 14)
          .fontColor(this.theme?.primary ?? '#5B8C5A')
          .fontWeight(this.theme?.fontWeightMedium ?? 500)
          .onClick(() => {
            this.handleCancel();
          })
      }
    }
    .width('100%')
    .padding({
      left: this.theme?.spacingMedium ?? 12,
      right: this.theme?.spacingMedium ?? 12,
      top: this.theme?.spacingSmall ?? 8,
      bottom: this.theme?.spacingSmall ?? 8
    })
  }
}
