/**
 * agent/UndoManager.ets — I 维度：撤销管理
 *
 * 3分钟时间窗口，支持撤销近期操作
 */

import { UndoableAction } from './types';

const UNDO_WINDOW_MS = 3 * 60 * 1000; // 3分钟

export class UndoManager {
  private actions: UndoableAction[] = [];

  recordAction(type: string, payload: ESObject): string {
    const now = new Date().toISOString();
    const id = 'undo_' + Date.now().toString();

    const action: UndoableAction = {
      id: id,
      type: type,
      payload: payload,
      timestamp: now,
      expiresAt: new Date(Date.now() + UNDO_WINDOW_MS).toISOString()
    };

    this.actions.push(action);
    this.clearExpired();
    return id;
  }

  getUndoableActions(): UndoableAction[] {
    this.clearExpired();
    return this.actions.slice();
  }

  canUndo(actionId: string): boolean {
    this.clearExpired();
    for (let i = 0; i < this.actions.length; i++) {
      if (this.actions[i].id === actionId) return true;
    }
    return false;
  }

  getLastAction(): UndoableAction | null {
    this.clearExpired();
    if (this.actions.length === 0) return null;
    return this.actions[this.actions.length - 1];
  }

  clearExpired(): void {
    const now = Date.now();
    const valid: UndoableAction[] = [];
    for (let i = 0; i < this.actions.length; i++) {
      if (new Date(this.actions[i].expiresAt).getTime() > now) {
        valid.push(this.actions[i]);
      }
    }
    this.actions = valid;
  }

  getCount(): number {
    this.clearExpired();
    return this.actions.length;
  }
}
