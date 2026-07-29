/**
 * agent/ContentPipeline.ets — E 维度：内容管道
 * JSON解析 + 格式验证 + 入库管理
 */

import { StorageService } from '../storage/storageService';
import { STORAGE_KEYS } from '../storage/keys';

export interface ContentManifest {
  version: string
  updatedAt: string
  domains: string[]
  contentTypes: string[]
  itemCounts: Record<string, number>
  checksum: string
}

export interface ImportResult {
  importedCount: number
  skippedCount: number
  errorCount: number
  errors: ImportError[]
}

export interface ImportError {
  index: number
  message: string
}

export class ContentPipeline {
  private manifestStore: StorageService<ContentManifest>;

  constructor() {
    this.manifestStore = new StorageService<ContentManifest>(STORAGE_KEYS.CONTENT_MANIFEST);
  }

  importQuestions(questions: ESObject[]): ImportResult {
    const result: ImportResult = { importedCount: 0, skippedCount: 0, errorCount: 0, errors: [] };

    for (let i = 0; i < questions.length; i++) {
      const q: ESObject = questions[i];
      let hasId = false;
      let hasText = false;
      let hasOptions = false;
      let hasAnswer = false;

      if (q['id'] !== undefined && typeof q['id'] === 'string') hasId = true;
      if (q['text'] !== undefined && typeof q['text'] === 'string') hasText = true;
      if (q['options'] !== undefined && Array.isArray(q['options'])) hasOptions = true;
      if (q['answer'] !== undefined && typeof q['answer'] === 'number') hasAnswer = true;

      if (hasId && hasText && hasOptions && hasAnswer) {
        result.importedCount++;
      } else {
        result.errorCount++;
        const err: ImportError = { index: i, message: '格式错误' };
        result.errors.push(err);
      }
    }

    return result;
  }

  async getManifest(): Promise<ContentManifest | null> {
    const manifests = await this.manifestStore.getAll();
    return manifests.length > 0 ? manifests[0] : null;
  }

  async updateManifest(manifest: ContentManifest): Promise<void> {
    await this.manifestStore.save(manifest, (m: ContentManifest): string => 'current');
  }
}
