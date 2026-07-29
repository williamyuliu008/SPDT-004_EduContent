/**
 * 入境 APP · Debug 日志服务
 * 将调试信息写入本地文件，供开发者通过 hdc pull 读取
 */

import { fileIo } from '@kit.CoreFileKit';
import { application } from '@kit.AbilityKit';
import { util } from '@kit.ArkTS';

const LOG_FILE = 'debug.log';

function logFilePath(): string {
  try {
    const ctx = application.getApplicationContext();
    return ctx.filesDir + '/' + LOG_FILE;
  } catch (_) {
    return '/data/storage/el2/base/files/debug.log';
  }
}

export function dlog(tag: string, msg: string): void {
  try {
    const path = logFilePath();
    const ts = new Date().toISOString().substring(11, 23); // HH:mm:ss.SSS
    const line = ts + ' [' + tag + '] ' + msg + '\n';
    const f = fileIo.openSync(path, fileIo.OpenMode.CREATE | fileIo.OpenMode.APPEND);
    fileIo.writeSync(f.fd as number, line);
    fileIo.closeSync(f.fd as number);
  } catch (_) {}
}

export function dlogRead(): string {
  try {
    const path = logFilePath();
    const stat = fileIo.statSync(path);
    if (stat.size > 200 * 1024) {
      // 文件过大，清空
      fileIo.unlinkSync(path);
      return '(log cleared - was > 200KB)\n';
    }
    const f = fileIo.openSync(path, fileIo.OpenMode.READ_ONLY);
    const buf: ArrayBuffer = new ArrayBuffer(stat.size);
    fileIo.readSync(f.fd as number, buf);
    fileIo.closeSync(f.fd as number);
    const decoder: util.TextDecoder = util.TextDecoder.create('utf-8', { ignoreBOM: true });
    return decoder.decodeToString(new Uint8Array(buf));
  } catch (_) {
    return '(no log yet)\n';
  }
}

export function dlogClear(): void {
  try {
    const path = logFilePath();
    fileIo.unlinkSync(path);
  } catch (_) {}
}
