/**
 * 入境 APP · 导入页
 * 卡片包一键导入 + 视频包导入（IF-B 协议）
 *
 * v5 修复（2026-07-30）：
 *   - 视频导入：直接读独立 ep 文件（ep01~ep08_metadata.json），
 *     不依赖有错的 墨骨山河全集_metadata.json 合并文件
 *   - 每个独立 ep 文件的 chain_id 均与 mogustory_cards.json 完全对应
 *   - migrateSubjectOwnership 新增无条件迁移步骤（确保墨骨山河%链始终为书法）
 *   - DEBUG 输出升级：打印导入后所有书法链 + subject，供 HiLog 诊断
 */

import { router } from '@kit.ArkUI';
import { promptAction } from '@kit.ArkUI';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { importCardPackage, importChainMeta, importVideoPackage, getVideoMeta, getVideoDir, getCalligraphyDisplayTitle } from '../service/ImportService';
import { db } from '../service/DatabaseService';
import { Subject } from '../model/DataModel';
import { fileIo } from '@kit.CoreFileKit';
import { util } from '@kit.ArkTS';
import { BusinessError } from '@kit.BasicServicesKit';

@Entry
@Component
struct ImportPage {
  // 历史 v3 卡片包（rujing_cards.json）
  @State importResult: string = '';
  @State isImporting: boolean = false;
  @State importedCards: number = 0;
  @State importedChains: number = 0;
  @State importedVideos: number = 0;  // legacy: 被旧 doCardImport/doVideoImport 引用
  // 高考古诗文通关（gaokao v1）
  @State gaokaoImportResult: string = '';
  @State isGaokaoImporting: boolean = false;
  @State gaokaoCards: number = 0;
  @State gaokaoChains: number = 0;
  // 书法·墨骨山河（统一入口：卡包+叙事+视频元数据）
  @State calligraphyImportResult: string = '';
  @State isCalligraphyImporting: boolean = false;
  @State calligraphyCards: number = 0;
  @State calligraphyChains: number = 0;
  @State calligraphyVideos: number = 0;
  @State calligraphyVideoDetail: string = '';  // 每集导入详情
  // 地理山河系列
  @State geoImportResult: string = '';
  @State isGeoImporting: boolean = false;
  @State geoCards: number = 0;
  @State geoChains: number = 0;

  // 思想政治体系
  @State politicsImportResult: string = '';
  @State isPoliticsImporting: boolean = false;
  @State politicsCards: number = 0;
  @State politicsChains: number = 0;

