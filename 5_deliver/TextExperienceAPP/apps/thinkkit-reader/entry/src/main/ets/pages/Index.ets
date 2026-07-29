@Entry
@Component
struct Index {
  @State message: string = 'ThinkKit Reader';

  build() {
    Column() {
      Text(this.message)
        .fontSize(28)
        .fontWeight(FontWeight.Bold)
        .fontColor('#5B8C5A')
        .margin({ top: 80 })
      Text('智能阅读器')
        .fontSize(16)
        .fontColor('#666')
        .margin({ top: 12 })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F7')
  }
}
