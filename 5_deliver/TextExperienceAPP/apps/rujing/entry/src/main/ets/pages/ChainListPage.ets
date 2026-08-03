/**
 * 入境 APP · 链列表页
 * 展示某学科下所有知识链，显示生熟进度
 * 古诗文学科：系列剧集和知识链均支持折叠/展开
 */

import { router } from '@kit.ArkUI';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { db } from '../service/DatabaseService';
import { Chain } from '../model/DataModel';

class ChainGroup {
  label: string = ''
  icon: string = ''
  chains: Chain[] = []
  expanded: boolean = false

  constructor(label: string, icon: string, chains: Chain[], expanded: boolean) {
    this.label = label;
    this.icon = icon;
    this.chains = chains;
    this.expanded = expanded;
  }
}

class CategoryBucket {
  label: string = ''
  icon: string = ''
  chains: Chain[] = []

  constructor(label: string, icon: string) {
    this.label = label;
    this.icon = icon;
  }
}

@Entry
@Component
struct ChainListPage {
  @State allChains: Chain[] = [];
  @State seriesChains: Chain[] = [];
  @State knowledgeGroups: ChainGroup[] = [];
  @State subject: string = '';
  @State subjectLabel: string = '';
  @State seriesExpanded: boolean = false;

  aboutToAppear(): void {
    const params: Record<string, Object> = router.getParams() as Record<string, Object>;
    this.subject = (params['subject'] as string) ?? '';
    this.loadChains();
  }

  // 知识链学习顺序映射（按学习逻辑编排：词汇→句法→鉴赏→练习）
  private readonly SORT_ORDER: Record<string, number> = {
    'CHAIN_实词_Top20_01': 1,
    'CHAIN_实词_时间_01': 2,
    'CHAIN_实词_言说_01': 3,
    'CHAIN_实词_官职_01': 4,
    'CHAIN_虚词_之_01': 5,
    'CHAIN_虚词_之_02_消独定后': 6,
    'CHAIN_虚词_以_01': 7,
    'CHAIN_虚词_其_01': 8,
    'CHAIN_虚词_于_01': 9,
    'CHAIN_虚词_而_01': 10,
    'CHAIN_古今异义_高频20_01': 11,
    'CHAIN_通假_高频30_01': 12,
    'CHAIN_断句_对话标志_01': 13,
    'CHAIN_句式_判断句_01': 14,
    'CHAIN_句式_省略句_01': 15,
    'CHAIN_句式_被动_01': 16,
    'CHAIN_倒装_定后宾前_01': 17,
    'CHAIN_活用_使动_01': 18,
    'CHAIN_活用_使动_02': 19,
    'CHAIN_活用_意动_01': 20,
    'CHAIN_活用_名作动_01': 21,
    'CHAIN_意象_五大群_01': 22,
    'CHAIN_情感_三层_01': 23,
    'CHAIN_手法_五种_01': 24,
    'CHAIN_炼字_三步法_01': 25,
    'CHAIN_比较鉴赏_模板_01': 26,
    'CHAIN_情感脉络_三层_01': 27,
    'CHAIN_推断_六陷阱_01': 28,
    'CHAIN_推断_张冠李戴_01': 29,
    'CHAIN_主观题_思路_01': 30,
    'CHAIN_主观题_手法_01': 31,
    'CHAIN_比较鉴赏_方法论_01': 32,
    'CHAIN_翻译_3加1_01': 33,
  };

