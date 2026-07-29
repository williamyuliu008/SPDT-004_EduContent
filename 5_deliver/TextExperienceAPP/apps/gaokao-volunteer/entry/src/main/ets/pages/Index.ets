/**
 * gaokao-volunteer · 首页
 * 搜索 + 分类入口 + 院校列表
 */
import { router, promptAction } from '@kit.ArkUI';
import { AppConfig } from '../app.config';
import { School } from '../model/SchoolModel';
import { schoolService } from '../service/SchoolService';

interface FilterCondition {
  province: string;
  type: string;
  tag: string;
  keyword: string;
}

const QUICK_TABS: string[] = ['全部', '985', '211', '双一流', '公办', '师范', '理工', '医药', '文科'];

@Entry
@Component
struct Index {
  @State schools: School[] = [];
  @State filteredSchools: School[] = [];
  @State keyword: string = '';
  @State filter: FilterCondition = { province: '', type: '', tag: '', keyword: '' };
  @State activeTab: string = '全部';
  @State isLoading: boolean = true;
  @State showFilter: boolean = false;

  private provinces: string[] = [];
  private types: string[] = [];

  aboutToAppear(): void {
    this.provinces = ['全部'];
    const provs = schoolService.getProvinces();
    for (let i = 0; i < provs.length; i++) {
      this.provinces.push(provs[i]);
    }
    this.types = ['全部'];
    const tps = schoolService.getTypes();
    for (let i = 0; i < tps.length; i++) {
      this.types.push(tps[i]);
    }
    this.loadData();
  }

  async loadData(): Promise<void> {
    this.isLoading = true;
    try {
      const context = getContext(this);
      await schoolService.loadSchools(context);
      this.schools = schoolService.sortByRank();
      this.applyFilters();
    } catch (e) {
      promptAction.showToast({ message: '数据加载失败' });
    } finally {
      this.isLoading = false;
    }
  }

  applyFilters(): void {
    let result: School[] = this.schools;
    if (this.keyword && this.keyword.trim() !== '') {
      result = schoolService.searchSchools(this.keyword.trim());
    }
    if (this.filter.province && this.filter.province !== '全部') {
      result = result.filter((s: School) => s.province === this.filter.province);
    }
    if (this.filter.type && this.filter.type !== '全部') {
      result = result.filter((s: School) => s.type === this.filter.type);
    }
    if (this.filter.tag && this.filter.tag !== '全部') {
      result = result.filter((s: School) => s.tags.includes(this.filter.tag));
    }
    this.filteredSchools = result;
  }

  onKeywordChange(val: string): void {
    this.keyword = val;
    this.applyFilters();
  }

  applyFilter(f: Partial<FilterCondition>): void {
    this.filter = {
      province: f.province !== undefined ? f.province : this.filter.province,
      type: f.type !== undefined ? f.type : this.filter.type,
      tag: f.tag !== undefined ? f.tag : this.filter.tag,
      keyword: f.keyword !== undefined ? f.keyword : this.filter.keyword,
    };
    this.applyFilters();
  }

  navigateToDetail(school: School): void {
    router.pushUrl({ url: 'pages/SchoolDetailPage', params: { schoolId: school.id } });
  }

  onQuickTabClick(tab: string): void {
    if (tab === '全部') {
      this.activeTab = '全部';
      this.filter = { province: '', type: '', tag: '', keyword: this.filter.keyword };
    } else if (['985', '211', '双一流'].indexOf(tab) >= 0) {
      this.activeTab = tab;
      this.filter = { province: this.filter.province, type: '', tag: tab, keyword: this.filter.keyword };
    } else {
      this.activeTab = tab;
      this.filter = { province: this.filter.province, type: tab, tag: '', keyword: this.filter.keyword };
    }
    this.applyFilters();
  }

  onProvinceClick(province: string): void {
    this.filter = { province: province, type: this.filter.type, tag: this.filter.tag, keyword: this.filter.keyword };
    this.applyFilters();
  }

  onTypeClick(tp: string): void {
    this.filter = { province: this.filter.province, type: tp, tag: this.filter.tag, keyword: this.filter.keyword };
    this.applyFilters();
  }

