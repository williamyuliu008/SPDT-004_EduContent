/**
 * Index.ets — 大纲速记 完整版
 * 层级大纲 + 新增/编辑/删除/折叠
 */
import { HNavBar } from '../common';
import { AppConfig } from '../app.config';

interface OutlineItem { id: string; text: string; level: number; children: OutlineItem[]; collapsed: boolean; }

@Entry
@Component
struct Index {
  @State items: OutlineItem[] = [
    { id: '1', text: '鸿蒙开发学习计划', level: 0, collapsed: false, children: [
      { id: '1a', text: 'ArkTS 基础语法', level: 1, collapsed: false, children: [
        { id: '1a1', text: '变量声明与类型标注', level: 2, collapsed: false, children: [] },
        { id: '1a2', text: '@State/@Link/@Prop', level: 2, collapsed: false, children: [] }
      ]},
      { id: '1b', text: 'Stage 模型', level: 1, collapsed: true, children: [
        { id: '1b1', text: 'EntryAbility 生命周期', level: 2, collapsed: false, children: [] }
      ]}
    ]},
    { id: '2', text: '项目发布 Checklist', level: 0, collapsed: false, children: [
      { id: '2a', text: '编译验证通过', level: 1, collapsed: false, children: [] },
      { id: '2b', text: '真机测试完成', level: 1, collapsed: false, children: [] },
      { id: '2c', text: '签名与上架', level: 1, collapsed: false, children: [] }
    ]}
  ];
  @State editId: string = '';
  @State editText: string = '';
  @State addParentId: string = '';
  @State addText: string = '';
  @State nextId: number = 100;
  private genId(): string { return 'n' + (this.nextId++).toString(); }

  private toggle(item: OutlineItem): void { item.collapsed = !item.collapsed; }
  private startEdit(item: OutlineItem): void { this.editId = item.id; this.editText = item.text; this.addParentId = ''; }
  private saveEdit(): void {
    const found = this.findItem(this.items, this.editId);
    if (found && this.editText.trim()) { found.text = this.editText.trim(); }
    this.editId = ''; this.editText = '';
  }
  private cancelEdit(): void { this.editId = ''; this.editText = ''; }
  private startAdd(parentId: string): void { this.addParentId = parentId; this.addText = ''; this.editId = ''; }
  private confirmAdd(): void {
    if (!this.addText.trim()) { this.addParentId = ''; return; }
    const newItem: OutlineItem = { id: this.genId(), text: this.addText.trim(), level: 0, collapsed: false, children: [] };
    if (this.addParentId) {
      const parent = this.findItem(this.items, this.addParentId);
      if (parent) { newItem.level = parent.level + 1; parent.children.push(newItem); parent.collapsed = false; }
    } else { newItem.level = 0; this.items.push(newItem); }
    this.addParentId = ''; this.addText = '';
  }
  private deleteItem(id: string): void { this.removeFrom(this.items, id); }

  private findItem(list: OutlineItem[], id: string): OutlineItem | null {
    for (let i = 0; i < list.length; i++) {
      if (list[i].id === id) return list[i];
      const found = this.findItem(list[i].children, id);
      if (found) return found;
    }
    return null;
  }

  private removeFrom(list: OutlineItem[], id: string): boolean {
    for (let i = 0; i < list.length; i++) {
      if (list[i].id === id) { list.splice(i, 1); return true; }
      if (this.removeFrom(list[i].children, id)) return true;
    }
    return false;
  }

  @Builder
  renderItem(item: OutlineItem) {
    Column() {
      Row() {
        if (item.children.length > 0) {
          Text(item.collapsed ? '▶' : '▼').fontSize(10).fontColor('#888').width(20)
            .onClick((): void => this.toggle(item))
        } else {
          Text('•').fontSize(14).fontColor('#CCC').width(20)
        }
        if (this.editId === item.id) {
          TextInput({ text: this.editText }).fontSize(14).layoutWeight(1).height(36).borderRadius(6).backgroundColor('#F0F0F0').padding(8)
            .onChange((v: string): void => { this.editText = v; })
          Text('✓').fontSize(16).fontColor('#34C759').width(32).textAlign(TextAlign.Center).onClick((): void => this.saveEdit())
          Text('✗').fontSize(16).fontColor('#FF3B30').width(32).textAlign(TextAlign.Center).onClick((): void => this.cancelEdit())
        } else {
          Text(item.text).fontSize(15).fontColor('#1C1C1E').layoutWeight(1)
            .onClick((): void => this.startEdit(item))
          Text('+').fontSize(14).fontColor('#AAA').width(24).textAlign(TextAlign.Center)
            .onClick((): void => this.startAdd(item.id))
          Text('×').fontSize(14).fontColor('#CCC').width(24).textAlign(TextAlign.Center)
            .onClick((): void => this.deleteItem(item.id))
        }
      }.width('100%').padding({ left: (item.level * 20) + 8, right: 8, top: 6, bottom: 6 })
      if (!item.collapsed && item.children.length > 0) {
        ForEach(item.children, (child: OutlineItem) => { this.renderItem(child) }, (c: OutlineItem): string => c.id)
      }
    }
  }

  build() {
    Column() {
      HNavBar({ title: AppConfig.appName, showBack: false, navBgColor: AppConfig.primaryColor,
        rightActions: [{ label: '+', onTap: (): void => this.startAdd('') }] })

      if (this.addParentId !== '') {
        Row() {
          TextInput({ placeholder: '新条目内容...', text: this.addText }).fontSize(14).layoutWeight(1).height(40).borderRadius(8).backgroundColor('#FFFFFF').border({ width: 1, color: '#DCDCDC' }).padding(10)
            .onChange((v: string): void => { this.addText = v; })
          Text('添加').fontSize(14).fontColor(AppConfig.primaryColor).fontWeight(600).margin({ left: 8 })
            .onClick((): void => this.confirmAdd())
        }.width('100%').padding(12).backgroundColor('#F0F0F0')
      }

      Scroll() {
        Column() {
          ForEach(this.items, (item: OutlineItem) => { this.renderItem(item) }, (item: OutlineItem): string => item.id)
          Column().width('100%').height(200)
        }.width('100%')
      }.layoutWeight(1).backgroundColor('#F5F5F5')
    }.width('100%').height('100%')
  }
}
