/**
 * 入境 APP · 导入服务
 * 从 PT-038 产出的 JSON/CSV 导入卡片和链元数据
 * v2 扩展（2026-07-16）：新增 video_package 导入（IF-B 协议）
 */

import { db } from './DatabaseService';
import { CardPackage, ChainMeta, Card, Chain, CardType, Maturity, ChainType, Subject, ChainRole } from '../model/DataModel';
import { fileIo } from '@kit.CoreFileKit';
import { util } from '@kit.ArkTS';
import { application } from '@kit.AbilityKit';

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
 * 从 PT-038 卡片包 JSON 导入
 */
export interface ImportResult {
  cards: number
  chains: number
}

export async function importCardPackage(jsonText: string): Promise<ImportResult> {
  const pkg: CardPackage = JSON.parse(jsonText) as CardPackage;
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
      card_type: (c.card_type as CardType) ?? CardType.NODE,
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
    const readableTitle: string = chainTitles.get(chain_id) ?? chain_id;
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
        subject: Subject.HISTORY,
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
    // 1. 裸数组  [{chain_id, narrative}, ...]  （旧 chain_narratives.json）
    // 2. 单个对象 {chain_id, narrative}          （边界情况）
    // 3. 包裹对象 {chains: [...]}               （gaokao_chain_narratives.json）
    if (Array.isArray(parsed)) {
      metas = parsed as ChainMeta[];
    } else {
      // 用类型断言 + try/catch 代替 in 操作符（arkts-no-in 规则）
      const wrapper = parsed as Record<string, object>;
      try {
        const chainsArr = wrapper['chains'] as ChainMeta[];
        if (chainsArr && Array.isArray(chainsArr)) {
          metas = chainsArr;
        } else {
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
      existing.subject = (meta.subject as Subject) ?? existing.subject;
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
        subject: (meta.subject as Subject) ?? Subject.GUWEN,
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