  @Builder
  SchoolCard(school: School) {
    Row() {
      Column() {
        Text(school.name)
          .fontSize(16)
          .fontWeight(FontWeight.Medium)
          .fontColor(AppConfig.textPrimary)
          .maxLines(1)
          .textOverflow({ overflow: TextOverflow.Ellipsis })

        Text(school.province + ' · ' + school.city + ' · ' + school.type)
          .fontSize(12)
          .fontColor(AppConfig.textSecondary)
          .margin({ top: 4 })

        Row() {
          ForEach(school.tags, (tag: string) => {
            Text(tag)
              .fontSize(10)
              .fontColor(tag === '985' ? '#1A73E8' : tag === '211' ? '#34A853' : '#F29900')
              .backgroundColor(tag === '985' ? '#E8F0FE' : tag === '211' ? '#E6F4EA' : '#FEF7E0')
              .borderRadius(4)
              .padding({ left: 6, right: 6, top: 2, bottom: 2 })
              .margin({ right: 4 })
          })
        }
        .margin({ top: 6 })

        Row() {
          Text('全国#' + school.rank_national)
            .fontSize(11)
            .fontColor(AppConfig.textSecondary)
          Text(' | ')
            .fontSize(11)
            .fontColor(AppConfig.borderColor)
          Text('录取参考: ' + school.minScore + '分+')
            .fontSize(11)
            .fontColor(AppConfig.primaryColor)
        }
        .margin({ top: 4 })
      }
      .alignItems(HorizontalAlign.Start)
      .layoutWeight(1)

      Image($r('sys.media.ohos_ic_public_arrow_right'))
        .width(16)
        .height(16)
        .fillColor(AppConfig.borderColor)
    }
    .width('100%')
    .padding(16)
    .backgroundColor(AppConfig.cardBg)
    .borderRadius(12)
    .shadow({ radius: 4, color: '#08000000', offsetX: 0, offsetY: 2 })
    .onClick(() => this.navigateToDetail(school))
    .margin({ bottom: 10 })
  }

