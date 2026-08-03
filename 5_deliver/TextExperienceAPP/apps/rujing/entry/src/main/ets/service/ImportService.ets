/**
 * 入境 APP · 导入服务
 * 从 PT-038 产出的 JSON/CSV 导入卡片和链元数据
 * v2 扩展（2026-07-16）：新增 video_package 导入（IF-B 协议）
 * v3 扩展（2026-08-01）：interface_version 标准化（P0）
 */

import { db } from './DatabaseService';
import { CardPackage, ChainMeta, Card, Chain, CardType, Maturity, ChainType, Subject, ChainRole } from '../model/DataModel';
import { fileIo } from '@kit.CoreFileKit';
import { util } from '@kit.ArkTS';
import { application } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';

const DOMAIN = 0xFF00;
const TAG = 'ImportService';

/**
 * 卡片包顶层元数据（interface_version 协议）
 * 用于版本协商和溯源
 */
export interface PackageHeader {
  interface_version?: string   // e.g. "3.0", "4.0"
  package_id?: string          // v3 标准字段
  pack_id?: string            // v1/v2 遗留字段（向后兼容）
  package_title?: string       // v3 标准字段
  pack_title?: string          // v1/v2 遗留字段（向后兼容）
  kb_source?: KbSource         // KB 溯源信息（v3+ 新增）
}

export interface KbSource {
  pack_id: string
  kb_version: string
  generated_at: string
  generator: string
}

/**
 * 检测卡片包的接口版本
 * 向后兼容所有版本：v1（pack_id）/ v2（schema_version）/ v3+（interface_version）
 */
function detectInterfaceVersion(raw: string): string {
  try {
    const obj: Record<string, Object> = JSON.parse(raw);
    const ifVer = obj['interface_version'];
    // v3+ 标准字段
    if (ifVer !== undefined && typeof ifVer === 'string') {
      hilog.info(DOMAIN, TAG, 'Detected interface_version: %{public}s', ifVer as string);
      return ifVer as string;
    }
    // v1/v2 legacy 格式（无 interface_version）
    const packId = obj['pack_id'];
    const schemaVer = obj['schema_version'];
    if (packId !== undefined || schemaVer !== undefined) {
      hilog.info(DOMAIN, TAG, 'Legacy package (no interface_version), treating as v3 compatible');
      return '3.0';
    }
    // 完全未知格式
    hilog.warn(DOMAIN, TAG, 'Unknown package format, defaulting to v3');
    return '3.0';
  } catch (e) {
    hilog.error(DOMAIN, TAG, 'JSON parse failed in detectInterfaceVersion: %{public}s', String(e));
    return 'unknown';
  }
}

/**
 * 规范化卡片包顶层字段
 * 兼容 pack_id→package_id / pack_title→package_title 的旧命名
 */
function normalizePackageFields(pkg: Record<string, Object>): Record<string, Object> {
  // pack_id → package_id
  const hasPkgId = pkg['package_id'] !== undefined;
  const hasPackId = pkg['pack_id'] !== undefined;
  if (!hasPkgId && hasPackId) {
    pkg['package_id'] = pkg['pack_id'];
    hilog.info(DOMAIN, TAG, 'Normalized: pack_id → package_id');
  }
  // pack_title → package_title
  const hasPkgTitle = pkg['package_title'] !== undefined;
  const hasPackTitle = pkg['pack_title'] !== undefined;
  if (!hasPkgTitle && hasPackTitle) {
    pkg['package_title'] = pkg['pack_title'];
  }
  // interface_version 缺失时设为默认值（向后兼容）
  if (pkg['interface_version'] === undefined) {
    pkg['interface_version'] = '3.0';
  }
  return pkg;
}

/**
 * 规范化 card_type 大小写
 * 旧包用大写（"NODE" / "STRATEGY" / "CHAIN"），新包用小写（"node" / "strategy" / "chain"）
 */