  async loadChains(): Promise<void> {
    switch (this.subject) {
      case '历史': this.subjectLabel = '历史'; break;
      case '地理': this.subjectLabel = '地理'; break;
      case '政治': this.subjectLabel = '政治'; break;
      case '古诗文': this.subjectLabel = '古诗文'; break;
      case '书法': this.subjectLabel = '书法'; break;
      default: this.subjectLabel = this.subject;
    }

    this.allChains = await db.getChainsBySubject(this.subject);

    // 诊断：加载后立即打印链列表到 HiLog
    const msg = '[ChainList] subject=' + this.subject + ' total=' + this.allChains.length;
    hilog.info(0x0000, 'ChainListPage', '%{public}s', msg);
    for (let i = 0; i < this.allChains.length; i++) {
      const c = this.allChains[i];
      hilog.info(0x0000, 'ChainListPage', '  [%{public}d] id=%{public}s subject=%{public}s',
        i.toString(), c.chain_id, c.subject);
    }

    if (this.subject === '古诗文') {
      const series: Chain[] = [];
      const remaining: Chain[] = [];

      for (const c of this.allChains) {
        if (c.chain_id.startsWith('GAOKAO_EP')) {
          series.push(c);
        } else {
          remaining.push(c);
        }
      }

      series.sort((a, b) => {
        const na = parseInt(a.chain_id.replace('GAOKAO_EP', ''));
        const nb = parseInt(b.chain_id.replace('GAOKAO_EP', ''));
        return na - nb;
      });

      remaining.sort((a, b) => {
        const oa = this.SORT_ORDER[a.chain_id] ?? 9999;
        const ob = this.SORT_ORDER[b.chain_id] ?? 9999;
        if (oa !== ob) return oa - ob;
        return a.title.localeCompare(b.title, 'zh-CN');
      });

      this.seriesChains = series;
      this.knowledgeGroups = this.categorizeKnowledgeChains(remaining);
    } else if (this.subject === '书法' || this.subject === '地理' || this.subject === '政治') {
      // 书法/地理/政治链：按显示标题的数字前缀排序（1_/2_/.../16_）
      // getCalligraphyDisplayTitle / getGeographyDisplayTitle / getPoliticsDisplayTitle 已注入序号
      this.allChains.sort((a, b) => {
        const na = parseInt(a.title);
        const nb = parseInt(b.title);
        if (!isNaN(na) && !isNaN(nb)) {
          return na - nb;
        }
        return a.title.localeCompare(b.title, 'zh-CN');
      });
    }
  }

  // 诊断：生成链前缀分布摘要
  private getSeriesSummary(): string {
    const summary: Record<string, number> = {};
    for (const c of this.allChains) {
      // 取 chain_id 前8字符作为系列标识
      const prefix = c.chain_id.length >= 8 ? c.chain_id.substring(0, 8) : c.chain_id;
      summary[prefix] = (summary[prefix] ?? 0) + 1;
    }
    const parts: string[] = [];
    for (const k of Object.keys(summary)) {
      parts.push(k + 'x' + summary[k]);
    }
    return parts.join(' | ');
  }

  categorizeKnowledgeChains(chains: Chain[]): ChainGroup[] {
    // 按学习场景重组为6大类，避免词法细分导致的碎片化
    const buckets: CategoryBucket[] = [
      new CategoryBucket('文言基础', '📜'),    // 虚词/实词/古今异义/通假
      new CategoryBucket('句法进阶', '📐'),    // 句式/活用/倒装
      new CategoryBucket('古诗专项', '🎭'),    // 意象/情感/手法/炼字/比较
      new CategoryBucket('文意推断', '🔍'),    // 推断陷阱
      new CategoryBucket('主观题', '✍️'),      // 主观题技法
      new CategoryBucket('翻译技法', '🔄'),    // 翻译
    ];
    const otherBucket = new CategoryBucket('其他', '📂');
    buckets.push(otherBucket);

    for (const chain of chains) {
      const id = chain.chain_id;
      let placed = false;

      // 文言基础：实词/虚词/古今/通假
      if (id.includes('实词') || id.includes('虚词') || id.includes('古今') || id.includes('通假')) {
        buckets[0].chains.push(chain);
        placed = true;
      }
      // 句法进阶：句式/活用/倒装
      else if (id.includes('句式') || id.includes('活用') || id.includes('倒装')) {
        buckets[1].chains.push(chain);
        placed = true;
      }
      // 古诗专项：意象/情感/手法/炼字/比较鉴赏
      else if (id.includes('意象') || id.includes('情感') || id.includes('手法') || id.includes('炼字') || id.includes('比较')) {
        buckets[2].chains.push(chain);
        placed = true;
      }
      // 文意推断
      else if (id.includes('推断') || id.includes('六陷阱') || id.includes('张冠李戴')) {
        buckets[3].chains.push(chain);
        placed = true;
      }
      // 主观题
      else if (id.includes('主观题')) {
        buckets[4].chains.push(chain);
        placed = true;
      }
      // 翻译
      else if (id.includes('翻译')) {
        buckets[5].chains.push(chain);
        placed = true;
      }

      if (!placed) {
        otherBucket.chains.push(chain);
      }
    }

    const groups: ChainGroup[] = [];
    for (const b of buckets) {
      if (b.chains.length > 0) {
        b.chains.sort((a, b) => a.title.localeCompare(b.title, 'zh-CN'));
        groups.push(new ChainGroup(b.label, b.icon, b.chains, false));
      }
    }

    return groups;
  }