  @Builder
  FilterPanel() {
    Column() {
      Column() {
        Text('筛选条件')
          .fontSize(16)
          .fontWeight(FontWeight.Medium)
          .fontColor(AppConfig.textPrimary)
          .width('100%')
          .padding({ bottom: 12 })

        Text('省份')
          .fontSize(13)
          .fontColor(AppConfig.textSecondary)
          .width('100%')
          .margin({ top: 8 })

        Scroll() {
          Row() {
            ForEach(this.provinces, (p: string) => {
              Text(p)
                .fontSize(13)
                .fontColor(this.filter.province === p ? '#FFF' : AppConfig.textPrimary)
                .backgroundColor(this.filter.province === p ? AppConfig.primaryColor : AppConfig.bgColor)
                .borderRadius(8)
                .padding({ left: 12, right: 12, top: 6, bottom: 6 })
                .margin({ right: 8 })
                .onClick(() => this.onProvinceClick(p))
            })
          }
        }
        .scrollBar(BarState.Off)
        .width('100%')

        Text('院校类型')
          .fontSize(13)
          .fontColor(AppConfig.textSecondary)
          .width('100%')
          .margin({ top: 12 })

        Row() {
          ForEach(this.types, (t: string) => {
            Text(t)
              .fontSize(13)
              .fontColor(this.filter.type === t ? '#FFF' : AppConfig.textPrimary)
              .backgroundColor(this.filter.type === t ? AppConfig.accentColor : AppConfig.bgColor)
              .borderRadius(8)
              .padding({ left: 12, right: 12, top: 6, bottom: 6 })
              .margin({ right: 8 })
              .onClick(() => this.onTypeClick(t))
          })
        }

        Row() {
          Button('重置')
            .fontSize(14)
            .fontColor(AppConfig.textSecondary)
            .backgroundColor(AppConfig.bgColor)
            .borderRadius(8)
            .height(36)
            .onClick(() => {
              this.filter = { province: '', type: '', tag: '', keyword: '' };
              this.keyword = '';
              this.applyFilters();
            })
          Button('确定')
            .fontSize(14)
            .fontColor('#FFF')
            .backgroundColor(AppConfig.primaryColor)
            .borderRadius(8)
            .height(36)
            .margin({ left: 12 })
            .onClick(() => {
              this.applyFilters();
              this.showFilter = false;
            })
        }
        .width('100%')
        .margin({ top: 20 })
        .justifyContent(FlexAlign.End)
      }
      .padding(16)
      .backgroundColor(AppConfig.cardBg)
      .borderRadius({ topLeft: 16, topRight: 16 })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#80000000')
    .justifyContent(FlexAlign.End)
    .onClick((e: ClickEvent) => {
      this.showFilter = false;
    })
  }

  build() {
    Stack({ alignContent: Alignment.TopStart }) {
      Column() {
        // 顶部标题
        Row() {
          Column() {
            Text(AppConfig.appName)
              .fontSize(22)
              .fontWeight(FontWeight.Bold)
              .fontColor(AppConfig.textPrimary)
            Text(AppConfig.shortDesc)
              .fontSize(12)
              .fontColor(AppConfig.textSecondary)
              .margin({ top: 2 })
          }
          .alignItems(HorizontalAlign.Start)
          .layoutWeight(1)

          Text('院校库')
            .fontSize(13)
            .fontColor(AppConfig.textSecondary)
        }
        .width('100%')
        .padding({ left: 20, right: 20, top: 16, bottom: 12 })

        // 搜索栏
        Row() {
          Search({ placeholder: '搜索院校名称/省份/类型...', value: this.keyword })
            .width('100%')
            .height(40)
            .borderRadius(20)
            .backgroundColor(AppConfig.bgColor)
            .placeholderColor(AppConfig.textSecondary)
            .textFont({ size: 14 })
            .onChange((val: string) => this.onKeywordChange(val))

          Text('⊞')
            .fontSize(22)
            .fontColor(AppConfig.textSecondary)
            .margin({ left: 10 })
            .onClick(() => { this.showFilter = true; })
        }
        .width('100%')
        .padding({ left: 20, right: 20, bottom: 12 })

        // 快捷分类
        Column() {
          Text('按标签快速筛选')
            .fontSize(13)
            .fontColor(AppConfig.textSecondary)
            .width('100%')
            .padding({ left: 20, bottom: 8 })

          Scroll() {
            Row() {
              ForEach(QUICK_TABS, (tab: string) => {
                Text(tab)
                  .fontSize(13)
                  .fontColor(this.activeTab === tab ? '#FFF' : AppConfig.textPrimary)
                  .backgroundColor(this.activeTab === tab ? AppConfig.primaryColor : AppConfig.bgColor)
                  .borderRadius(20)
                  .padding({ left: 14, right: 14, top: 6, bottom: 6 })
                  .margin({ right: 8 })
                  .onClick(() => this.onQuickTabClick(tab))
              })
            }
          }
          .scrollBar(BarState.Off)
          .padding({ left: 20, right: 20 })
        }
        .width('100%')

        // 统计行
        Row() {
          Text('共 ' + this.filteredSchools.length + ' 所院校')
            .fontSize(13)
            .fontColor(AppConfig.textSecondary)
        }
        .width('100%')
        .padding({ left: 20, top: 8, bottom: 4 })

        // 院校列表
        if (this.isLoading) {
          Column() {
            LoadingProgress()
              .width(40)
              .height(40)
              .color(AppConfig.primaryColor)
            Text('加载中...')
              .fontSize(13)
              .fontColor(AppConfig.textSecondary)
              .margin({ top: 8 })
          }
          .width('100%')
          .height('100%')
          .justifyContent(FlexAlign.Center)
        } else {
          List() {
            ForEach(this.filteredSchools, (school: School) => {
              ListItem() {
                this.SchoolCard(school)
              }
            })
          }
          .width('100%')
          .layoutWeight(1)
          .padding({ left: 16, right: 16, top: 8 })
          .divider({ strokeWidth: 0, color: '#00000000' })
          .edgeEffect(EdgeEffect.Spring)
        }
      }
      .width('100%')
      .height('100%')
      .backgroundColor(AppConfig.bgColor)

      // 筛选面板
      if (this.showFilter) {
        this.FilterPanel()
      }
    }
    .width('100%')
    .height('100%')
  }
}