function normalizeCardType(raw: string | undefined): CardType {
  if (!raw) return CardType.NODE;
  const lower = raw.toLowerCase();
  if (lower === 'node' || lower === 'strategy' || lower === 'chain') {
    return lower as CardType;
  }
  // 未知类型，降级为 node
  hilog.warn(DOMAIN, TAG, 'Unknown card_type "%{public}s", defaulting to node', raw);
  return CardType.NODE;
}

/** 运行时派生路径（基于 app context.filesDir，避免硬编码漂移） */
function getVideoDirImpl(): string {
  return application.getApplicationContext().filesDir + '/rujing/videos/';
}
function getNarrativeDirImpl(): string {
  return application.getApplicationContext().filesDir + '/rujing/narratives/';
}

/**
 * 视频包元数据（IF-B 协议子集）
 * 来自 PT-VFX series_builder.py 输出的 metadata.json
 */
export interface VideoPackageMeta {
  schema_version: string
  package_id: string
  series_title: string
  total_episodes: number
  produced_by: string
  produced_at: string
  episodes: VideoEpisode[]
}

export interface VideoEpisode {
  ep: number
  title: string
  subtitle?: string
  video_file: string
  audio_file?: string
  duration_seconds: number
  resolution?: string
  bitrate_kbps?: number
  chains: string[]
  cards_file?: string
  scene_timeline: SceneTimelineEntry[]
}

export interface FiveSkandha {
  color_base?: string
  action_prompt?: string
  recognition_marker?: string
}

export interface SceneTimelineEntry {
  idx: number
  time: number
  scene_name: string
  scene_type?: string
  chain_ref?: string
  five_skandha?: FiveSkandha
}

/**
 * 初始化叙事文本目录
 */
function ensureNarrativeDir(): void {
  try {
    fileIo.mkdirSync(getNarrativeDirImpl(), true);
  } catch (_) {
    // 目录已存在
  }
}

/**
 * 从叙事文本文件读取
 */
function readNarrative(chain_id: string): string {
  try {
    const path: string = getNarrativeDirImpl() + chain_id + '.txt';
    const file: fileIo.File = fileIo.openSync(path, fileIo.OpenMode.READ_ONLY);
    const stat = fileIo.statSync(path);
    const buf: ArrayBuffer = new ArrayBuffer(stat.size);
    fileIo.readSync(file.fd, buf);
    fileIo.closeSync(file);
    const decoder: util.TextDecoder = util.TextDecoder.create('utf-8', { ignoreBOM: true });
    return decoder.decodeToString(new Uint8Array(buf));
  } catch (_) {
    return '';
  }
}

/**
 * 写入叙事文本文件
 */
function writeNarrative(chain_id: string, text: string): void {
  ensureNarrativeDir();
  const path: string = getNarrativeDirImpl() + chain_id + '.txt';
  const file: fileIo.File = fileIo.openSync(path, fileIo.OpenMode.CREATE | fileIo.OpenMode.WRITE_ONLY);
  const encoder: util.TextEncoder = new util.TextEncoder();
  const data: Uint8Array = encoder.encodeInto(text);
  fileIo.writeSync(file.fd, data.buffer as ArrayBuffer);
  fileIo.closeSync(file);
}

/**
 * 从 chain_id 推断显示标题（含序号前缀，供书法链编号）
 *
 * 【墨骨山河系列】编号映射（ep_metadata 确认）：
 *   墨骨山河_ep01 → 1_李斯·小篆的秩序与第一道名字
 *   墨骨山河_ep02 → 2_王羲之·兰亭序与书法的觉醒
 *   墨骨山河_ep03 → 3_苏轼·寒食帖与书法的生命维度
 *   墨骨山河_ep04 → 4_孙过庭·书谱之道
 *   墨骨山河_ep05 → 5_张旭怀素·草书的极限与癫狂
 *   墨骨山河_ep06 → 6_颜真卿·忠烈之书与大唐的至暗时刻
 *   墨骨山河_ep07 → 7_阮元与书法的版图重划
 *   墨骨山河_ep08 → 8_许慎·六书之学与汉字的终极命名
 *
 * 【CAFA书法史系列】编号映射（按 chain_id Ep 编号排列）：
 *   CHAIN_CAFA_Ep01_李斯·小篆统一   → 1_李斯·小篆统一
 *   CHAIN_CAFA_Ep02_王羲之·兰亭之雅 → 2_王羲之·兰亭之雅
 *   CHAIN_CAFA_Ep03_兰亭之雅         → 3_兰亭之雅
 *   CHAIN_CAFA_Ep04_书谱之道         → 4_书谱之道
 *   CHAIN_CAFA_Ep05_颠张醉素         → 5_颠张醉素
 *   CHAIN_CAFA_Ep06_颜筋柳骨         → 6_颜筋柳骨
 *   CHAIN_CAFA_Ep07_黄州突围         → 7_黄州突围
 *   CHAIN_CAFA_Ep08_碑学中兴         → 8_碑学中兴
 */
