// ============================================================
// model/FileParser.ets — TXT/Markdown 文件解析器
// ============================================================

import { Chapter } from './ReaderModel';
import fileFs from '@ohos.file.fs';
import util from '@ohos.util';
import { BusinessError } from '@kit.BasicServicesKit';

/**
 * 文件解析器：负责读取文本文件、识别章节
 */
export class FileParser {
  /** 全文内容缓存 */
  private contentCache: Map<string, string> = new Map();

  /**
   * 读取文件全文
   */
  async readFileText(fileUri: string): Promise<string> {
    // 检查缓存
    let cached = this.contentCache.get(fileUri);
    if (cached !== undefined) {
      return cached;
    }

    try {
      let file = fileFs.openSync(fileUri, fileFs.OpenMode.READ_ONLY);
      let stat = fileFs.statSync(fileUri);
      let bufSize = stat.size;
      let arrayBuffer = new ArrayBuffer(bufSize);
      let readLen = fileFs.readSync(file.fd, arrayBuffer);
      fileFs.closeSync(file);

      // 转文本（尝试 UTF-8，失败则 GBK）
      let text = this.decodeBuffer(arrayBuffer, readLen);
      this.contentCache.set(fileUri, text);
      return text;
    } catch (err) {
      let e = err as BusinessError;
      console.error('[FileParser] 读取文件失败:', e.message);
      return '';
    }
  }

  /**
   * 解析章节（基于 Markdown 标题 # / TXT 章节标记）
   */
  parseChapters(fullText: string): Chapter[] {
    let chapters: Chapter[] = [];
    let lines = fullText.split(/\r?\n/);

    // 正则：匹配 Markdown 标题 (#, ##, ###) 或 TXT 章节标记
    let mdHeader = /^(#{1,3})\s+(.+)/;
    let txtChapter = /^(第[一二三四五六七八九十百千\d]+[章节卷部篇回]|Chapter\s*\d+|CH\d+)\s*[：:\s]?(.*)/i;
    let txtSection = /^(【.+】|\[.+\]|（.+）).*/;
    let txtNumber = /^(\d+[\.\、\)）]\s*.+)/;

    let lastChapterStart = 0;
    let chapterIndex = 0;

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i].trim();
      if (line.length === 0) {
        continue;
      }

      let isHeader = false;
      let title = '';
      let level = 1;

      // 1. Markdown 标题检测
      let mdMatch = line.match(mdHeader);
      if (mdMatch !== null) {
        isHeader = true;
        level = mdMatch[1]!.length;
        title = mdMatch[2]!.trim();
      }

      // 2. TXT 章节/卷/部/篇检测
      if (!isHeader) {
        let txtMatch = line.match(txtChapter);
        if (txtMatch !== null) {
          isHeader = true;
          title = txtMatch[0]!.trim();
        }
      }

      // 3. 中文标记检测
      if (!isHeader) {
        let secMatch = line.match(txtSection);
        if (secMatch !== null && secMatch[0]!.length <= 30) {
          isHeader = true;
          title = secMatch[1]!.trim();
        }
      }

      // 4. 数字序号 + 文本（如 "一、序言" 或 "1. Introduction"）
      if (!isHeader) {
        let numMatch = line.match(txtNumber);
        if (numMatch !== null && numMatch[1]!.length <= 25) {
          isHeader = true;
          title = numMatch[1]!.trim();
        }
      }

      if (isHeader && title.length > 0) {
        // 计算本行在全文字符串中的起始位置
        let charStart = this.getLineCharStart(fullText, lines, i);

        // 结束前一章节
        if (chapters.length > 0) {
          chapters[chapters.length - 1].endChar = charStart - 1;
        }

        // 如果第一个章节不在开头，添加一个"前言"章节
        if (chapters.length === 0 && charStart > 0) {
          chapters.push(new Chapter(chapterIndex, '前言', 0, charStart - 1, 0));
          chapterIndex++;
        }

        chapters.push(new Chapter(chapterIndex, title, charStart, fullText.length, level));
        chapterIndex++;
        lastChapterStart = charStart;
      }
    }

    // 如果没有识别到任何章节，将全文作为一个章节
    if (chapters.length === 0 && fullText.length > 0) {
      chapters.push(new Chapter(0, '正文', 0, fullText.length, 0));
    }

    // 修正最后一个章节的 endChar
    if (chapters.length > 0) {
      chapters[chapters.length - 1].endChar = fullText.length;
    }

    return chapters;
  }

  /**
   * 获取指定行在全文中的字符起始位置
   */
  private getLineCharStart(fullText: string, lines: string[], lineIndex: number): number {
    let pos = 0;
    for (let i = 0; i < lineIndex; i++) {
      pos += lines[i]!.length + 1; // +1 for \n
    }
    return pos;
  }

  /**
   * Buffer 解码为文本
   */
  private decodeBuffer(arrayBuffer: ArrayBuffer, byteLength: number): string {
    // 尝试 UTF-8
    try {
      let textDecoder = new util.TextDecoder('utf-8', { fatal: false });
      let uint8 = new Uint8Array(arrayBuffer, 0, byteLength);
      let text = textDecoder.decodeToString(uint8, { stream: false });
      // 检查是否有乱码标记（替换字符过多）
      let replacementCount = (text.match(/\uFFFD/g) || []).length;
      if (replacementCount < text.length * 0.05) {
        return text;
      }
    } catch (e) {
      // UTF-8 失败，尝试 GBK
    }
    // 尝试 GBK/GB2312
    try {
      let textDecoder = new util.TextDecoder('gbk', { fatal: false });
      let uint8 = new Uint8Array(arrayBuffer, 0, byteLength);
      return textDecoder.decodeToString(uint8, { stream: false });
    } catch (e) {
      // 最后兜底：二进制转文本
      return this.fallbackDecode(arrayBuffer, byteLength);
    }
  }

  private fallbackDecode(arrayBuffer: ArrayBuffer, byteLength: number): string {
    let uint8 = new Uint8Array(arrayBuffer, 0, byteLength);
    let result = '';
    for (let i = 0; i < byteLength; i++) {
      result += String.fromCharCode(uint8[i]!);
    }
    return result;
  }

  /**
   * 提取文件标题（从文件名或首行）
   */
  extractTitle(fileUri: string, firstLine: string): string {
    // 从 URI 提取文件名
    let parts = fileUri.split('/');
    let fileName = parts[parts.length - 1] || '未命名';
    // 去掉扩展名
    let dotIdx = fileName.lastIndexOf('.');
    if (dotIdx > 0) {
      fileName = fileName.substring(0, dotIdx);
    }

    // 如果首行可能是标题（短且没有标点），使用首行
    let cleanFirst = firstLine.replace(/^[#\s]+/, '').trim();
    if (cleanFirst.length > 0 && cleanFirst.length < 50) {
      return cleanFirst;
    }

    return fileName;
  }

  /**
   * 清理缓存
   */
  clearCache(fileUri?: string): void {
    if (fileUri) {
      this.contentCache.delete(fileUri);
    } else {
      this.contentCache.clear();
    }
  }
}
