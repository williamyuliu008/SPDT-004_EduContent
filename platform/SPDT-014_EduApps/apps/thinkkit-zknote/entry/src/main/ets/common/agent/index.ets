/**
 * common/agent-core/index.ets — 智能体公共模块统一导出
 *
 * 用法:
 *   import { AgentEngine } from 'common/agent-core';
 *   const agent = new AgentEngine({ appId: 'my-app', ... });
 */

export { AgentEngine, AgentConfig, AgentDimension } from './AgentEngine';
export { AgentProfile } from './AgentProfile';
export { IntentContext } from './IntentContext';
export { InputAssist, ColdStartQuestion, ColdStartProgress } from './InputAssist';
export { OutputAction, RISK_MATRIX } from './OutputAction';
export { ContentPipeline, ContentManifest, ImportResult } from './ContentPipeline';
export { LobsterClient } from './LobsterClient';
export { EnvAwareness } from './EnvAwareness';
export { UndoManager } from './UndoManager';
export * from './types';