export function getCalligraphyDisplayTitle(chain_id: string, baseTitle: string): string {
  // 墨骨山河系列
  const epKeys: string[] = [
    '墨骨山河_ep01', '墨骨山河_ep02', '墨骨山河_ep03', '墨骨山河_ep04',
    '墨骨山河_ep05', '墨骨山河_ep06', '墨骨山河_ep07', '墨骨山河_ep08'
  ];
  const epTitles: string[] = [
    '1_李斯·小篆的秩序与第一道名字',
    '2_王羲之·兰亭序与书法的觉醒',
    '3_苏轼·寒食帖与书法的生命维度',
    '4_孙过庭·书谱之道',
    '5_张旭怀素·草书的极限与癫狂',
    '6_颜真卿·忠烈之书与大唐的至暗时刻',
    '7_阮元与书法的版图重划',
    '8_许慎·六书之学与汉字的终极命名',
  ];
  let idx: number = epKeys.indexOf(chain_id);
  if (idx >= 0) {
    return epTitles[idx];
  }
  // CAFA书法史系列
  const cafaKeys: string[] = [
    'CHAIN_CAFA_Ep01_李斯·小篆统一',
    'CHAIN_CAFA_Ep02_王羲之·兰亭之雅',
    'CHAIN_CAFA_Ep03_兰亭之雅',
    'CHAIN_CAFA_Ep04_书谱之道',
    'CHAIN_CAFA_Ep05_颠张醉素',
    'CHAIN_CAFA_Ep06_颜筋柳骨',
    'CHAIN_CAFA_Ep07_黄州突围',
    'CHAIN_CAFA_Ep08_碑学中兴',
  ];
  const cafaTitles: string[] = [
    '1_李斯·小篆统一',
    '2_王羲之·兰亭之雅',
    '3_兰亭之雅',
    '4_书谱之道',
    '5_颠张醉素',
    '6_颜筋柳骨',
    '7_黄州突围',
    '8_碑学中兴',
  ];
  idx = cafaKeys.indexOf(chain_id);
  if (idx >= 0) {
    return cafaTitles[idx];
  }
  return baseTitle;
}

/**
 * 从 chain_id 推断地理链显示标题（含序号前缀）
 * 【地理山河系列】16条链编号映射（标题压缩至10字以内）：
 *   自然地理要素链（8条）：
 *     GEO_山河_黄河   → 1_黄河·九曲
 *     GEO_山河_长江   → 2_长江·三峡
 *     GEO_山河_淮河   → 3_淮河
 *     GEO_山河_珠江   → 4_珠江三角洲
 *     GEO_山河_松花江 → 5_松花江
 *     GEO_山河_塔里木 → 6_塔里木
 *     GEO_山河_青藏   → 7_青藏高原
 *     GEO_山河_天山   → 8_天山
 *   人文地理要素链（4条）：
 *     GEO_人地_人口迁移   → 9_人口迁移
 *     GEO_人地_产业转移   → 10_产业转移
 *     GEO_人地_农业地域   → 11_农业地域
 *     GEO_人地_可持续发展 → 12_可持续发展
 *   区域综合链（4条）：
 *     GEO_区域_北方地区 → 13_北方地区
 *     GEO_区域_南方地区 → 14_南方地区
 *     GEO_区域_西北地区 → 15_西北地区
 *     GEO_区域_青藏地区 → 16_青藏地区
 */
