/**
 * Index.ets — 思维导图 (ThinkKit MindMap)
 *
 * 功能:
 *   - 节点树展示（展开/折叠）
 *   - 点击选中、编辑节点
 *   - 添加/删除子节点
 *   - 颜色标记（6色）
 *   - 双指缩放 & 单指平移
 *   - 导出为文本大纲
 */
import { AppConfig } from '../app.config';
import { MindMapEngine, MindMapNode, VisibleNode, COLOR_PALETTE, COLOR_NAMES } from '../model/MindMapData';

@Entry
@Component
struct Index {
  @State engine: MindMapEngine = new MindMapEngine('中心主题');
  @State selectedId: string = '';
  @State visibleNodes: VisibleNode[] = [];
  @State scaleValue: number = 1.0;
  @State showColorPicker: boolean = false;
  @State showEditDialog: boolean = false;
  @State editText: string = '';
  @State exportText: string = '';
  @State showExport: boolean = false;
  @State showAddDialog: boolean = false;
  @State addText: string = '';

  aboutToAppear(): void {
    this.refreshView();
  }

  refreshView(): void {
    this.engine.selectedNodeId = this.selectedId;
    this.visibleNodes = this.engine.collectVisibleNodes();
  }

  build() {
    Stack() {
      Column() {
        // ========== 顶部栏 ==========
        Row() {
          Text(AppConfig.appName)
            .fontSize(18).fontWeight(700).fontColor('#FFFFFF')
          Blank()
          Text(this.getNodeCount() + ' 节点')
            .fontSize(12).fontColor('#FFFFFF').opacity(0.7)
            .margin({ right: 12 })
          Text('📤')
            .fontSize(20)
            .onClick(() => {
              this.exportText = this.engine.exportOutline();
              this.showExport = true;
            })
        }
        .width('100%').height(48)
        .padding({ left: 16, right: 16 })
        .backgroundColor(AppConfig.primaryColor)

        // ========== 导图画布（可缩放/平移） ==========
        Stack() {
          Scroll() {
            Column() {
              ForEach(this.visibleNodes, (vn: VisibleNode, idx: number) => {
                this.buildNodeRow(vn)
              }, (vn: VisibleNode): string => vn.node.id)
              // 底部留白
              Row().width('100%').height(80)
            }
            .width('100%')
            .scale({ x: this.scaleValue, y: this.scaleValue })
          }
          .scrollable(ScrollDirection.Vertical)
          .width('100%').layoutWeight(1)
          .backgroundColor(AppConfig.bgColor)
          .gesture(
            PinchGesture({ fingers: 2 })
              .onActionUpdate((event: GestureEvent) => {
                let newScale: number = this.scaleValue * event.scale;
                this.scaleValue = Math.max(0.5, Math.min(2.5, newScale));
              })
          )
        }
        .layoutWeight(1)

        // ========== 底部工具栏 ==========
        Column() {
          // 颜色选择器
          if (this.showColorPicker) {
            Row({ space: 4 }) {
              Text('颜色标记:').fontSize(12).fontColor('#666')
              ForEach(COLOR_NAMES, (name: string, ci: number) => {
                Row() {
                  if (ci > 0) {
                    Row()
                      .width(22).height(22)
                      .borderRadius(11)
                      .backgroundColor(COLOR_PALETTE[ci])
                      .border({ width: 1, color: '#DDD' })
                  } else {
                    Row()
                      .width(22).height(22)
                      .borderRadius(11)
                      .backgroundColor('#FFFFFF')
                      .border({ width: 1, color: '#CCC' })
                  }
                }
                .padding(3)
                .borderRadius(14)
                .backgroundColor(this.getSelectedColor() === ci ? (AppConfig.primaryColor + '20') : 'transparent')
                .border({ width: this.getSelectedColor() === ci ? 1.5 : 0, color: AppConfig.primaryColor })
                .onClick(() => this.setColor(ci))
              }, (name: string): string => name)
            }
            .width('100%')
            .padding({ left: 12, right: 12, top: 6, bottom: 6 })
            .backgroundColor('#FFFFFF')
          }

          // 操作按钮行
          Row({ space: 8 }) {
            this.buildToolBtn('➕', '添加子节点', () => this.startAddChild())
            this.buildToolBtn('✏️', '编辑', () => this.startEdit())
            this.buildToolBtn('🎨', '颜色', () => { this.showColorPicker = !this.showColorPicker; })
            this.buildToolBtn('🗑', '删除', () => this.deleteSelected())
            this.buildToolBtn('📤', '导出', () => {
              this.exportText = this.engine.exportOutline();
              this.showExport = true;
            })
          }
          .width('100%')
          .padding({ left: 8, right: 8, top: 6, bottom: 8 })
          .backgroundColor('#FFFFFF')
          .border({ width: { top: 0.5 }, color: '#E5E5E5' })
        }
      }
      .width('100%').height('100%')

      // ========== 导出弹窗 ==========
      if (this.showExport) {
        this.buildExportSheet()
      }

      // ========== 添加子节点弹窗 ==========
      if (this.showAddDialog) {
        this.buildAddDialog()
      }

      // ========== 编辑弹窗 ==========
      if (this.showEditDialog) {
        this.buildEditDialog()
      }
    }
    .width('100%').height('100%')
  }