  build() {
    Column() {
      Row() {
        Text('← 返回首页')
          .fontSize(15).fontColor('#4a6cf7')
          .onClick(() => router.pushUrl({ url: 'pages/Index' }))
        Blank()
        Text('导入数据')
          .fontSize(18).fontWeight(600).fontColor('#1a1a1a')
      }
      .width('100%').padding({ left: 16, right: 16, top: 16, bottom: 12 })

      Scroll() {
        Column({ space: 16 }) {
          // ── 书法·墨骨山河（统一入口：卡片+叙事+视频元数据）───────────
          Column() {
            Row() {
              Text('书法·墨骨山河')
                .fontSize(16).fontWeight(600).fontColor('#1a1a1a')
              Text(' 书法 ')
                .fontSize(11).fontColor('#8B4513')
                .backgroundColor('#fff5f0')
                .borderRadius(8).padding({ left: 6, right: 6, top: 2, bottom: 2 })
                .margin({ left: 8 })
            }.width('100%').alignItems(VerticalAlign.Center)

            Text('李斯 → 王羲之 → 苏轼 → 孙过庭 → 张旭/怀素 → 颜真卿 → 阮元 → 许慎（ep01~ep08）')
              .fontSize(11).fontColor('#888').margin({ top: 4 })
            Text('16张墨骨山河卡 + 国美书法校考卡 + 8集视频（独立元数据）')
              .fontSize(10).fontColor('#8B4513').margin({ top: 2 })

            if (this.calligraphyImportResult.length > 0) {
              Column() {
                Text(this.calligraphyImportResult)
                  .fontSize(13).fontColor(this.calligraphyImportResult.startsWith('OK') ? '#8B4513' : '#c0392b')
                  .textAlign(TextAlign.Start).width('100%')
                  .lineHeight(20)
                if (this.calligraphyVideoDetail.length > 0) {
                  Text('视频详情: ' + this.calligraphyVideoDetail)
                    .fontSize(11).fontColor('#c0392b')
                    .textAlign(TextAlign.Start).width('100%')
                    .margin({ top: 4 })
                }
              }
              .width('100%').padding(12)
              .backgroundColor('#fffbf0').borderRadius(10)
              .margin({ top: 10 })
            }

            Button('一键导入书法全部')
              .fontSize(15).backgroundColor('#8B4513').borderRadius(24)
              .width('90%').height(48).margin({ top: 12 })
              .onClick(() => this.doCalligraphyAllImport())

            if (this.isCalligraphyImporting) {
              LoadingProgress().width(36).height(36).margin({ top: 8 })
            }
          }
          .width('100%').padding(20)
          .backgroundColor(Color.White).borderRadius(14)

          Divider().color('#f0f0f0').margin({ top: 4, bottom: 4 })

          // ── 高考古诗文通关·完整版（gaokao v1）────────────────
          Column() {
            Row() {
              Text('高考古诗文通关·完整版')
                .fontSize(16).fontWeight(600).fontColor('#1a1a1a')
              Text(' 古诗文 ')
                .fontSize(11).fontColor('#9b59b6')
                .backgroundColor('#f5f0ff')
                .borderRadius(8).padding({ left: 6, right: 6, top: 2, bottom: 2 })
                .margin({ left: 8 })
            }.width('100%').alignItems(VerticalAlign.Center)

            Text('41 条知识链 / 106 张文言文卡 / 18 张诗词卡 / 12 集')
              .fontSize(12).fontColor('#888').margin({ top: 4 })
            Text('含：判断句/使动意动/虚词系统/通假古今异义/被动句式/翻译采分点/推断六陷阱/意象五大群/比较鉴赏')
              .fontSize(11).fontColor('#9b59b6').margin({ top: 2 })

            Column() {
              Text('一键导入全部')
                .fontSize(16).fontWeight(600).fontColor('#1a1a1a')
                .alignSelf(ItemAlign.Start).margin({ bottom: 8 })
              Button('导入高考古诗文')
                .fontSize(14).backgroundColor('#9b59b6').borderRadius(24)
                .width('80%').height(44)
                .onClick(() => this.doGaokaoImport())
            }
            .width('100%').padding(16)
            .backgroundColor('#faf5ff').borderRadius(10)
            .margin({ top: 12 })
          }
          .width('100%').padding(20)
          .backgroundColor(Color.White).borderRadius(14)

          if (this.gaokaoImportResult.length > 0) {
            Column() {
              Text(this.gaokaoImportResult)
                .fontSize(14).fontColor(this.gaokaoImportResult.startsWith('OK') ? '#9b59b6' : '#c0392b')
                .textAlign(TextAlign.Start).width('100%')
            }
            .width('100%').padding(16)
            .backgroundColor(this.gaokaoImportResult.startsWith('OK') ? '#faf5ff' : '#fff5f5')
            .borderRadius(10)
          }

          if (this.isGaokaoImporting) {
            LoadingProgress().width(36).height(36)
          }

          Divider().color('#f0f0f0').margin({ top: 4, bottom: 4 })

          // ── 历史 v3 卡片包区块 ──────────────────────────────
          Column() {
            Row() {
              Text('历史·近代史通关系列')
                .fontSize(16).fontWeight(600).fontColor('#1a1a1a')
              Text(' 历史 ')
                .fontSize(11).fontColor('#5B8C5A')
                .backgroundColor('#f0fdf4')
                .borderRadius(8).padding({ left: 6, right: 6, top: 2, bottom: 2 })
                .margin({ left: 8 })
            }.width('100%').alignItems(VerticalAlign.Center)

            Text('129 张卡片 / 16 条知识链：鸦片战争 → 太平天国 → 洋务运动 → 甲午战争 → 戊戌变法')
              .fontSize(12).fontColor('#888').margin({ top: 4 })

            Column() {
              Text('一键导入')
                .fontSize(16).fontWeight(600).fontColor('#1a1a1a')
                .alignSelf(ItemAlign.Start).margin({ bottom: 8 })
              Button('开始导入')
                .fontSize(14).backgroundColor('#5B8C5A').borderRadius(24)
                .width('80%').height(44)
                .onClick(() => this.doCardImport())
            }
            .width('100%').padding(16)
            .backgroundColor('#f0fdf4').borderRadius(10)
            .margin({ top: 12 })
          }
          .width('100%').padding(20)
          .backgroundColor(Color.White).borderRadius(14)

          if (this.importResult.length > 0) {
            Column() {
              Text(this.importResult)
                .fontSize(14)
                .fontColor(this.importResult.startsWith('OK') ? '#5B8C5A' : '#c0392b')
                .textAlign(TextAlign.Start).width('100%')
            }
            .width('100%').padding(16)
            .backgroundColor(this.importResult.startsWith('OK') ? '#f0fdf4' : '#fff5f5')
            .borderRadius(10)
          }

          if (this.isImporting) {
            LoadingProgress().width(36).height(36)
          }

          if (this.importedCards > 0 || this.calligraphyCards > 0) {
            Button('返回首页')
              .backgroundColor('#5B8C5A').borderRadius(24)
              .width('60%').margin({ top: 8 })
              .onClick(() => {
                router.clear();
                router.pushUrl({ url: 'pages/Index' });
              })
          }

          Divider().color('#f0f0f0').margin({ top: 4, bottom: 4 })

          // ── 地理山河系列 · 自然+人文+区域（2026-08-01）────────────
          Column() {
            Row() {
              Text('地理山河系列')
                .fontSize(16).fontWeight(600).fontColor('#1a1a1a')
              Text(' 地理 ')
                .fontSize(11).fontColor('#5B8C5A')
                .backgroundColor('#f0fdf4')
                .borderRadius(8).padding({ left: 6, right: 6, top: 2, bottom: 2 })
                .margin({ left: 8 })
            }.width('100%').alignItems(VerticalAlign.Center)

            Text('自然地理要素链（8条山河）+ 人文地理链（4条）+ 区域综合链（4条）')
              .fontSize(11).fontColor('#888').margin({ top: 4 })
            Text('黄河·长江·淮河·珠江·松花江·塔里木·青藏·天山 | 人口·产业·农业·可持续 | 南北西北青藏')
              .fontSize(10).fontColor('#5B8C5A').margin({ top: 2 })

            if (this.geoImportResult.length > 0) {
              Column() {
                Text(this.geoImportResult)
                  .fontSize(13).fontColor(this.geoImportResult.startsWith('OK') ? '#5B8C5A' : '#c0392b')
                  .textAlign(TextAlign.Start).width('100%')
              }
              .width('100%').padding(12)
              .backgroundColor(this.geoImportResult.startsWith('OK') ? '#f0fdf4' : '#fff5f5')
              .borderRadius(10)
              .margin({ top: 10 })
            }

            Button('一键导入地理山河')
              .fontSize(15).backgroundColor('#5B8C5A').borderRadius(24)
              .width('90%').height(48).margin({ top: 12 })
              .onClick(() => this.doGeographyImport())

            if (this.isGeoImporting) {
              LoadingProgress().width(36).height(36).margin({ top: 8 })
            }
          }
          .width('100%').padding(20)
          .backgroundColor(Color.White).borderRadius(14)

          // 思想政治体系
          Column() {
            Row() {
              Text('思想政治体系')
                .fontSize(16).fontWeight(600).fontColor('#1a1a1a')
              Text(' 新 ')
                .fontSize(11).fontColor('#4a6cf7')
                .backgroundColor('#eef2ff')
                .borderRadius(8).padding({ left: 6, right: 6, top: 2, bottom: 2 })
                .margin({ left: 8 })
            }.width('100%').alignItems(VerticalAlign.Center)

            Text('经济/政治/哲学/法律/时事，16条知识链，32张卡片')
              .fontSize(11).fontColor('#888').margin({ top: 4 })
            Text('商品与货币 · 国家与公民 · 唯物论基础 · 公民权利义务 · 时政热点')
              .fontSize(10).fontColor('#888').margin({ top: 2 })

            if (this.politicsImportResult.length > 0) {
              Column() {
                Text(this.politicsImportResult)
                  .fontSize(13).fontColor(this.politicsImportResult.startsWith('OK') ? '#4a6cf7' : '#c0392b')
                  .textAlign(TextAlign.Start).width('100%')
              }
              .width('100%').padding(12)
              .backgroundColor(this.politicsImportResult.startsWith('OK') ? '#eef2ff' : '#fff5f5')
              .borderRadius(10)
              .margin({ top: 10 })
            }

            Button('一键导入思想政治')
              .fontSize(15).backgroundColor('#4a6cf7').borderRadius(24)
              .width('90%').height(48).margin({ top: 12 })
              .onClick(() => this.doPoliticsImport())

            if (this.isPoliticsImporting) {
              LoadingProgress().width(36).height(36).margin({ top: 8 })
            }
          }
          .width('100%').padding(20)
          .backgroundColor(Color.White).borderRadius(14)
        }
        .padding(20)
      }
      .layoutWeight(1).scrollBar(BarState.Off)
    }
    .width('100%').height('100%')
    .backgroundColor('#F5F5F5')
  }

