/**
 * Index.ets — gaokao language 首页
 * 品牌：GaokaoAgent
 */
import { AppConfig } from '../app.config';

@Entry
@Component
struct Index {
  build() {
    Column() {
      Text(AppConfig.appName)
        .fontSize(24)
        .fontWeight(FontWeight.Bold)
        .fontColor(AppConfig.primaryColor)
      Text(AppConfig.shortDesc)
        .fontSize(14)
        .fontColor('#999999')
        .margin({ top: 8 })
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}