  build() {
    Column() {
      // 顶栏
      Row() {
        Text('← 返回首页')
          .fontSize(15).fontColor('#4a6cf7')
          .onClick(() => router.pushUrl({ url: 'pages/Index' }))
        Blank()
        Text(this.subjectLabel)
          .fontSize(18).fontWeight(600).fontColor('#1a1a1a')
      }
      .width('100%').padding({ left: 16, right: 16, top: 16, bottom: 12 })

      if (this.allChains.length === 0) {
        Column({ space: 12 }) {
          Text('📚').fontSize(40)
          Text('该学科暂无知识链').fontSize(14).fontColor('#888')
          Text('请先导入卡片包').fontSize(12).fontColor('#aaa')
        }
        .width('100%').layoutWeight(1).justifyContent(FlexAlign.Center)
      } else if (this.subject === '古诗文') {
        Scroll() {
          Column({ space: 12 }) {
            // ── 系列剧集（可折叠）─────────────────────
            this.seriesSection()

            // ── 知识链分类（可折叠）──────────────────
            ForEach(this.knowledgeGroups, (group: ChainGroup) => {
              this.groupSection(group)
            })
          }
          .padding({ left: 16, right: 16, bottom: 20 })
        }
        .layoutWeight(1).scrollBar(BarState.Off)
      } else {
        // 其他学科：普通列表（含诊断：显示链数量）
        Column() {
          Text('共 ' + this.allChains.length + ' 条知识链')
            .fontSize(12).fontColor('#888').margin({ bottom: 8 })
          // 诊断：列出各 chain_id 前缀的数量
          Text(this.getSeriesSummary())
            .fontSize(11).fontColor('#bbb').margin({ bottom: 6 })
          List({ space: 8 }) {
            ForEach(this.allChains, (chain: Chain) => {
              ListItem() {
                this.chainItem(chain, '')
              }
            })
          }
          .layoutWeight(1).padding({ left: 16, right: 16 }).scrollBar(BarState.Off)
        }
      }
    }
    .width('100%').height('100%').backgroundColor('#F5F5F5')
  }

  // ── 系列剧集折叠区 ──────────────────────────────
  @Builder
  seriesSection() {
    Column() {
      // 头部（始终可见，点击折叠/展开）
      Row() {
        Text('🎬').fontSize(18)
        Text('系列剧集').fontSize(15).fontWeight(600).fontColor('#333').margin({ left: 8 })
        Text(this.seriesChains.length + ' 集').fontSize(11).fontColor('#e67e22')
          .backgroundColor('#fff3e0').borderRadius(8)
          .padding({ left: 6, right: 6, top: 2, bottom: 2 }).margin({ left: 8 })
        Blank()
        Text(this.seriesExpanded ? '▲' : '▶')
          .fontSize(12).fontColor('#999').margin({ left: 8 })
      }
      .width('100%')
      .padding({ left: 16, right: 16, top: 14, bottom: 14 })
      .backgroundColor(Color.White)
      .borderRadius(12)
      .onClick(() => { this.seriesExpanded = !this.seriesExpanded; })

      // 内容（展开时显示）
      if (this.seriesExpanded) {
        Column({ space: 8 }) {
          ForEach(this.seriesChains, (chain: Chain) => {
            ListItem() {
              this.chainItem(chain, '#e67e22')
            }
          })
        }
        .width('100%')
        .padding({ left: 16, right: 16, top: 8, bottom: 4 })
      }
    }
    .width('100%')
    .backgroundColor(Color.White)
    .borderRadius(12)
  }

