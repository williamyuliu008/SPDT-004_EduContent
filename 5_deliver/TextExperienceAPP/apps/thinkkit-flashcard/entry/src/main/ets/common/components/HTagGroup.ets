/**
 * HTagGroup — 标签组组件（多标签联动）
 *
 * 支持单选/多选模式下的标签列表，自动换行。
 *
 * ============================================================================
 * Props 类型定义
 * ============================================================================
 * interface HTagGroupProps {
 *   tags: TagItem[];                 // 标签列表（必填）
 *   selectedIds?: string[];          // 当前选中标签 ID 列表
 *   multiSelect?: boolean;           // 是否多选，默认 false（单选模式）
 *   onChange?: (selectedIds: string[]) => void; // 选中变更回调
 * }
 *
 * interface TagItem {
 *   id: string;                      // 唯一标识
 *   label: string;                   // 显示文字
 *   color?: string;                  // 标签颜色
 * }
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * // 单选模式
 * HTagGroup({
 *   tags: [
 *     { id: 'all', label: '全部' },
 *     { id: 'tech', label: '技术' },
 *     { id: 'life', label: '生活' }
 *   ],
 *   selectedIds: [this.selectedCategory],
 *   onChange: (ids: string[]) => { this.selectedCategory = ids[0] || 'all'; this.filter() }
 * })
 *
 * // 多选模式
 * HTagGroup({
 *   tags: [{ id: 'arkts', label: 'ArkTS' }, { id: 'ui', label: 'UI' }],
 *   selectedIds: this.selectedTags,
 *   multiSelect: true,
 *   onChange: (ids: string[]) => { this.selectedTags = ids; this.filter() }
 * })
 */

import { ThemeTokens } from '../theme/tokens';

// ---- 类型定义 ----

export interface TagItem {
  id: string;
  label: string;
  color?: string;
}

// ---- 组件 ----

@Component
export struct HTagGroup {
  @Prop tags: TagItem[] = [];
  @Prop multiSelect: boolean = false;
  @Link selectedIds: string[];
  onChange?: (selectedIds: string[]) => void;

  @StorageProp('theme') theme: ThemeTokens | null = null;

  private isSelected(tagId: string): boolean {
    return this.selectedIds.indexOf(tagId) >= 0;
  }

  private handleTagTap(tag: TagItem): void {
    let newSelected: string[];

    if (this.multiSelect) {
      // 多选模式：toggle
      if (this.isSelected(tag.id)) {
        newSelected = this.selectedIds.filter((id: string) => id !== tag.id);
      } else {
        newSelected = [...this.selectedIds, tag.id];
      }
    } else {
      // 单选模式：点击已选中的则取消选中，否则切换
      if (this.isSelected(tag.id)) {
        newSelected = [];
      } else {
        newSelected = [tag.id];
      }
    }

    this.selectedIds = newSelected;
    if (this.onChange) {
      this.onChange(newSelected);
    }
  }

  build() {
    Flex({ wrap: FlexWrap.Wrap, direction: FlexDirection.Row }) {
      ForEach(
        this.tags,
        (tag: TagItem, index: number) => {
          Row() {
            Text(tag.label)
              .fontSize(this.theme?.fontSizeCaption ?? 12)
              .fontColor(
                this.isSelected(tag.id)
                  ? '#FFFFFF'
                  : (tag.color || this.theme?.primary || '#5B8C5A')
              )
              .fontWeight(this.theme?.fontWeightMedium ?? 500)
              .maxLines(1)
          }
          .height(32)
          .padding({ left: 12, right: 12 })
          .backgroundColor(
            this.isSelected(tag.id)
              ? (tag.color || this.theme?.primary || '#5B8C5A')
              : 'transparent'
          )
          .border({
            width: 1,
            color: tag.color || this.theme?.primary || '#5B8C5A',
            style: BorderStyle.Solid
          })
          .borderRadius(16)
          .margin({ right: this.theme?.spacingSmall ?? 8, bottom: this.theme?.spacingSmall ?? 8 })
          .onClick(() => {
            this.handleTagTap(tag);
          })
        },
        (tag: TagItem) => tag.id
      )
    }
    .width('100%')
    .padding({ left: this.theme?.spacingMedium ?? 12, right: this.theme?.spacingMedium ?? 12 })
  }
}
