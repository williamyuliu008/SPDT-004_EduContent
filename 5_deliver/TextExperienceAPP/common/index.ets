/**
 * common/index.ets — 统一导出入口
 *
 * 一次性导入所有 common 模块，供 App 页面使用：
 *
 * @example
 * import { HButton, HCard, StorageService, generateId, lightTheme } from '../common';
 *
 * ============================================================================
 * 维护规则：
 *   - 新增 common 模块时，在此文件中添加对应的 export 语句
 *   - 按类别分组：Components / Storage / Theme / Utils / Algo
 *   - 只导出公开 API，内部实现不导出
 * ============================================================================
 */

// ---- Components ----
export { HButton } from './components/HButton';
export type { HButtonProps, ButtonType, ButtonSize } from './components/HButton';

export { HCard } from './components/HCard';
export type { HCardSwipeConfig } from './components/HCard';

export { HEmptyState } from './components/HEmptyState';

export { HFormItem } from './components/HFormItem';
export type { FormFieldType } from './components/HFormItem';

export { HProgressBar } from './components/HProgressBar';
export type { ProgressBarType, LabelFormat } from './components/HProgressBar';

export { HToast } from './components/HToast';
export type { HToastConfig, ToastType, ToastPosition } from './components/HToast';

export { HNavBar } from './components/HNavBar';
export type { NavBarAction } from './components/HNavBar';

export { HSearchBar } from './components/HSearchBar';

export { HConfirmDialog } from './components/HConfirmDialog';
export type { HConfirmDialogConfig } from './components/HConfirmDialog';

export { HTag } from './components/HTag';
export type { HTagSize } from './components/HTag';

export { HTagGroup } from './components/HTagGroup';
export type { TagItem } from './components/HTagGroup';

export { HFAB } from './components/HFAB';
export type { FABPosition } from './components/HFAB';

// ---- Storage ----
export { StorageService } from './storage/storageService';
export { STORAGE_KEYS } from './storage/keys';
export type { StorageKey } from './storage/keys';

// ---- Theme ----
export { lightTheme, darkTheme, eyeCareTheme, autoTheme, ALL_THEMES, ALL_THEME_NAMES } from './theme/tokens';
export type { ThemeTokens, ShadowOptions } from './theme/tokens';

// ---- Utils ----
export { formatDate, timeAgo, getWeekday, isSameDay, getWeekRange, daysBetween, daysInMonth } from './utils/date';
export { formatNumber, formatCurrency, formatPercent, formatFileSize, formatDuration, abbreviateNumber, padZero } from './utils/format';
export { isNotEmpty, lengthBetween, isValidEmail, isValidPhone, isValidUrl, isStrongPassword, numberInRange, validateAll } from './utils/validate';
export type { ValidationResult } from './utils/validate';
export { generateId, shortId } from './utils/id';
export { debounce, throttle } from './utils/debounce';

// ---- Algo ----
export { SM2, SM2Quality } from './algo/sm2';
export type { SM2Card, SM2Stats } from './algo/sm2';
export { StreakCalculator } from './algo/streak';
export type { StreakResult } from './algo/streak';
