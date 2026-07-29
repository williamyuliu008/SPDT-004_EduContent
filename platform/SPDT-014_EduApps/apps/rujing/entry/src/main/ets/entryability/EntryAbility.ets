import { UIAbility, Want, AbilityConstant } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { window } from '@kit.ArkUI';
import { db } from '../service/DatabaseService';
import { ai } from '../service/AIService';
import { util } from '@kit.ArkTS';

const DOMAIN = 0x0000;
const TAG = 'rujing';

export default class EntryAbility extends UIAbility {
  async onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): Promise<void> {
    hilog.info(DOMAIN, TAG, 'Ability onCreate');

    // 初始化数据库
    try {
      await db.initialize(this.context);
      hilog.info(DOMAIN, TAG, 'Database initialized');
      // 数据迁移：链归属学科修正（历史 → 古诗文/书法）
      await db.migrateSubjectOwnership();
    } catch (e) {
      hilog.error(DOMAIN, TAG, 'Database init failed: %{public}s', JSON.stringify(e));
    }

    // 初始化 AI 服务
    try {
      const rm = this.context.resourceManager;
      const rawData: Uint8Array = await rm.getRawFileContent('zhipu_api.txt');
      const decoder: util.TextDecoder = util.TextDecoder.create('utf-8', { ignoreBOM: true });
      let apiKey: string = decoder.decodeToString(rawData).trim();

      // 去掉占位文本
      if (!apiKey || apiKey.includes('YOUR_') || apiKey.includes('HERE')) {
        hilog.warn(DOMAIN, TAG, 'API key not configured, AI features disabled');
      } else {
        ai.setBackend({
          name: 'zhipu',
          apiUrl: 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
          apiKey: apiKey,
          model: 'glm-4-flash',
          enabled: true
        });
        hilog.info(DOMAIN, TAG, 'AI service initialized with GLM-4-Flash');
      }
    } catch (e) {
      hilog.warn(DOMAIN, TAG, 'AI init skipped: %{public}s', JSON.stringify(e));
    }
  }

  onDestroy(): void {
    hilog.info(DOMAIN, TAG, '%{public}s', 'Ability onDestroy');
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    hilog.info(DOMAIN, TAG, '%{public}s', 'Ability onWindowStageCreate');
    windowStage.loadContent('pages/Index', (err) => {
      if (err.code) {
        hilog.error(DOMAIN, TAG, 'Failed to load content. Cause: %{public}s', JSON.stringify(err));
        return;
      }
      hilog.info(DOMAIN, TAG, 'Succeeded in loading content.');
    });
  }

  onWindowStageDestroy(): void {
    hilog.info(DOMAIN, TAG, '%{public}s', 'Ability onWindowStageDestroy');
  }

  onForeground(): void {
    hilog.info(DOMAIN, TAG, '%{public}s', 'Ability onForeground');
  }

  onBackground(): void {
    hilog.info(DOMAIN, TAG, '%{public}s', 'Ability onBackground');
  }
}