  // ================= 节点行 =================
  @Builder
  buildNodeRow(vn: VisibleNode) {
    Row() {
      // 缩进
      if (vn.depth * 28 > 0) {
        Row().width(vn.depth * 28).height(1)
      }
      // 展开/折叠
      if (vn.node.children.length > 0) {
        Text(vn.node.expanded ? '▼' : '▶')
          .fontSize(10).fontColor('#999')
          .width(20).textAlign(TextAlign.Center)
          .onClick(() => {
            this.engine.toggleExpand(vn.node.id);
            this.refreshView();
          })
      } else {
        Row().width(20)
      }
      // 颜色指示条
      if (vn.node.color > 0) {
        Row()
          .width(3).height(24)
          .backgroundColor(COLOR_PALETTE[vn.node.color])
          .borderRadius(1.5)
          .margin({ right: 6 })
      }
      // 节点文本
      Text(vn.node.label)
        .fontSize(14).fontWeight(vn.depth === 0 ? 600 : 400)
        .fontColor(vn.node.id === this.selectedId ? AppConfig.primaryColor : '#1C1C1E')
        .maxLines(2).textOverflow({ overflow: TextOverflow.Ellipsis })
        .layoutWeight(1)
      // 子节点数
      if (vn.node.children.length > 0) {
        Text('(' + this.countDescendants(vn.node) + ')')
          .fontSize(10).fontColor('#BBB')
          .margin({ left: 4, right: 8 })
      }
    }
    .width('100%')
    .padding({ left: 8, right: 12, top: 8, bottom: 8 })
    .backgroundColor(vn.node.id === this.selectedId ? (AppConfig.primaryColor + '15') : (COLOR_PALETTE[vn.node.color]))
    .borderRadius(6)
    .border({ width: 1.5, color: vn.node.id === this.selectedId ? AppConfig.primaryColor : 'transparent' })
    .margin({ left: 8, right: 8, top: 2, bottom: 2 })
    .onClick(() => {
      this.selectedId = vn.node.id;
      this.refreshView();
    })
    .gesture(
      LongPressGesture()
        .onAction(() => {
          this.selectedId = vn.node.id;
          this.refreshView();
          // 弹出操作菜单（用 showColorPicker + editText 模拟）
        })
    )
  }

  // ================= 工具栏按钮 =================
  @Builder
  buildToolBtn(icon: string, label: string, action: () => void) {
    Column({ space: 1 }) {
      Text(icon).fontSize(20)
      Text(label).fontSize(9).fontColor('#888')
    }
    .layoutWeight(1)
    .padding({ top: 4, bottom: 2 })
    .borderRadius(8)
    .backgroundColor('#F5F5F5')
    .onClick(() => action())
  }

  // ================= 编辑对话框 =================
  @Builder
  buildEditDialog() {
    Column({ space: 12 }) {
      Text('编辑节点').fontSize(16).fontWeight(600).fontColor('#1C1C1E')
      TextInput({ text: this.editText, placeholder: '输入节点内容' })
        .width('100%').height(40)
        .fontSize(14).backgroundColor('#F5F5F5').borderRadius(8)
        .onChange((value: string) => { this.editText = value; })
      Row({ space: 8 }) {
        Button('取消')
          .fontSize(14).layoutWeight(1).height(38)
          .backgroundColor('#F0F0F0').fontColor('#666').borderRadius(8)
          .onClick(() => { this.showEditDialog = false; })
        Button('确认')
          .fontSize(14).layoutWeight(1).height(38)
          .backgroundColor(AppConfig.primaryColor).borderRadius(8)
          .onClick(() => this.confirmEdit())
      }.width('100%')
    }
    .width('80%')
    .padding(20)
    .backgroundColor('#FFFFFF')
    .borderRadius(12)
  }