  // ── 知识链分类折叠区 ───────────────────────────
  @Builder
  groupSection(group: ChainGroup) {
    Column() {
      // 头部
      Row() {
        Text(group.icon).fontSize(18)
        Text(group.label).fontSize(15).fontWeight(600).fontColor('#333').margin({ left: 8 })
        Text(group.chains.length + ' 条').fontSize(11).fontColor('#888')
          .backgroundColor('#f0f0f0').borderRadius(8)
          .padding({ left: 6, right: 6, top: 2, bottom: 2 }).margin({ left: 8 })
        Blank()
        Text(group.expanded ? '▲' : '▶')
          .fontSize(12).fontColor('#999').margin({ left: 8 })
      }
      .width('100%')
      .padding({ left: 16, right: 16, top: 14, bottom: 14 })
      .backgroundColor(Color.White)
      .borderRadius(12)
      .onClick(() => {
        const idx = this.knowledgeGroups.findIndex(g => g.label === group.label);
        if (idx >= 0) {
          const current = this.knowledgeGroups[idx];
          const next = new ChainGroup(
            current.label, current.icon, current.chains, !current.expanded
          );
          const updated = this.knowledgeGroups.slice();
          updated[idx] = next;
          this.knowledgeGroups = updated;
        }
      })

      // 内容（展开时显示）
      if (group.expanded) {
        Column({ space: 8 }) {
          ForEach(group.chains, (chain: Chain) => {
            ListItem() {
              this.chainItem(chain, '#8B4513')
            }
          })
        }
        .width('100%')
        .padding({ left: 16, right: 16, top: 8, bottom: 4 })
      }
    }
    .width('100%')
    .backgroundColor(Color.White)
    .borderRadius(12)
  }

  // ── 链条目 ─────────────────────────────────────
  @Builder
  chainItem(chain: Chain, accentColor: string) {
    Row() {
      Column() {
        Text(chain.title)
          .fontSize(14).fontWeight(500).fontColor('#1a1a1a')
          .maxLines(1).textOverflow({ overflow: TextOverflow.Ellipsis })
        Row({ space: 8 }) {
          Text(chain.card_count + ' 张')
            .fontSize(11).fontColor('#999')
          Text(chain.raw_count.toString() + ' 生 · ' + chain.cooked_count.toString() + ' 熟')
            .fontSize(11).fontColor(chain.raw_count > 0 ? '#e67e22' : '#5B8C5A')
          // DEBUG：显示 chain_id 和 subject
          Text('[' + chain.chain_id + ']')
            .fontSize(10).fontColor('#bbb')
        }
        .margin({ top: 4 })
        if (chain.card_count > 0) {
          Progress({
            value: chain.cooked_count / chain.card_count * 100,
            total: 100,
            type: ProgressType.Linear
          })
            .color('#5B8C5A').width('55%').height(3)
            .style({ strokeWidth: 3 }).margin({ top: 5 })
        }
      }
      .alignItems(HorizontalAlign.Start).layoutWeight(1)
      Image($r('app.media.startIcon')).width(14).height(14).fillColor('#ccc')
    }
    .width('100%')
    .padding(14)
    .backgroundColor('#fafafa')
    .borderRadius(8)
    .onClick(() => {
      router.pushUrl({
        url: 'pages/ChainReaderPage',
        params: { chain_id: chain.chain_id }
      });
    })
  }
}
