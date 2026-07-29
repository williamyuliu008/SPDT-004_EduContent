// ============================================================
// common/index.ets — 通用层统一导出
// ============================================================

export { generateId, shortId } from './utils/id';

export { StorageService } from './storage/storageService';
export { STORAGE_KEYS } from './storage/keys';

export {
  ThemeTokens,
  ShadowOptions,
  lightTheme,
  darkTheme,
  eyeCareTheme,
  autoTheme,
  ALL_THEMES,
  ALL_THEME_NAMES,
} from './theme/tokens';
