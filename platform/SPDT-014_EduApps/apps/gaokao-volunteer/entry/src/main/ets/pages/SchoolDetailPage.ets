/**
 * gaokao-volunteer · 院校详情页
 */
import { router } from '@kit.ArkUI';
import { AppConfig } from '../app.config';
import { School, MajorCategory, ScoreLine } from '../model/SchoolModel';
import { schoolService } from '../service/SchoolService';

@Entry
@Component
struct SchoolDetailPage {
  @State school: School | null = null;
  @State activeSection: string = 'info';
  @State isLoading: boolean = true;

  aboutToAppear(): void {
    const params = router.getParams() as Record<string, string>;
    const schoolId = params?.schoolId ?? '';
    this.loadSchool(schoolId);
  }

  async loadSchool(id: string): Promise<void> {
    this.isLoading = true;
    try {
      const context = getContext(this);
      await schoolService.loadSchools(context);
      this.school = schoolService.getSchoolById(id) ?? null;
    } catch (e) {
      console.error('Failed to load school:', JSON.stringify(e));
    } finally {
      this.isLoading = false;
    }
  }

  @Builder
  TagBadge(tag: string) {
    Text(tag)
      .fontSize(12)
      .fontColor(tag === '985' ? '#1A73E8' : tag === '211' ? '#34A853' : '#F29900')
      .backgroundColor(tag === '985' ? '#E8F0FE' : tag === '211' ? '#E6F4EA' : '#FEF7E0')
      .borderRadius(6)
      .padding({ left: 10, right: 10, top: 4, bottom: 4 })
      .margin({ right: 6 })
  }

  @Builder
  SectionTab(title: string, key: string) {
    Column() {
      Text(title)
        .fontSize(14)
        .fontColor(this.activeSection === key ? AppConfig.primaryColor : AppConfig.textSecondary)
        .fontWeight(this.activeSection === key ? FontWeight.Medium : FontWeight.Normal)
      Divider()
        .color(AppConfig.primaryColor)
        .strokeWidth(this.activeSection === key ? 2 : 0)
        .margin({ top: 4 })
    }
    .layoutWeight(1)
    .alignItems(HorizontalAlign.Center)
    .padding({ top: 10, bottom: 10 })
    .onClick(() => { this.activeSection = key; })
  }

  @Builder
  InfoSection() {
    Column() {
      // 基础信息卡片
      Column() {
        Row() {
          Text('📍 所在地')
            .fontSize(13)
            .fontColor(AppConfig.textSecondary)
            .width(80)
          Text(this.school!.province + ' · ' + this.school!.city)
            .fontSize(13)
            .fontColor(AppConfig.textPrimary)
        }
        .width('100%')
        .margin({ bottom: 12 })

        Row() {
          Text('🏛️ 院校类型')
            .fontSize(13)
            .fontColor(AppConfig.textSecondary)
            .width(80)
          Text(this.school!.type)
            .fontSize(13)
            .fontColor(AppConfig.textPrimary)
        }
        .width('100%')
        .margin({ bottom: 12 })

        Row() {
          Text('🏆 全国排名')
            .fontSize(13)
            .fontColor(AppConfig.textSecondary)
            .width(80)
          Text('第 ' + this.school!.rank_national + ' 名')
            .fontSize(13)
            .fontColor(AppConfig.primaryColor)
            .fontWeight(FontWeight.Medium)
        }
        .width('100%')
        .margin({ bottom: 12 })

        Row() {
          Text('📋 院校代码')
            .fontSize(13)
            .fontColor(AppConfig.textSecondary)
            .width(80)
          Text(this.school!.id)
            .fontSize(13)
            .fontColor(AppConfig.textPrimary)
        }
        .width('100%')

        Divider().margin({ top: 12, bottom: 12 })

        Text(this.school!.description)
          .fontSize(13)
          .fontColor(AppConfig.textSecondary)
          .lineHeight(20)
      }
      .width('100%')
      .padding(16)
      .backgroundColor(AppConfig.cardBg)
      .borderRadius(12)
      .margin({ top: 12 })
    }
    .width('100%')
  }