  // ── 视频包导入（IF-B v2，内置 rawfile 模式）────────────────────
  // 流程：读 rawfile metadata.json → 复制 MP4 到沙箱 filesDir → 更新 video_file 路径 → 持久化
  // 资源文件：entry/src/main/resources/rawfile/ep01_metadata.json + ep01_pipeline.mp4

  // ── 高考古诗文通关导入（gaokao v1）────────────────
  async doGaokaoImport(): Promise<void> {
    this.isGaokaoImporting = true;
    this.gaokaoImportResult = '';
    const ctx = getContext(this);
    const rm = ctx.resourceManager;
    const decoder: util.TextDecoder = util.TextDecoder.create('utf-8', { ignoreBOM: true });

    try {
      // Step 1：导入文言文卡包（gaokao_guwen_cards.json）
      let guwenCards = 0;
      let guwenChains = 0;
      try {
        const rawGuwen: Uint8Array = await rm.getRawFileContent('gaokao_guwen_cards.json');
        const textGuwen: string = decoder.decodeToString(rawGuwen);
        const resultGuwen = await importCardPackage(textGuwen);
        guwenCards = resultGuwen.cards;
        guwenChains = resultGuwen.chains;
      } catch (e) {
        this.gaokaoImportResult = 'FAIL: gaokao_guwen_cards.json 读取失败: ' + JSON.stringify(e);
        this.isGaokaoImporting = false;
        return;
      }

      // Step 2：导入古诗词卡包（gaokao_poetry_cards.json）
      let poetryCards = 0;
      try {
        const rawPoetry: Uint8Array = await rm.getRawFileContent('gaokao_poetry_cards.json');
        const textPoetry: string = decoder.decodeToString(rawPoetry);
        const resultPoetry = await importCardPackage(textPoetry);
        poetryCards = resultPoetry.cards;
      } catch (e) {
        // 古诗词文件不存在不影响主流程
        console.warn('[ImportPage] gaokao_poetry_cards.json 读取失败: ' + JSON.stringify(e));
      }

      // Step 3：导入知识链叙事（gaokao_chain_narratives.json）
      let chainNarratives = 0;
      try {
        const rawNarr: Uint8Array = await rm.getRawFileContent('gaokao_chain_narratives.json');
        const textNarr: string = decoder.decodeToString(rawNarr);
        chainNarratives = await importChainMeta(textNarr);
      } catch (e) {
        console.warn('[ImportPage] gaokao_chain_narratives.json 读取失败: ' + JSON.stringify(e));
      }

      // Step 4：读 metadata 并打印汇总
      let metaInfo = '';
      try {
        const rawMeta: Uint8Array = await rm.getRawFileContent('gaokao_metadata.json');
        const textMeta: string = decoder.decodeToString(rawMeta);
        const meta = JSON.parse(textMeta) as Record<string, Object>;
        metaInfo = ' | 12集 | ' + (meta['total_episodes'] || '?') + ' episodes';
      } catch (_) {
        // metadata 缺失不影响主流程
      }

      const totalCards = guwenCards + poetryCards;
      this.gaokaoCards = totalCards;
      this.gaokaoChains = guwenChains;
      this.gaokaoImportResult = 'OK: ' + totalCards.toString() + ' 张卡片（' +
        guwenCards.toString() + ' 文言+' + poetryCards.toString() + ' 诗词）| ' +
        guwenChains.toString() + ' 链 | ' + chainNarratives.toString() + ' 叙事' + metaInfo;

      promptAction.showToast({
        message: '高考古诗文 ' + totalCards.toString() + ' 张卡片已导入',
        duration: 3000
      });
    } catch (e) {
      this.gaokaoImportResult = 'FAIL: ' + JSON.stringify(e);
    } finally {
      await db.migrateSubjectOwnership();
      this.isGaokaoImporting = false;
    }
  }