export function getGeographyDisplayTitle(chain_id: string, baseTitle: string): string {
  // 自然地理要素链（8条）
  const natKeys: string[] = [
    'GEO_山河_黄河', 'GEO_山河_长江', 'GEO_山河_淮河', 'GEO_山河_珠江',
    'GEO_山河_松花江', 'GEO_山河_塔里木', 'GEO_山河_青藏', 'GEO_山河_天山'
  ];
  const natTitles: string[] = [
    '1_黄河·九曲', '2_长江·三峡', '3_淮河', '4_珠江三角洲',
    '5_松花江', '6_塔里木', '7_青藏高原', '8_天山'
  ];
  let idx: number = natKeys.indexOf(chain_id);
  if (idx >= 0) {
    return natTitles[idx];
  }
  // 人文地理要素链（4条）
  const humKeys: string[] = [
    'GEO_人地_人口迁移', 'GEO_人地_产业转移',
    'GEO_人地_农业地域', 'GEO_人地_可持续发展'
  ];
  const humTitles: string[] = [
    '9_人口迁移', '10_产业转移',
    '11_农业地域', '12_可持续发展'
  ];
  idx = humKeys.indexOf(chain_id);
  if (idx >= 0) {
    return humTitles[idx];
  }
  // 区域综合链（4条）
  const regKeys: string[] = [
    'GEO_区域_北方地区', 'GEO_区域_南方地区',
    'GEO_区域_西北地区', 'GEO_区域_青藏地区'
  ];
  const regTitles: string[] = [
    '13_北方地区', '14_南方地区',
    '15_西北地区', '16_青藏地区'
  ];
  idx = regKeys.indexOf(chain_id);
  if (idx >= 0) {
    return regTitles[idx];
  }
  return baseTitle;
}

/**
 * 从 chain_id 推断政治链显示标题（含序号前缀）
 * 【思想政治系列】16条链编号映射：
 *   经济生活链（4条）：
 *     POLI_经济_商品货币 → 1_商品与货币
 *     POLI_经济_生产消费 → 2_生产与消费
 *     POLI_经济_分配保障 → 3_分配与社保
 *     POLI_经济_市场经济 → 4_市场经济
 *   政治生活链（4条）：
 *     POLI_政治_国家公民 → 5_国家与公民
 *     POLI_政治_政党制度 → 6_政党制度
 *     POLI_政治_人大制度 → 7_人大制度
 *     POLI_政治_国际社会 → 8_国际社会
 *   哲学常识链（4条）：
 *     POLI_哲学_唯物论   → 9_唯物论基础
 *     POLI_哲学_唯物辩证 → 10_唯物辩证法
 *     POLI_哲学_认识实践 → 11_认识与实践
 *     POLI_哲学_历史唯物 → 12_历史唯物主义
 *   法律道德链（2条）：
 *     POLI_法律_公民权利 → 13_公民权利义务
 *     POLI_法律_法律基础 → 14_法律基础
 *   时事政治链（2条）：
 *     POLI_时事_国内热点 → 15_国内时政热点
 *     POLI_时事_国际热点 → 16_国际时政热点
 */
export function getPoliticsDisplayTitle(chain_id: string, baseTitle: string): string {
  const poliKeys: string[] = [
    'POLI_经济_商品货币', 'POLI_经济_生产消费', 'POLI_经济_分配保障', 'POLI_经济_市场经济',
    'POLI_政治_国家公民', 'POLI_政治_政党制度', 'POLI_政治_人大制度', 'POLI_政治_国际社会',
    'POLI_哲学_唯物论', 'POLI_哲学_唯物辩证', 'POLI_哲学_认识实践', 'POLI_哲学_历史唯物',
    'POLI_法律_公民权利', 'POLI_法律_法律基础',
    'POLI_时事_国内热点', 'POLI_时事_国际热点'
  ];
  const poliTitles: string[] = [
    '1_商品与货币', '2_生产与消费', '3_分配与社保', '4_市场经济',
    '5_国家与公民', '6_政党制度', '7_人大制度', '8_国际社会',
    '9_唯物论基础', '10_唯物辩证法', '11_认识与实践', '12_历史唯物主义',
    '13_公民权利义务', '14_法律基础',
    '15_国内时政热点', '16_国际时政热点'
  ];
  const idx: number = poliKeys.indexOf(chain_id);
  if (idx >= 0) {
    return poliTitles[idx];
  }
  return baseTitle;
}

