/**
 * agent/EnvAwareness.ets — H 维度：环境感知
 *
 * 职责：电池状态监控 + 后台同步控制
 * Phase 1A: 地基 · 使用 HarmonyOS batteryInfo SDK
 */

import batteryInfo from '@ohos.batteryInfo';
import { DeviceEnv } from './types';

export class EnvAwareness {
  private lowBatteryCallback: (() => void) | null = null;

  // ============================================================
  // 电池状态
  // ============================================================

  getBatteryLevel(): number {
    try {
      return Math.round(batteryInfo.batterySOC * 100);
    } catch {
      return 100; // 模拟器/无电池设备默认满电
    }
  }

  isCharging(): boolean {
    try {
      return batteryInfo.chargingStatus !== 0; // 0 = NONE
    } catch {
      return true;
    }
  }

  /**
   * 是否应该暂停后台同步
   * 规则：电量 <20% 且未充电
   */
  shouldThrottleSync(): boolean {
    return this.getBatteryLevel() < 20 && !this.isCharging();
  }

  /**
   * 获取当前设备环境快照
   */
  getSnapshot(): DeviceEnv {
    return {
      batteryLevel: this.getBatteryLevel(),
      batteryCharging: this.isCharging(),
      networkType: 'wifi', // TODO: 后续接入 @ohos.net.connection
      screenOn: true
    };
  }

  // ============================================================
  // 回调
  // ============================================================

  /**
   * 注册低电量回调
   * 当电量低于20%且未充电时触发
   */
  onLowBattery(callback: () => void): void {
    this.lowBatteryCallback = callback;
  }

  /**
   * 检查并触发低电量回调
   * 建议在定时器或用户操作后调用
   */
  checkAndNotify(): void {
    if (this.shouldThrottleSync() && this.lowBatteryCallback !== null) {
      this.lowBatteryCallback();
    }
  }

  /**
   * 电池状态友好文本
   */
  getBatteryStatusText(): string {
    const level = this.getBatteryLevel();
    if (this.isCharging()) return `充电中 ${level}%`;
    if (level < 10) return `电量极低 ${level}%`;
    if (level < 20) return `电量低 ${level}%`;
    return `${level}%`;
  }
}