  // ── 卡片包导入（原有逻辑）─────────────────────────────

  async doCardImport(): Promise<void> {
    this.isImporting = true;
    this.importResult = '读取中...';

    try {
      const ctx = getContext(this);
      const rm = ctx.resourceManager;
      const rawData: Uint8Array = await rm.getRawFileContent('rujing_cards.json');
      const decoder: util.TextDecoder = util.TextDecoder.create('utf-8', { ignoreBOM: true });
      const text: string = decoder.decodeToString(rawData);

      const result = await importCardPackage(text);
      this.importedCards += result.cards;
      this.importedChains += result.chains;

      // 同时导入链叙事文本
      try {
        const narrData: Uint8Array = await rm.getRawFileContent('chain_narratives.json');
        const narrText: string = decoder.decodeToString(narrData);
        const chainCount: number = await importChainMeta(narrText);
        this.importResult = 'OK: ' + result.cards.toString() + ' cards, ' + result.chains.toString() + ' chains, ' + chainCount.toString() + ' narratives';
      } catch (_) {
        this.importResult = 'OK: ' + result.cards.toString() + ' cards, ' + result.chains.toString() + ' chains (no narratives)';
      }
    } catch (e) {
      this.importResult = 'FAIL: ' + JSON.stringify(e);
    } finally {
      await db.migrateSubjectOwnership();
      this.isImporting = false;
    }
  }