/**
 * 从 chain_id 前缀推断学科
 * 解决 narrative JSON 缺 subject 字段、以及 mogustory_cards 默认 HISTORY 的问题
 *
 * 分类规则（2026-07-30 最终版）：
 *   墨骨山河_ep*  / CHAIN_CAFA_Ep*     → 书法
 *   GAOKAO_EP* / CHAIN_炼字* 等       → 古诗文
 *   其余所有 CHAIN_* 链（实词/虚词/句式/推断/意象/固定搭配等）→ 古诗文
 *   CHAIN_近代* / CHAIN_现代* / CHAIN_全球关联* 等             → 历史
 *   GEO_山河_* / GEO_人地_* / GEO_区域_*                       → 地理
 */
function inferSubject(chain_id: string): Subject {
  // CAFA古汉语三链：属于古诗文（译篆/句读/文字学基础），非书法
  // 注意：CAFA_Ep03/04/05/06/07/08 保留 CALLIGRAPHY，因其为墨骨山河 CAFA 版本
  //       （内容虽是古诗文，但与 墨骨山河_ep01~ep08 共同构成书法备考系列）
  if (chain_id === 'CHAIN_CAFA_古汉语基础' ||
      chain_id === 'CHAIN_CAFA_句读标志' ||
      chain_id === 'CHAIN_CAFA_译篆要诀') {
    return Subject.GUWEN;  // 古诗文
  }
  // 书法史链
  if (chain_id.startsWith('墨骨山河') ||
      chain_id.startsWith('CHAIN_CAFA_Ep')) {
    return Subject.CALLIGRAPHY;  // 书法
  }
  // 地理山河链（自然/人文/区域三类）
  if (chain_id.startsWith('GEO_山河_') ||
      chain_id.startsWith('GEO_人地_') ||
      chain_id.startsWith('GEO_区域_')) {
    return Subject.GEOGRAPHY;  // 地理
  }
  // 政治链（经济/政治/哲学/法律/时事五类）
  if (chain_id.startsWith('POLI_经济_') ||
      chain_id.startsWith('POLI_政治_') ||
      chain_id.startsWith('POLI_哲学_') ||
      chain_id.startsWith('POLI_法律_') ||
      chain_id.startsWith('POLI_时事_')) {
    return Subject.POLITICS;  // 政治
  }
  // 历史链（近代/现代/全球关联/外交 → 保持历史）
  if (chain_id.startsWith('CHAIN_近代') ||
      chain_id.startsWith('CHAIN_现代') ||
      chain_id.startsWith('CHAIN_全球关联') ||
      chain_id.startsWith('CHAIN_现代外交')) {
    return Subject.HISTORY;  // 历史
  }
  // 古诗文链（其余所有 CHAIN_* + GAOKAO_*）
  if (chain_id.startsWith('CHAIN_') ||
      chain_id.startsWith('GAOKAO_EP')) {
    return Subject.GUWEN;  // 古诗文
  }
  return Subject.HISTORY;  // 历史（兜底）
}

/**
 * 从 PT-038 卡片包 JSON 导入
 */
export interface ImportResult {
  cards: number
  chains: number
}

