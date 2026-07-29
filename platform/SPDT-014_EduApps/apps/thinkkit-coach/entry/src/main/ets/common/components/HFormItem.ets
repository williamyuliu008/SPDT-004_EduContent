/**
 * HFormItem — 表单项组件
 *
 * 从 common/theme/tokens 统一引用 ThemeTokens。
 *
 * ============================================================================
 * Props 类型定义
 * ============================================================================
 * interface HFormItemProps {
 *   label: string;                // 标签文字（必填）
 *   value?: string;               // 当前值（双向绑定）
 *   placeholder?: string;         // 占位提示文字，默认 '请输入'
 *   type?: FormFieldType;         // 字段类型：'text' | 'textarea' | 'number'，默认 'text'
 *   maxLength?: number;           // 最大输入长度，默认 200
 *   required?: boolean;           // 是否必填（显示红色星号），默认 false
 *   errorMessage?: string;        // 校验错误信息（非空时显示红字并变红边框）
 *   onChange?: (value: string) => void;  // 值变更回调
 *   validator?: (value: string) => string | null; // 自定义校验器
 * }
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * HFormItem({ label: '笔记标题', value: this.noteTitle, placeholder: '请输入标题', onChange: (val: string) => { ... } })
 * HFormItem({ label: '邮箱', required: true, validator: (val: string) => /.../.test(val) ? null : '格式不正确' })
 * HFormItem({ label: '正文', type: 'textarea', placeholder: '请输入内容...', value: this.noteBody })
 */

import { ThemeTokens } from '../theme/tokens';

// ---- 类型定义 ----

export type FormFieldType = 'text' | 'textarea' | 'number';

// ---- 组件 ----

@Component
export struct HFormItem {
  @Prop label: string = '';
  @Prop placeholder: string = '请输入';
  @Prop type: FormFieldType = 'text';
  @Prop maxLength: number = 200;
  @Prop required: boolean = false;
  @Link value: string;
  errorMessage?: string;
  onChange?: (value: string) => void;
  validator?: (value: string) => string | null;

  @StorageProp('theme') theme: ThemeTokens | null = null;

  /** 内部错误状态 */
  @State private internalError: string = '';

  /**
   * 处理值变更：通知父组件 + 执行校验
   */
  private handleChange(newValue: string): void {
    if (this.onChange) {
      this.onChange(newValue);
    }
    if (this.validator) {
      const error = this.validator(newValue);
      this.internalError = error ?? '';
    }
  }

  /** 获取当前应显示的错误信息（外部传入优先） */
  private getCurrentError(): string {
    return this.errorMessage ?? this.internalError;
  }

  /** 是否有错误状态 */
  private hasError(): boolean {
    return this.getCurrentError().length > 0;
  }

  build() {
    Column({ space: 6 }) {
      // ---- 标签行 ----
      Row() {
        if (this.required) {
          Text('*')
            .fontSize(this.theme?.fontSizeBody ?? 14)
            .fontColor(this.theme?.error ?? '#FF3B30')
            .margin({ right: 2 })
        }
        Text(this.label)
          .fontSize(this.theme?.fontSizeBody ?? 14)
          .fontColor(this.hasError() ? (this.theme?.error ?? '#FF3B30') : (this.theme?.onSurface ?? '#1C1C1E'))
          .fontWeight(this.theme?.fontWeightMedium ?? 500)
      }

      // ---- 输入区域 ----
      if (this.type === 'textarea') {
        TextArea({ placeholder: this.placeholder, text: this.value })
          .width('100%')
          .height(160)
          .maxLength(this.maxLength)
          .borderRadius(this.theme?.radiusSmall ?? 8)
          .backgroundColor(this.theme?.surface ?? '#FFFFFF')
          .border({
            width: 1,
            color: this.hasError() ? (this.theme?.error ?? '#FF3B30') : (this.theme?.outline ?? '#DCDCDC')
          })
          .padding(this.theme?.spacingMedium ?? 12)
          .onChange((value: string) => {
            this.handleChange(value);
          })
      } else {
        TextInput({ placeholder: this.placeholder, text: this.value })
          .width('100%')
          .height(44)
          .type(this.type === 'number' ? InputType.Number : InputType.Normal)
          .maxLength(this.maxLength)
          .borderRadius(this.theme?.radiusSmall ?? 8)
          .backgroundColor(this.theme?.surface ?? '#FFFFFF')
          .border({
            width: 1,
            color: this.hasError() ? (this.theme?.error ?? '#FF3B30') : (this.theme?.outline ?? '#DCDCDC')
          })
          .padding({
            left: this.theme?.spacingMedium ?? 12,
            right: this.theme?.spacingMedium ?? 12
          })
          .onChange((value: string) => {
            this.handleChange(value);
          })
      }

      // ---- 错误提示 ----
      if (this.hasError()) {
        Text(this.getCurrentError())
          .fontSize(this.theme?.fontSizeCaption ?? 12)
          .fontColor(this.theme?.error ?? '#FF3B30')
          .padding({ left: 4 })
      }
    }
    .width('100%')
    .alignItems(HorizontalAlign.Start)
  }
}