  // ── 书法·墨骨山河统一导入（UI 唯一入口）──────────────
  // 串联三个来源：mogustory_cards(+narratives) → cafa_cards(+narratives) → 视频元数据
  // migrateSubjectOwnership 在最后统一修正学科归属

  async doCalligraphyAllImport(): Promise<void> {
    this.isCalligraphyImporting = true;
    this.calligraphyImportResult = '';
    this.calligraphyCards = 0;
    this.calligraphyChains = 0;
    this.calligraphyVideos = 0;
    this.calligraphyVideoDetail = '';
    const ctx = getContext(this);
    const rm = ctx.resourceManager;
    const decoder: util.TextDecoder = util.TextDecoder.create('utf-8', { ignoreBOM: true });

    try {
      // Step 1：墨骨山河卡包（mogustory_cards.json + chain_narratives.json）
      try {
        const rawData: Uint8Array = await rm.getRawFileContent('mogustory_cards.json');
        const text: string = decoder.decodeToString(rawData);
        const result = await importCardPackage(text);
        this.calligraphyCards += result.cards;
        this.calligraphyChains += result.chains;
      } catch (e) {
        console.warn('[CalligraphyAll] mogustory_cards.json 失败: ' + JSON.stringify(e));
      }

      // Step 2：墨骨山河叙事（chain_narratives.json）
      try {
        const narrData: Uint8Array = await rm.getRawFileContent('chain_narratives.json');
        const narrText: string = decoder.decodeToString(narrData);
        const n = await importChainMeta(narrText);
        this.calligraphyChains += n; // chain_narratives.json 不新增链，但会更新标题
      } catch (e) {
        console.warn('[CalligraphyAll] chain_narratives.json 失败: ' + JSON.stringify(e));
      }

      // Step 3：国美书法校考卡包（cafa_cards.json）
      // cafa_cards 含：ep03-ep08（书法史）+ 古汉语基础/句读标志/译篆要诀（古诗文）
      // 学科归属由 doCardImport 末尾的 migrateSubjectOwnership 统一修正
      try {
        const rawCafa: Uint8Array = await rm.getRawFileContent('cafa_cards.json');
        const textCafa: string = decoder.decodeToString(rawCafa);
        const resultCafa = await importCardPackage(textCafa);
        this.calligraphyCards += resultCafa.cards;
        this.calligraphyChains += resultCafa.chains;
      } catch (e) {
        console.warn('[CalligraphyAll] cafa_cards.json 失败: ' + JSON.stringify(e));
      }

      // Step 4：CAFA 叙事（cafa_chain_narratives.json）
      try {
        const rawCN: Uint8Array = await rm.getRawFileContent('cafa_chain_narratives.json');
        const textCN: string = decoder.decodeToString(rawCN);
        await importChainMeta(textCN);
      } catch (e) {
        console.warn('[CalligraphyAll] cafa_chain_narratives.json 失败: ' + JSON.stringify(e));
      }

      // Step 5：视频元数据（直接读独立 ep 文件，不依赖有错的合并文件）
      // 每个 epN_metadata.json 的 chain_id 均与 mogustory_cards.json 完全对应：
      //   ep01→墨骨山河_ep01（李斯）  ep05→墨骨山河_ep05（张旭/怀素）
      //   ep02→墨骨山河_ep02（王羲之） ep06→墨骨山河_ep06（颜真卿）
      //   ep03→墨骨山河_ep03（苏轼）   ep07→墨骨山河_ep07（阮元）
      //   ep04→墨骨山河_ep04（孙过庭） ep08→墨骨山河_ep08（许慎）
      this.calligraphyVideoDetail = '';
      const videoStatusList: string[] = [];
      try {
        const allEpisodes: Record<string, Object>[] = [];
        const videoDir = getVideoDir();
        try { fileIo.mkdirSync(videoDir, true); } catch (_) {}
        const epFiles = ['ep01', 'ep02', 'ep03', 'ep04', 'ep05', 'ep06', 'ep07', 'ep08'];
        for (const epName of epFiles) {
          let epOk = false;
          let epReason = '';
          try {
            const rawMeta: Uint8Array = await rm.getRawFileContent(epName + '_metadata.json');
            const metaText: string = decoder.decodeToString(rawMeta);
            const epMeta = JSON.parse(metaText) as Record<string, Object>;
            const episodes = epMeta['episodes'] as Array<Record<string, Object>> | undefined;
            if (episodes && episodes.length > 0) {
              const ep = episodes[0];
              const videoFile = ep['video_file'] as string;
              if (videoFile && videoFile.length > 0) {
                const dstPath = videoDir + videoFile;
                try {
                  const rawV: Uint8Array = await rm.getRawFileContent(videoFile);
                  const fd: number = fileIo.openSync(dstPath,
                    fileIo.OpenMode.CREATE | fileIo.OpenMode.WRITE_ONLY).fd;
                  fileIo.writeSync(fd, rawV.buffer as ArrayBuffer);
                  fileIo.closeSync(fd);
                  ep['video_file'] = dstPath;
                  this.calligraphyVideos++;
                  epOk = true;
                  videoStatusList.push(epName + ':OK');
                } catch (e) {
                  // 读取失败时，记录错误但继续（不阻塞其他集）
                  const err = e as BusinessError;
                  epReason = '读取失败: ' + (err.message ?? JSON.stringify(e));
                  videoStatusList.push(epName + ':SKIP');
                  this.calligraphyVideoDetail = (this.calligraphyVideoDetail.length > 0
                    ? this.calligraphyVideoDetail + ' | ' : '') + epName + '跳过:' + (err.message ?? 'err');
                }
              } else {
                epReason = 'video_file为空';
                videoStatusList.push(epName + ':EMPTY');
              }
              allEpisodes.push(ep);
            } else {
              epReason = '无episodes数据';
              videoStatusList.push(epName + ':NO_DATA');
            }
          } catch (e) {
            epReason = 'metadata读取失败: ' + JSON.stringify(e);
            videoStatusList.push(epName + ':META_ERR');
          }
          // 记录失败原因
          if (!epOk && epReason.length > 0) {
            this.calligraphyVideoDetail = (this.calligraphyVideoDetail.length > 0
              ? this.calligraphyVideoDetail + ' | ' : '') + epName + '失败:' + epReason;
          }
        }
        if (allEpisodes.length > 0) {
          const mergedMetaStr = JSON.stringify({
            schema_version: '2.0.0',
            package_id: '墨骨山河_全集',
            series_title: '墨骨山河',
            total_episodes: allEpisodes.length,
            produced_by: 'PT-VFX',
            produced_at: (new Date()).toString(),
            episodes: allEpisodes
          });
          await importVideoPackage(mergedMetaStr);
        }
      } catch (e) {
        console.warn('[CalligraphyAll] 视频元数据导入失败: ' + JSON.stringify(e));
      }

      // 统一修正学科归属（处理历史遗留 subject 错误）
      const migrated = await db.migrateSubjectOwnership();

      // 【v7 精确修复】post-migration 逐条确认 EP01/02 subject
      // 根因：upsertChain UPDATE 分支不更新 subject，但 migration UPDATE 可能因游标
      // 或时序问题未覆盖 EP01/02。此处用 updateChainSubject 精确写死，确保 EP01/02
      // 在书法栏目下可见（chain_id.startsWith('墨骨山河') 过滤依赖 subject=CALLIGRAPHY）。
      const epFixList: string[] = ['墨骨山河_ep01', '墨骨山河_ep02'];
      for (const cid of epFixList) {
        const chain = await db.getChain(cid);
        if (chain) {
          await db.updateChainSubject(cid, Subject.CALLIGRAPHY);
          hilog.info(0x0000, 'ImportPage', '[POST-MIG] 精确修复 %{public}s subject -> 书法', cid);
        } else {
          hilog.warn(0x0000, 'ImportPage', '[POST-MIG] %{public}s 链不存在，跳过', cid);
        }
      }

      // 补充编号 + 诊断：一次性查询所有链
      const allChains = await db.getAllChains();
      let calligraphyChains: string[] = [];
      for (const c of allChains) {
        if (c.chain_id.startsWith('墨骨山河') || c.chain_id.startsWith('CHAIN_CAFA_Ep')) {
          calligraphyChains.push(c.chain_id);
          // 书法链：添加序号前缀（用 updateChainTitle 而非 upsertChain，避免覆盖 subject）
          // 墨骨山河系列 + CAFA书法史系列均需编号
          if (c.chain_id.startsWith('墨骨山河') || c.chain_id.startsWith('CHAIN_CAFA_Ep')) {
            const numbered = getCalligraphyDisplayTitle(c.chain_id, c.title);
            if (c.title !== numbered) {
              await db.updateChainTitle(c.chain_id, numbered);
              hilog.info(0x0000, 'ImportPage', '[TITLE] %{public}s -> "%{public}s"', c.chain_id, numbered);
            }
          }
          // 诊断日志
          hilog.info(0x0000, 'ImportPage', '[DIAG] chain: id=%{public}s subject=%{public}s card=%{public}d title="%{public}s"',
            c.chain_id, c.subject, c.card_count.toString(), c.title);
        }
      }
      hilog.info(0x0000, 'ImportPage', '[DIAG] 共 %{public}d 条书法链', calligraphyChains.length);

      this.calligraphyImportResult = 'OK: ' + this.calligraphyCards.toString() + ' 张卡片 | ' +
        this.calligraphyChains.toString() + ' 条链 | ' +
        this.calligraphyVideos.toString() + ' 集视频' +
        (migrated > 0 ? ' | 修正 ' + migrated.toString() + ' 条学科归属' : '');

      promptAction.showToast({
        message: '书法·墨骨山河 导入完成（' + this.calligraphyCards.toString() + '张卡片）',
        duration: 3000
      });
    } catch (e) {
      this.calligraphyImportResult = 'FAIL: ' + JSON.stringify(e);
    } finally {
      this.isCalligraphyImporting = false;
    }
  }