export async function importCardPackage(jsonText: string): Promise<ImportResult> {
  // Step 0: 读取 interface_version（用于日志和未来版本协商）
  const ifVer = detectInterfaceVersion(jsonText);
  hilog.info(DOMAIN, TAG, '[importCardPackage] interface_version=%{public}s', ifVer);

  // Step 1: 解析为 object 以便规范化字段
  const raw: object = JSON.parse(jsonText);
  const pkg: CardPackage = raw as CardPackage;

  // Step 2: 规范化字段（pack_id→package_id，interface_version 默认值）
  const rawRec = raw as Record<string, Object>;
  if (rawRec['package_id'] === undefined && rawRec['pack_id'] !== undefined) {
    rawRec['package_id'] = rawRec['pack_id'];
    hilog.info(DOMAIN, TAG, 'Normalized: pack_id → package_id');
  }
  if (rawRec['package_title'] === undefined && rawRec['pack_title'] !== undefined) {
    rawRec['package_title'] = rawRec['pack_title'];
  }
  if (rawRec['interface_version'] === undefined) {
    rawRec['interface_version'] = '3.0';
  }

  let cardCount: number = 0;
  const chainSet: Set<string> = new Set<string>();

  // 处理三型卡片（v3 格式）
  const allCards: Partial<Card>[] = [];
  if (pkg.node_cards) {
    for (const c of pkg.node_cards) { allCards.push(c); }
  }
  if (pkg.strategy_cards) {
    for (const c of pkg.strategy_cards) { allCards.push(c); }
  }
  if (pkg.chain_cards) {
    for (const c of pkg.chain_cards) { allCards.push(c); }
  }
  // 兼容 v1/v2 扁平格式
  if (pkg.cards) {
    for (const c of pkg.cards) { allCards.push(c); }
  }

  const now: number = Date.now();

  // 构建 chain_id → chain_title 映射
  const chainTitles: Map<string, string> = new Map<string, string>();

  for (const c of allCards) {
    if (!c.card_id || !c.chain_id) continue;

    // 记录链标题（取第一个非空值）
    if (!chainTitles.has(c.chain_id) && c.chain_title) {
      chainTitles.set(c.chain_id, c.chain_title);
    }

    const card: Card = {
      card_id: c.card_id,
      chain_id: c.chain_id,
      chain_title: c.chain_title ?? c.chain_id,
      card_type: normalizeCardType(c.card_type as string | undefined),
      chain_role: (c.chain_role as ChainRole) ?? ChainRole.PROCESS,
      front: c.front ?? '',
      back_core: c.back_core ?? '',
      back_detail: c.back_detail ?? '',
      maturity: Maturity.RAW,
      tags: c.tags ?? [],
      is_new: true,
      last_marked: 0
    };

    await db.upsertCard(card);
    chainSet.add(c.chain_id);
    cardCount++;
  }

  // 为每个链创建/更新链记录
  for (const chain_id of chainSet) {
    let readableTitle: string = chainTitles.get(chain_id) ?? chain_id;
    // 书法链：加序号前缀
    if (chain_id.startsWith('墨骨山河') || chain_id.startsWith('CHAIN_CAFA_Ep')) {
      readableTitle = getCalligraphyDisplayTitle(chain_id, readableTitle);
    }
    // 地理山河链：加序号前缀（1_黄河·九曲入海 等）
    if (chain_id.startsWith('GEO_')) {
      readableTitle = getGeographyDisplayTitle(chain_id, readableTitle);
    }
    // 政治链：加序号前缀（1_商品与货币 等）
    if (chain_id.startsWith('POLI_')) {
      readableTitle = getPoliticsDisplayTitle(chain_id, readableTitle);
    }
    const existing: Chain | null = await db.getChain(chain_id);
    if (existing) {
      // 用可读标题更新
      if (existing.title === existing.chain_id) {
        existing.title = readableTitle;
        await db.upsertChain(existing);
      }
      await db.recalcChainCounts(chain_id);
    } else {
      const chain: Chain = {
        chain_id: chain_id,
        title: readableTitle,
        subject: inferSubject(chain_id),
        chain_type: ChainType.CAUSAL,
        narrative: '',
        child_cards: [],
        related_chains: [],
        tags: [],
        card_count: 0,
        raw_count: 0,
        cooked_count: 0,
        last_viewed: 0,
        created_at: now,
        updated_at: now
      };
      await db.upsertChain(chain);
      await db.recalcChainCounts(chain_id);
    }
  }

  const result: ImportResult = { cards: cardCount, chains: chainSet.size };
  return result;
}

