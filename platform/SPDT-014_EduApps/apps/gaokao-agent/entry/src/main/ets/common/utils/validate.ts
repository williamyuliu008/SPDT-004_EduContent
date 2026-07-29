/**
 * utils/validate.ts — 常用校验规则
 *
 * ============================================================================
 * 所有校验函数返回格式统一的 ValidationResult：
 *   { valid: boolean, message: string }
 * - valid=true  时 message 为空字符串
 * - valid=false 时 message 为中文错误提示
 *
 * 设计原则：
 *   1. 纯函数，无副作用，可在页面和工具类中直接调用
 *   2. 返回的错误提示可直接用于 HFormItem.errorMessage
 *   3. 校验规则覆盖常见场景：非空、长度、邮箱、手机号、URL、密码强度、数字范围
 * ============================================================================
 */

/** 校验结果类型 */
export interface ValidationResult {
  valid: boolean;
  message: string;
}

/** 快捷创建合法结果 */
function ok(): ValidationResult {
  return { valid: true, message: '' };
}

/** 快捷创建非法结果 */
function fail(message: string): ValidationResult {
  return { valid: false, message };
}

// ============================================================================
// 基础校验
// ============================================================================

/**
 * 非空校验（去除首尾空格后判断）
 *
 * @param value 待校验值
 * @param fieldName 字段名称（用于错误提示），如 '标题'
 * @returns ValidationResult
 *
 * @example
 * isNotEmpty('你好', '标题')  // → { valid: true, message: '' }
 * isNotEmpty('  ', '标题')   // → { valid: false, message: '标题不能为空' }
 * isNotEmpty('', '笔记内容') // → { valid: false, message: '笔记内容不能为空' }
 */
export function isNotEmpty(value: string, fieldName: string = '内容'): ValidationResult {
  if (!value || value.trim().length === 0) {
    return fail(`${fieldName}不能为空`);
  }
  return ok();
}

/**
 * 长度校验
 *
 * @param value 待校验值
 * @param min 最小长度
 * @param max 最大长度
 * @param fieldName 字段名称
 * @returns ValidationResult
 *
 * @example
 * lengthBetween('abc', 1, 10, '用户名')  // → valid
 * lengthBetween('a', 3, 10, '密码')      // → { valid: false, message: '密码长度需在3-10个字符之间' }
 */
export function lengthBetween(
  value: string,
  min: number,
  max: number,
  fieldName: string = '内容'
): ValidationResult {
  const len = (value ?? '').length;
  if (len < min) {
    return fail(`${fieldName}不能少于${min}个字符`);
  }
  if (len > max) {
    return fail(`${fieldName}不能超过${max}个字符`);
  }
  return ok();
}

// ============================================================================
// 格式校验
// ============================================================================

/** 邮箱正则 */
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * 邮箱格式校验
 *
 * @param email 待校验邮箱地址
 * @returns ValidationResult
 *
 * @example
 * isValidEmail('test@example.com')  // → valid
 * isValidEmail('not-email')         // → { valid: false, message: '邮箱格式不正确' }
 * isValidEmail('')                  // → { valid: false, message: '邮箱不能为空' }
 */
export function isValidEmail(email: string): ValidationResult {
  const empty = isNotEmpty(email, '邮箱');
  if (!empty.valid) {
    return empty;
  }
  if (!EMAIL_REGEX.test(email)) {
    return fail('邮箱格式不正确');
  }
  return ok();
}

/** 国内手机号正则（1开头的11位数字） */
const PHONE_REGEX = /^1[3-9]\d{9}$/;

/**
 * 手机号格式校验（中国大陆）
 *
 * @param phone 待校验手机号
 * @returns ValidationResult
 *
 * @example
 * isValidPhone('13800138000')  // → valid
 * isValidPhone('12345')        // → { valid: false, message: '手机号格式不正确' }
 */
export function isValidPhone(phone: string): ValidationResult {
  const empty = isNotEmpty(phone, '手机号');
  if (!empty.valid) {
    return empty;
  }
  if (!PHONE_REGEX.test(phone)) {
    return fail('手机号格式不正确');
  }
  return ok();
}

/** URL 正则 */
const URL_REGEX = /^https?:\/\/[^\s/$.?#].[^\s]*$/i;

/**
 * URL 格式校验
 *
 * @param url 待校验 URL
 * @returns ValidationResult
 */
export function isValidUrl(url: string): ValidationResult {
  const empty = isNotEmpty(url, '链接地址');
  if (!empty.valid) {
    return empty;
  }
  if (!URL_REGEX.test(url)) {
    return fail('链接格式不正确，需以 http:// 或 https:// 开头');
  }
  return ok();
}

// ============================================================================
// 业务校验
// ============================================================================

/**
 * 密码强度校验
 *
 * 规则：
 *   长度 ≥ 8
 *   包含至少一种大写字母
 *   包含至少一种小写字母
 *   包含至少一个数字
 *
 * @param password 待校验密码
 * @returns ValidationResult
 */
export function isStrongPassword(password: string): ValidationResult {
  const empty = isNotEmpty(password, '密码');
  if (!empty.valid) {
    return empty;
  }
  if (password.length < 8) {
    return fail('密码长度不能少于8位');
  }
  if (!/[A-Z]/.test(password)) {
    return fail('密码需包含至少一个大写字母');
  }
  if (!/[a-z]/.test(password)) {
    return fail('密码需包含至少一个小写字母');
  }
  if (!/[0-9]/.test(password)) {
    return fail('密码需包含至少一个数字');
  }
  return ok();
}

/**
 * 数字范围校验
 *
 * @param value 数字值
 * @param min 最小值
 * @param max 最大值
 * @param fieldName 字段名称
 * @returns ValidationResult
 *
 * @example
 * numberInRange(5, 1, 10, '评分')      // → valid
 * numberInRange(0, 1, 10, '评分')      // → { valid: false, message: '评分不能小于1' }
 */
export function numberInRange(
  value: number,
  min: number,
  max: number,
  fieldName: string = '数值'
): ValidationResult {
  if (!isFinite(value)) {
    return fail(`${fieldName}必须是有效数字`);
  }
  if (value < min) {
    return fail(`${fieldName}不能小于${min}`);
  }
  if (value > max) {
    return fail(`${fieldName}不能大于${max}`);
  }
  return ok();
}

// ============================================================================
// 组合校验工具
// ============================================================================

/**
 * 执行多个校验器，返回第一个失败的结果
 *
 * @param value 待校验值
 * @param validators 校验器数组
 * @returns 第一个失败的 ValidationResult，或 ok()
 *
 * @example
 * validateAll(this.email, [
 *   (v) => isNotEmpty(v, '邮箱'),
 *   (v) => isValidEmail(v),
 * ])
 */
export function validateAll(
  value: string,
  validators: ((value: string) => ValidationResult)[]
): ValidationResult {
  for (const validator of validators) {
    const result = validator(value);
    if (!result.valid) {
      return result;
    }
  }
  return ok();
}
