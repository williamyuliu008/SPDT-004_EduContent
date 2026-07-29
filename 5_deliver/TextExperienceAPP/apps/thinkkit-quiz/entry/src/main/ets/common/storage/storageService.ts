/**
 * storage/storageService.ts — 基于 Preferences 的泛型 CRUD 封装
 *
 * ============================================================================
 * 设计理念
 * ============================================================================
 * 1. 泛型支持：同一套代码可存储任意数据类型
 * 2. 零后端依赖：纯本地 Preferences 操作
 * 3. 错误友好：所有方法内置 try/catch
 * 4. 单例初始化：Preferences 实例只创建一次
 * ============================================================================
 */

import preferences from '@ohos.data.preferences';
import { common } from '@kit.AbilityKit';
import { StorageKey } from './keys';

let _preferences: preferences.Preferences | null = null;
const PREFERENCES_NAME = 'ThinkKitQuizDB';

async function getPreferences(): Promise<preferences.Preferences> {
  if (_preferences !== null) {
    return _preferences;
  }
  throw new Error('[StorageService] Preferences 未初始化，请先调用 StorageService.init(this.context)');
}

export class StorageService<T> {
  private readonly key: string;

  constructor(storeKey: StorageKey | string) {
    this.key = storeKey;
  }

  static async init(context: common.Context): Promise<void> {
    try {
      _preferences = await preferences.getPreferences(context, PREFERENCES_NAME);
      console.info('[StorageService] Preferences 初始化成功');
    } catch (err) {
      console.error('[StorageService] 初始化失败:', JSON.stringify(err));
    }
  }

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

  async save(item: T, getId: (item: T) => string): Promise<void> {
    try {
      const pref = await getPreferences();
      const items = await this.getAll();
      const id = getId(item);
      const existingIndex = items.findIndex((i: T) => getId(i) === id);
      if (existingIndex >= 0) {
        items[existingIndex] = item;
      } else {
        items.push(item);
      }
      await pref.put(this.key, JSON.stringify(items));
      await pref.flush();
    } catch (err) {
      console.error(`[StorageService] save(${this.key}) 失败:`, JSON.stringify(err));
    }
  }

  async saveAll(items: T[]): Promise<void> {
    try {
      const pref = await getPreferences();
      await pref.put(this.key, JSON.stringify(items));
      await pref.flush();
    } catch (err) {
      console.error(`[StorageService] saveAll(${this.key}) 失败:`, JSON.stringify(err));
    }
  }

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

  async clear(): Promise<void> {
    try {
      const pref = await getPreferences();
      await pref.delete(this.key);
      await pref.flush();
    } catch (err) {
      console.error(`[StorageService] clear(${this.key}) 失败:`, JSON.stringify(err));
    }
  }
}