/**
 * 导入链元数据（叙事文本 + 关联关系）
 */
export async function importChainMeta(jsonText: string): Promise<number> {
  ensureNarrativeDir();

  let metas: ChainMeta[];
  try {
    const parsed: object = JSON.parse(jsonText);
    // 兼容三种格式：
    // 1. 裸数组  [{chain_id, narrative}, ...]  （旧 chain_narratives.json / gaokao_chain_narratives.json）
    // 2. 包裹对象 {chains: [...]}               （gaokao_chain_narratives.json 变体）
    // 3. 单个对象 {chain_id, narrative}          （边界情况）
    // 注：cafa_chain_narratives.json 为字典格式 {chain_id: {...}}，其 narrative 字段全为空，
    //     暂不处理；CAFA 古汉语链的归属由 migrateSubjectOwnership 统一纠正
    if (Array.isArray(parsed)) {
      metas = parsed as ChainMeta[];
    } else {
      const wrapper = parsed as Record<string, object>;
      // 格式2：{chains: [...]}  — 用 try/catch 代替 'in' 操作符（arkts-no-in 规则）
      try {
        const chainsArr = wrapper['chains'] as ChainMeta[];
        if (chainsArr && Array.isArray(chainsArr)) {
          metas = chainsArr;
        } else {
          // 格式3：单个对象 —  fallback
          metas = [parsed as ChainMeta];
        }
      } catch (_) {
        metas = [parsed as ChainMeta];
      }
    }
  } catch (_) {
    return 0;
  }

  let count: number = 0;

  for (const meta of metas) {
    if (!meta.chain_id) continue;

    // 保存叙事文本到文件系统
    if (meta.narrative) {
      writeNarrative(meta.chain_id, meta.narrative);
    }

    // 更新链记录
    const existing: Chain | null = await db.getChain(meta.chain_id);
    if (existing) {
      existing.title = meta.chain_title ?? existing.title;
      // subject 字段为空字符串（chain_narratives）或无效值时，用 inferSubject 兜底
      const metaSubject = meta.subject as string;
      existing.subject = (metaSubject && metaSubject.length > 0)
        ? (metaSubject as Subject)
        : inferSubject(meta.chain_id);
      existing.chain_type = (meta.chain_type as ChainType) ?? existing.chain_type;
      existing.related_chains = meta.related_chains ?? [];
      existing.tags = meta.tags ?? [];
      existing.narrative = meta.narrative ?? '';
      existing.updated_at = Date.now();
      await db.upsertChain(existing);
    } else {
      const chain: Chain = {
        chain_id: meta.chain_id,
        title: meta.chain_title ?? meta.chain_id,
        subject: inferSubject(meta.chain_id),
        chain_type: (meta.chain_type as ChainType) ?? ChainType.CAUSAL,
        narrative: meta.narrative ?? '',
        child_cards: [],
        related_chains: meta.related_chains ?? [],
        tags: meta.tags ?? [],
        card_count: 0,
        raw_count: 0,
        cooked_count: 0,
        last_viewed: 0,
        created_at: Date.now(),
        updated_at: Date.now()
      };
      await db.upsertChain(chain);
    }
    count++;
  }

  return count;
}

/**
 * 获取链的叙事文本
 */
export function getChainNarrative(chain_id: string): string {
  return readNarrative(chain_id);
}

// ─── 视频包导入（IF-B 协议，v2 新增）──────────────────────────

/**
 * 确保视频目录存在
 */
function ensureVideoDir(): void {
  try {
    fileIo.mkdirSync(getVideoDirImpl(), true);
  } catch (_) {
    // 目录已存在
  }
}

/**
 * 保存视频包元数据（IF-B metadata.json）到本地
 */