  // ================= 导出面板 =================
  @Builder
  buildExportSheet() {
    Column() {
      Column() {
        Row() {
          Text('导出大纲').fontSize(16).fontWeight(600)
          Blank()
          Text('✕').fontSize(18).fontColor('#999').onClick(() => { this.showExport = false; })
        }.width('100%').margin({ bottom: 12 })
        Scroll() {
          Text(this.exportText)
            .fontSize(13).fontColor('#333')
            .fontFamily('monospace')
            .width('100%')
        }
        .height(200).backgroundColor('#F8F8F8').borderRadius(8).padding(12)
        Row({ space: 8 }) {
          Button('复制')
            .fontSize(14).layoutWeight(1).height(38)
            .backgroundColor(AppConfig.primaryColor).borderRadius(8)
          Button('关闭')
            .fontSize(14).layoutWeight(1).height(38)
            .backgroundColor('#F0F0F0').fontColor('#666').borderRadius(8)
            .onClick(() => { this.showExport = false; })
        }.width('100%').margin({ top: 12 })
      }
      .width('88%').padding(20).backgroundColor('#FFFFFF').borderRadius(12)
    }
    .width('100%').height('100%')
    .justifyContent(FlexAlign.Center)
    .backgroundColor('#00000040')
    .onClick(() => { this.showExport = false; })
  }

  // ================= 添加子节点弹窗 =================
  @Builder
  buildAddDialog() {
    Column() {
      Column({ space: 12 }) {
        Text('添加子节点').fontSize(16).fontWeight(600).fontColor('#1C1C1E')
        Text('父节点: ' + this.getSelectedLabel())
          .fontSize(13).fontColor('#888')
        TextInput({ text: this.addText, placeholder: '输入新节点内容' })
          .width('100%').height(40)
          .fontSize(14).backgroundColor('#F5F5F5').borderRadius(8)
          .onChange((value: string) => { this.addText = value; })
        Row({ space: 8 }) {
          Button('取消')
            .fontSize(14).layoutWeight(1).height(38)
            .backgroundColor('#F0F0F0').fontColor('#666').borderRadius(8)
            .onClick(() => { this.showAddDialog = false; })
          Button('添加')
            .fontSize(14).layoutWeight(1).height(38)
            .backgroundColor(AppConfig.primaryColor).borderRadius(8)
            .onClick(() => this.confirmAdd())
        }.width('100%')
      }
      .width('80%').padding(20).backgroundColor('#FFFFFF').borderRadius(12)
    }
    .width('100%').height('100%')
    .justifyContent(FlexAlign.Center)
    .backgroundColor('#00000040')
    .onClick(() => { this.showAddDialog = false; })
  }

  // ================= 操作方法 =================
  startEdit(): void {
    if (!this.selectedId) {
      return;
    }
    let node = this.engine.findNode(this.selectedId);
    if (node !== null) {
      this.editText = node.label;
      this.showEditDialog = true;
    }
  }

  confirmEdit(): void {
    if (this.selectedId && this.editText.trim()) {
      this.engine.setLabel(this.selectedId, this.editText.trim());
      this.refreshView();
    }
    this.showEditDialog = false;
  }

  startAddChild(): void {
    let targetId = this.selectedId || this.engine.root.id;
    this.addText = '';
    this.showAddDialog = true;
    // 确保选中
    if (!this.selectedId) {
      this.selectedId = targetId;
    }
  }

  confirmAdd(): void {
    let targetId = this.selectedId || this.engine.root.id;
    let label = this.addText.trim();
    if (label) {
      this.engine.addChild(targetId, label);
      this.refreshView();
    }
    this.showAddDialog = false;
    this.addText = '';
  }

  deleteSelected(): void {
    if (this.selectedId && this.selectedId !== this.engine.root.id) {
      this.engine.deleteNode(this.selectedId);
      this.selectedId = '';
      this.refreshView();
    }
  }

  setColor(ci: number): void {
    if (this.selectedId) {
      this.engine.setColor(this.selectedId, ci);
      this.refreshView();
    }
  }

  getSelectedColor(): number {
    if (!this.selectedId) {
      return 0;
    }
    let node = this.engine.findNode(this.selectedId);
    if (node !== null) {
      return node.color;
    }
    return 0;
  }

  getSelectedLabel(): string {
    if (!this.selectedId) {
      return this.engine.root.label;
    }
    let node = this.engine.findNode(this.selectedId);
    if (node !== null) {
      return node.label;
    }
    return '';
  }

  getNodeCount(): number {
    let count = 0;
    let collectAll = (node: MindMapNode): void => {
      count++;
      for (let child of node.children) {
        collectAll(child);
      }
    };
    collectAll(this.engine.root);
    return count;
  }

  countDescendants(node: MindMapNode): number {
    let count = 0;
    for (let child of node.children) {
      count++;
      count += this.countDescendantsInner(child);
    }
    return count;
  }

  private countDescendantsInner(node: MindMapNode): number {
    let count = 0;
    for (let child of node.children) {
      count++;
      count += this.countDescendantsInner(child);
    }
    return count;
  }
}
