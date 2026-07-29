/**
 * storage/storageService.ts — 基于 Preferences 的泛型 CRUD 封装
 *
 * ============================================================================
 * 设计理念
 * ============================================================================
 * 1. 泛型支持：同一套代码可存储 Note / Habit / Subscription 等任意数据类型
 * 2. 零后端依赖：纯本地 Preferences 操作，无需网络/账号
 * 3. 错误友好：所有方法内置 try/catch，不会因存储异常导致 App 崩溃
 * 4. 单例初始化：Preferences 实例只创建一次，后续方法复用
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * // 1. 在 EntryAbility 中初始化
 * import { StorageService } from '../common/storage/storageService';
 * StorageService.init(this.context);
 *
 * // 2. 创建存储实例
 * const noteStore = new StorageService<Note>(STORAGE_KEYS.NOTES);
 *
 * // 3. CRUD 操作
 * const notes: Note[] = await noteStore.getAll();
 * await noteStore.save(newNote, (n) => n.id);
 * await noteStore.delete(noteId, (n) => n.id);
 * await noteStore.clear();
 *
 * // 4. 列出所有 key（调试用）
 * const keys: string[] = await noteStore.listKeys();
 *
 * ============================================================================
 * 错误处理
 * ============================================================================
 * 所有方法在内部捕获异常并通过 console.error 记录。
 * 读取失败时返回空数组，写入失败时静默跳过（避免数据丢失时阻塞 UI）。
 * 生产环境建议接入监控上报（如华为 AGC Crash）。
 * ============================================================================
 */

import preferences from '@ohos.data.preferences';
import { common } from '@kit.AbilityKit';
import { StorageKey } from './keys';

/** 内部 Preferences 单例 */
let _preferences: preferences.Preferences | null = null;

/** Preferences 数据文件名 */
const PREFERENCES_NAME = 'HarmonyStudioDB';

/**
 * 获取 Preferences 实例（懒初始化）
 */
async function getPreferences(): Promise<preferences.Preferences> {
  if (_preferences !== null) {
    return _preferences;
  }
  throw new Error('[StorageService] Preferences 未初始化，请先调用 StorageService.init(this.context)');
}

/**
 * 泛型存储服务类
 *
 * @template T - 存储数据项的类型，必须为 object（interface 类型）
 */
export class StorageService<T> {
  /** 当前实例对应的存储键 */
  private readonly key: string;

  /**
   * @param storeKey - 存储键名，建议使用 STORAGE_KEYS 常量
   */
  constructor(storeKey: StorageKey | string) {
    this.key = storeKey;
  }

  /**
   * 初始化 Preferences（应用启动时调用一次）
   *
   * @param context - UIAbility 上下文，通常在 EntryAbility.onWindowStageCreate() 中传入
   *
   * @example
   * // EntryAbility.ts
   * import { StorageService } from '../common/storage/storageService';
   * StorageService.init(this.context);
   */
  static async init(context: common.Context): Promise<void> {
    try {
      _preferences = await preferences.getPreferences(context, PREFERENCES_NAME);
      console.info('[StorageService] Preferences 初始化成功');
    } catch (err) {
      console.error('[StorageService] 初始化失败:', JSON.stringify(err));
    }
  }

  /**
   * 获取全部数据
   *
   * @returns 数据数组，若 key 不存在则返回空数组 []
   */
  async getAll(): Promise<T[]> {
    try {
      const pref = await getPreferences();
      const raw = await pref.get(this.key, '[]');
      const str = (raw as object).toString();
      return JSON.parse(str) as T[];
    } catch (err) {
      console.error(`[StorageService] getAll(${this.key}) 失败:`, JSON.stringify(err));
      return [];
    }
  }

  /**
   * 保存单条数据（存在则更新，不存在则追加）
   *
   * @param item - 要保存的数据项
   * @param getId - 获取 item 唯一标识的函数
   *
   * @example
   * await noteStore.save(newNote, (n: Note) => n.id);
   */
  async save(item: T, getId: (item: T) => string): Promise<void> {
    try {
      const pref = await getPreferences();
      const items = await this.getAll();
      const id = getId(item);

      // 查找是否存在同 ID 的记录
      const existingIndex = items.findIndex((i: T) => getId(i) === id);

      if (existingIndex >= 0) {
        // 更新已有记录
        items[existingIndex] = item;
      } else {
        // 追加新记录
        items.push(item);
      }

      await pref.put(this.key, JSON.stringify(items));
      await pref.flush();
    } catch (err) {
      console.error(`[StorageService] save(${this.key}) 失败:`, JSON.stringify(err));
    }
  }

  /**
   * 批量保存（替换整个数据集）
   *
   * @param items - 要保存的完整数据数组
   *
   * @example
   * await noteStore.saveAll(filteredNotes);
   */
  async saveAll(items: T[]): Promise<void> {
    try {
      const pref = await getPreferences();
      await pref.put(this.key, JSON.stringify(items));
      await pref.flush();
    } catch (err) {
      console.error(`[StorageService] saveAll(${this.key}) 失败:`, JSON.stringify(err));
    }
  }

  /**
   * 删除指定 ID 的数据
   *
   * @param id - 要删除的数据唯一标识
   * @param getId - 获取 item 唯一标识的函数
   *
   * @example
   * await noteStore.delete('1700000000000', (n: Note) => n.id);
   */
  async delete(id: string, getId: (item: T) => string): Promise<void> {
    try {
      const pref = await getPreferences();
      let items = await this.getAll();
      items = items.filter((i: T) => getId(i) !== id);
      await pref.put(this.key, JSON.stringify(items));
      await pref.flush();
    } catch (err) {
      console.error(`[StorageService] delete(${this.key}, ${id}) 失败:`, JSON.stringify(err));
    }
  }

  /**
   * 清空当前 key 的所有数据
   */
  async clear(): Promise<void> {
    try {
      const pref = await getPreferences();
      await pref.delete(this.key);
      await pref.flush();
    } catch (err) {
      console.error(`[StorageService] clear(${this.key}) 失败:`, JSON.stringify(err));
    }
  }

  /**
   * 列出 Preferences 中的所有存储键（调试用）
   *
   * @returns 所有已存储的 key 数组
   */
  static async listKeys(): Promise<string[]> {
    try {
      const pref = await getPreferences();
      // Preferences API 不直接提供 listKeys，这里通过已知 STORAGE_KEYS 遍历检查
      // 实际项目中可维护一个 meta key 记录所有已用 key
      const allKeys: string[] = [];
      // 尝试从 meta key 获取已记录的 key 列表
      const raw = await pref.get('__META_KEYS__', '[]');
      const str = (raw as object).toString();
      try {
        return JSON.parse(str) as string[];
      } catch {
        return allKeys;
      }
    } catch (err) {
      console.error('[StorageService] listKeys 失败:', JSON.stringify(err));
      return [];
    }
  }
}