function saveVideoMeta(package_id: string, meta: VideoPackageMeta): void {
  ensureVideoDir();
  const path: string = getVideoDirImpl() + package_id + '_metadata.json';
  const file: fileIo.File = fileIo.openSync(path, fileIo.OpenMode.CREATE | fileIo.OpenMode.WRITE_ONLY);
  const encoder: util.TextEncoder = new util.TextEncoder();
  const data: Uint8Array = encoder.encodeInto(JSON.stringify(meta));
  fileIo.writeSync(file.fd, data.buffer as ArrayBuffer);
  fileIo.closeSync(file);
}

/**
 * 获取视频包元数据
 */
export function getVideoMeta(package_id: string): VideoPackageMeta | null {
  try {
    const path: string = getVideoDirImpl() + package_id + '_metadata.json';
    const file: fileIo.File = fileIo.openSync(path, fileIo.OpenMode.READ_ONLY);
    const stat = fileIo.statSync(path);
    const buf: ArrayBuffer = new ArrayBuffer(stat.size);
    fileIo.readSync(file.fd, buf);
    fileIo.closeSync(file);
    const decoder: util.TextDecoder = util.TextDecoder.create('utf-8', { ignoreBOM: true });
    return JSON.parse(decoder.decodeToString(new Uint8Array(buf))) as VideoPackageMeta;
  } catch (_) {
    return null;
  }
}

/**
 * 获取视频包目录
 */
export function getVideoDir(): string {
  return getVideoDirImpl();
}

/**
 * 导入 PT-VFX 产出的视频包（IF-B metadata.json）
 *
 * 工作流程：
 *   1. 解析 IF-B metadata JSON
 *   2. 保存到本地视频目录（videoService 读取 file:// 路径）
 *   3. 解析 scene_timeline，建立 chain_id → video 映射
 *   4. 在 DatabaseService 中为相关链关联视频
 *
 * @param jsonText IF-B video_package metadata JSON 字符串
 * @returns 导入结果 {episodes, chains}
 */
export interface VideoImportResult {
  package_id: string
  series_title: string
  episodes: number
  chains: number
}

export async function importVideoPackage(jsonText: string): Promise<VideoImportResult> {
  let meta: VideoPackageMeta;
  try {
    meta = JSON.parse(jsonText) as VideoPackageMeta;
  } catch (_) {
    return { package_id: '', series_title: '', episodes: 0, chains: 0 };
  }

  const package_id = meta.package_id || 'unknown';
  const series_title = meta.series_title || '';

  // 1. 保存 metadata 到本地
  saveVideoMeta(package_id, meta);

  // 2. 收集涉及的 chain_id
  const chainSet: Set<string> = new Set<string>();
  for (const ep of meta.episodes) {
    for (const chain of ep.chains) {
      chainSet.add(chain);
    }
  }

  // 3. 可选：在 DatabaseService 中为链关联视频（如果有 db.addVideoMeta 等接口）
  // 目前先不做数据库写入，视频信息通过 getVideoMeta() 按需读取
  // 后续如果 DatabaseService 有 schema 支持，可以在这里调用 db.upsertChainVideo()

  const result: VideoImportResult = {
    package_id,
    series_title,
    episodes: meta.episodes.length,
    chains: chainSet.size
  };

  return result;
}

/**
 * 根据 chain_id 查找对应的视频集信息
 * 遍历所有已导入的视频包，找到包含该 chain 的集
 */
export async function findVideoForChain(chain_id: string): Promise<VideoEpisode | null> {
  // 扫描视频目录中的 metadata 文件
  try {
    const dir = fileIo.listFileSync(getVideoDirImpl());
    for (const fname of dir) {
      if (fname.endsWith('_metadata.json')) {
        const pkgId = fname.replace('_metadata.json', '');
        const meta = getVideoMeta(pkgId);
        if (meta) {
          for (const ep of meta.episodes) {
            if (ep.chains.includes(chain_id)) {
              return ep;
            }
          }
        }
      }
    }
  } catch (_) {}
  return null;
}