  @Builder
  ScoreSection() {
    Column() {
      if (this.school!.scoreLines.length > 0) {
        ForEach(this.school!.scoreLines, (line: ScoreLine) => {
          Column() {
            Text(line.year + '年录取数据')
              .fontSize(14)
              .fontWeight(FontWeight.Medium)
              .fontColor(AppConfig.textPrimary)
              .width('100%')
              .margin({ bottom: 12 })

            Row() {
              Column() {
                Text('文科一本线')
                  .fontSize(11)
                  .fontColor(AppConfig.textSecondary)
                Text(line.arts_score + '分')
                  .fontSize(16)
                  .fontWeight(FontWeight.Bold)
                  .fontColor(AppConfig.textSecondary)
                  .margin({ top: 4 })
              }
              .alignItems(HorizontalAlign.Center)
              .layoutWeight(1)

              Column() {
                Text('理科一本线')
                  .fontSize(11)
                  .fontColor(AppConfig.textSecondary)
                Text(line.science_score + '分')
                  .fontSize(16)
                  .fontWeight(FontWeight.Bold)
                  .fontColor(AppConfig.textSecondary)
                  .margin({ top: 4 })
              }
              .alignItems(HorizontalAlign.Center)
              .layoutWeight(1)
            }
            .width('100%')

            Divider().margin({ top: 12, bottom: 12 })

            Row() {
              Column() {
                Text('文科录取最低')
                  .fontSize(11)
                  .fontColor(AppConfig.textSecondary)
                Text(line.arts_admit_min + '分')
                  .fontSize(18)
                  .fontWeight(FontWeight.Bold)
                  .fontColor(AppConfig.accentColor)
                  .margin({ top: 4 })
              }
              .alignItems(HorizontalAlign.Center)
              .layoutWeight(1)

              Column() {
                Text('理科录取最低')
                  .fontSize(11)
                  .fontColor(AppConfig.textSecondary)
                Text(line.science_admit_min + '分')
                  .fontSize(18)
                  .fontWeight(FontWeight.Bold)
                  .fontColor(AppConfig.accentColor)
                  .margin({ top: 4 })
              }
              .alignItems(HorizontalAlign.Center)
              .layoutWeight(1)
            }
            .width('100%')

            Text('※ 数据为全国参考线，实际录取分因省份、专业而异')
              .fontSize(11)
              .fontColor(AppConfig.textSecondary)
              .margin({ top: 8 })
              .width('100%')
          }
          .width('100%')
          .padding(16)
          .backgroundColor(AppConfig.cardBg)
          .borderRadius(12)
          .margin({ top: 12 })
        })
      } else {
        Column() {
          Text('暂无历年数据')
            .fontSize(13)
            .fontColor(AppConfig.textSecondary)
            .padding(20)
        }
        .width('100%')
        .backgroundColor(AppConfig.cardBg)
        .borderRadius(12)
        .margin({ top: 12 })
      }
    }
    .width('100%')
  }

  @Builder
  MajorSection() {
    Column() {
      ForEach(this.school!.majorCategories, (cat: MajorCategory) => {
        Column() {
          Row() {
            Text(cat.category)
              .fontSize(14)
              .fontWeight(FontWeight.Medium)
              .fontColor(AppConfig.textPrimary)
            Text(cat.majors.length + ' 个专业')
              .fontSize(12)
              .fontColor(AppConfig.textSecondary)
              .margin({ left: 6 })
          }
          .width('100%')
          .margin({ bottom: 8 })

          Flex({ wrap: FlexWrap.Wrap }) {
            ForEach(cat.majors, (major: string) => {
              Text(major)
                .fontSize(12)
                .fontColor(AppConfig.textSecondary)
                .backgroundColor(AppConfig.bgColor)
                .borderRadius(6)
                .padding({ left: 10, right: 10, top: 4, bottom: 4 })
                .margin({ right: 6, bottom: 6 })
            })
          }
        }
        .width('100%')
        .padding(16)
        .backgroundColor(AppConfig.cardBg)
        .borderRadius(12)
        .margin({ top: 12 })
      })
    }
    .width('100%')
  }

  build() {
    Column() {
      if (this.isLoading) {
        Column() {
          LoadingProgress().width(40).height(40).color(AppConfig.primaryColor)
          Text('加载中...').fontSize(13).fontColor(AppConfig.textSecondary).margin({ top: 8 })
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
      } else if (!this.school) {
        Column() {
          Text('未找到该院校')
            .fontSize(16)
            .fontColor(AppConfig.textSecondary)
          Button('返回')
            .margin({ top: 12 })
            .onClick(() => router.back())
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
      } else {
        // 顶部
        Column() {
          Row() {
            Image($r('sys.media.ohos_ic_public_arrow_left'))
              .width(24)
              .height(24)
              .fillColor('#FFF')
              .onClick(() => router.back())
            Text(this.school.name)
              .fontSize(18)
              .fontWeight(FontWeight.Bold)
              .fontColor('#FFF')
              .layoutWeight(1)
              .margin({ left: 8 })
          }
          .width('100%')
          .padding({ left: 12, right: 12, top: 8, bottom: 8 })

          Scroll() {
            Row() {
              ForEach(this.school.tags, (tag: string) => {
                this.TagBadge(tag)
              })
              Text('全国#' + this.school.rank_national)
                .fontSize(12)
                .fontColor('#FFF')
                .backgroundColor('rgba(255,255,255,0.25)')
                .borderRadius(6)
                .padding({ left: 10, right: 10, top: 4, bottom: 4 })
            }
          }
          .scrollBar(BarState.Off)
          .padding({ left: 12, right: 12, bottom: 12 })
        }
        .width('100%')
        .backgroundColor(AppConfig.primaryColor)

        // 导航栏
        Row() {
          this.SectionTab('院校信息', 'info')
          this.SectionTab('历年分数', 'score')
          this.SectionTab('专业设置', 'major')
        }
        .width('100%')
        .backgroundColor(AppConfig.cardBg)

        // 内容区
        Scroll() {
          Column() {
            if (this.activeSection === 'info') {
              this.InfoSection()
            } else if (this.activeSection === 'score') {
              this.ScoreSection()
            } else if (this.activeSection === 'major') {
              this.MajorSection()
            }
          }
          .padding({ left: 16, right: 16, bottom: 20 })
        }
        .width('100%')
        .layoutWeight(1)
        .edgeEffect(EdgeEffect.Spring)
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor(AppConfig.bgColor)
  }
}