  // ── 地理山河系列导入 ─────────────────────────────────
  // 导入 geo_cards.json（16条链/32张卡片：自然+人文+区域）
  async doGeographyImport(): Promise<void> {
    this.isGeoImporting = true;
    this.geoImportResult = '';
    this.geoCards = 0;
    this.geoChains = 0;
    const ctx = getContext(this);
    const rm = ctx.resourceManager;
    const decoder: util.TextDecoder = util.TextDecoder.create('utf-8', { ignoreBOM: true });

    try {
      // Step 1：导入地理山河卡包（geo_cards.json）
      try {
        const rawGeo: Uint8Array = await rm.getRawFileContent('geo_cards.json');
        const textGeo: string = decoder.decodeToString(rawGeo);
        const result = await importCardPackage(textGeo);
        this.geoCards = result.cards;
        this.geoChains = result.chains;
      } catch (e) {
        this.geoImportResult = 'FAIL: geo_cards.json 读取失败: ' + JSON.stringify(e);
        this.isGeoImporting = false;
        return;
      }

      // Step 2：统一修正学科归属 + 地理链标题编号
      await db.migrateSubjectOwnership();
      const allChains = await db.getAllChains();
      let geoCount = 0;
      for (const c of allChains) {
        if (c.chain_id.startsWith('GEO_')) {
          geoCount++;
          hilog.info(0x0000, 'ImportPage', '[GEO] chain: id=%{public}s subject=%{public}s card=%{public}d title="%{public}s"',
            c.chain_id, c.subject, c.card_count.toString(), c.title);
        }
      }

      this.geoImportResult = 'OK: ' + this.geoCards.toString() + ' 张卡片 | ' +
        this.geoChains.toString() + ' 条链（自然8+人文4+区域4）';

      promptAction.showToast({
        message: '地理山河 ' + this.geoCards.toString() + ' 张卡片已导入',
        duration: 3000
      });
    } catch (e) {
      this.geoImportResult = 'FAIL: ' + JSON.stringify(e);
    } finally {
      this.isGeoImporting = false;
    }
  }


  // 思想政治体系导入
  async doPoliticsImport(): Promise<void> {
    this.isPoliticsImporting = true;
    this.politicsImportResult = '';
    this.politicsCards = 0;
    this.politicsChains = 0;
    const ctx = getContext(this);
    const rm = ctx.resourceManager;
    const decoder: util.TextDecoder = util.TextDecoder.create('utf-8', { ignoreBOM: true });

    try {
      try {
        const rawData: Uint8Array = await rm.getRawFileContent('political_cards.json');
        const text: string = decoder.decodeToString(rawData);
        const result = await importCardPackage(text);
        this.politicsCards = result.cards;
        this.politicsChains = result.chains;
      } catch (e) {
        this.politicsImportResult = 'FAIL: political_cards.json 读取失败: ' + JSON.stringify(e);
        this.isPoliticsImporting = false;
        return;
      }

      await db.migrateSubjectOwnership();
      const allChains = await db.getAllChains();
      for (const c of allChains) {
        if (c.chain_id.startsWith('POLI_')) {
          hilog.info(0x0000, 'ImportPage', '[POLI] chain: id=%{public}s subject=%{public}s card=%{public}d title="%{public}s"',
            c.chain_id, c.subject, c.card_count.toString(), c.title);
        }
      }

      this.politicsImportResult = 'OK: ' + this.politicsCards.toString() + ' 张卡片 | ' +
        this.politicsChains.toString() + ' 条知识链（经济4+政治4+哲学4+法律2+时事2）';

      promptAction.showToast({
        message: '思想政治 ' + this.politicsCards.toString() + ' 张卡片已导入',
        duration: 3000
      });
    } catch (e) {
      this.politicsImportResult = 'FAIL: ' + JSON.stringify(e);
    } finally {
      this.isPoliticsImporting = false;
    }
  }

}
