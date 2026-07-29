// ============================================================
// model/OHPMLibrary.ets — OHPM 三方库数据模型
// ============================================================

/** OHPM 三方库 */
export class OHPMLibrary {
  id: string;
  name: string;
  category: string;
  description: string;
  author: string;
  stars: number;
  version: string;
  downloads: string;
  ohpmInstall: string;
  officialUrl: string;
  tags: string[];
  favorite: boolean;

  constructor(
    id: string, name: string, category: string, description: string,
    author: string, stars: number, version: string, downloads: string,
    ohpmInstall: string, officialUrl: string, tags: string[]
  ) {
    this.id = id;
    this.name = name;
    this.category = category;
    this.description = description;
    this.author = author;
    this.stars = stars;
    this.version = version;
    this.downloads = downloads;
    this.ohpmInstall = ohpmInstall;
    this.officialUrl = officialUrl;
    this.tags = tags;
    this.favorite = false;
  }
}

/** 库分类 */
export const CATEGORIES: string[] = [
  '全部',
  '网络请求',
  '数据存储',
  'UI组件',
  '图片处理',
  '音视频',
  '工具库',
  '状态管理',
  '安全加密',
  '测试调试',
];

/** 所有 OHPM 三方库数据 */
export function getAllLibraries(): OHPMLibrary[] {
  return [
    // ---- 网络请求 ----
    new OHPMLibrary(
      'lib_axios', '@ohos/axios', '网络请求',
      '基于 Axios 的鸿蒙 HTTP 网络请求库，支持请求/响应拦截器、并发请求、取消请求等特性。',
      'OpenHarmony SIG', 5200, '2.0.2', '12.5万+',
      'ohpm install @ohos/axios',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Faxios',
      ['HTTP', '网络', '请求', 'Axios']
    ),
    new OHPMLibrary(
      'lib_retrofit', '@ohos/retrofit', '网络请求',
      '鸿蒙版 Retrofit，声明式 HTTP 客户端，支持注解风格的 API 定义。',
      'OpenHarmony SIG', 1800, '1.0.0', '4.3万+',
      'ohpm install @ohos/retrofit',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fretrofit',
      ['HTTP', 'REST', '注解', 'Retrofit']
    ),
    new OHPMLibrary(
      'lib_websocket', '@ohos/websocket', '网络请求',
      'WebSocket 连接库，支持长连接、自动重连、心跳检测。',
      'OpenHarmony SIG', 890, '1.2.0', '3.1万+',
      'ohpm install @ohos/websocket',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fwebsocket',
      ['WebSocket', '长连接', '实时通讯', '推送']
    ),
    // ---- 数据存储 ----
    new OHPMLibrary(
      'lib_preferences', '@ohos/data-preferences', '数据存储',
      '轻量级键值对存储库，适用于应用配置和用户偏好设置。',
      'OpenHarmony SIG', 3200, '1.1.0', '18.2万+',
      'ohpm install @ohos/data-preferences',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fdata-preferences',
      ['存储', '配置', '键值对', '本地']
    ),
    new OHPMLibrary(
      'lib_sqlite', '@ohos/sqlite-adapter', '数据存储',
      'SQLite 数据库适配器，封装了关系型数据库的常用操作。',
      'OpenHarmony SIG', 2100, '1.0.3', '9.8万+',
      'ohpm install @ohos/sqlite-adapter',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fsqlite-adapter',
      ['数据库', 'SQLite', 'ORM', '本地存储']
    ),
    new OHPMLibrary(
      'lib_mmkv', '@tencent/mmkv', '数据存储',
      '腾讯开源的高性能 KV 存储库 MMKV 的鸿蒙移植版，基于 mmap 实现极速读写。',
      'Tencent', 4100, '2.0.0', '15.6万+',
      'ohpm install @tencent/mmkv',
      'https://ohpm.openharmony.cn/#/cn/detail/@tencent%2Fmmkv',
      ['KV存储', '高性能', 'mmap', '腾讯']
    ),
    // ---- UI组件 ----
    new OHPMLibrary(
      'lib_lottie', '@ohos/lottie', 'UI组件',
      'Lottie 动画库，支持 AE 导出的 JSON 动画在鸿蒙上播放。',
      'OpenHarmony SIG', 6700, '2.0.1', '28.3万+',
      'ohpm install @ohos/lottie',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Flottie',
      ['动画', 'Lottie', '动效', 'AE']
    ),
    new OHPMLibrary(
      'lib_swiper_indicator', '@ohos/swiper-indicator', 'UI组件',
      '轮播指示器组件，支持多种样式和自定义配置。',
      'OpenHarmony SIG', 1200, '1.1.0', '6.5万+',
      'ohpm install @ohos/swiper-indicator',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fswiper-indicator',
      ['轮播', '指示器', 'Swiper', 'UI']
    ),
    new OHPMLibrary(
      'lib_pulltorefresh', '@ohos/pull-to-refresh', 'UI组件',
      '下拉刷新和上拉加载更多组件，支持自定义刷新头部和底部。',
      'OpenHarmony SIG', 2800, '2.1.0', '11.7万+',
      'ohpm install @ohos/pull-to-refresh',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fpull-to-refresh',
      ['下拉刷新', '上拉加载', '列表', 'UI']
    ),
    new OHPMLibrary(
      'lib_chart', '@ohos/chart', 'UI组件',
      '图表组件库，支持折线图、柱状图、饼图、雷达图等多种图表类型。',
      'OpenHarmony SIG', 3500, '2.0.0', '16.8万+',
      'ohpm install @ohos/chart',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fchart',
      ['图表', '可视化', '折线图', '柱状图']
    ),
    new OHPMLibrary(
      'lib_calendar', '@ohos/calendar-kit', 'UI组件',
      '日历组件，支持月视图、周视图、日程标记和日期选择。',
      '社区开发者', 950, '1.3.2', '4.2万+',
      'ohpm install @ohos/calendar-kit',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fcalendar-kit',
      ['日历', '日期', '日程', '选择器']
    ),
    // ---- 图片处理 ----
    new OHPMLibrary(
      'lib_glide', '@ohos/glide', '图片处理',
      '图片加载和缓存库，灵感来自 Android Glide，支持网络/本地图片加载、缓存策略、变换处理。',
      'OpenHarmony SIG', 4800, '1.2.0', '22.1万+',
      'ohpm install @ohos/glide',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fglide',
      ['图片加载', '缓存', 'Glide', '图片处理']
    ),
    new OHPMLibrary(
      'lib_image_cropper', '@ohos/image-cropper', '图片处理',
      '图片裁剪组件，支持自由裁剪、固定比例裁剪、旋转和缩放。',
      '社区开发者', 760, '1.0.2', '3.4万+',
      'ohpm install @ohos/image-cropper',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fimage-cropper',
      ['图片裁剪', '头像', '编辑', '选择']
    ),
    new OHPMLibrary(
      'lib_qrcode', '@ohos/qr-code', '图片处理',
      '二维码生成和扫描库，支持多种编码格式和自定义样式。',
      'OpenHarmony SIG', 1900, '2.1.0', '8.9万+',
      'ohpm install @ohos/qr-code',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fqr-code',
      ['二维码', '扫码', 'QR码', '识别']
    ),
    // ---- 音视频 ----
    new OHPMLibrary(
      'lib_video_player', '@ohos/video-player', '音视频',
      '视频播放器组件，封装了 AVPlayer，支持全屏、倍速、手势控制。',
      'OpenHarmony SIG', 2100, '1.5.0', '13.6万+',
      'ohpm install @ohos/video-player',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fvideo-player',
      ['视频', '播放器', 'AVPlayer', '全屏']
    ),
    new OHPMLibrary(
      'lib_audio_recorder', '@ohos/audio-recorder', '音视频',
      '音频录制库，支持多种格式录制、降噪、音量检测。',
      '社区开发者', 630, '1.0.1', '2.8万+',
      'ohpm install @ohos/audio-recorder',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Faudio-recorder',
      ['音频', '录制', '录音', 'Media']
    ),
    // ---- 工具库 ----
    new OHPMLibrary(
      'lib_util', '@ohos/util', '工具库',
      '通用工具库，包含日期格式化、字符串处理、数字计算等常用工具函数。',
      'OpenHarmony SIG', 5600, '2.3.0', '35.2万+',
      'ohpm install @ohos/util',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Futil',
      ['工具', '日期', '字符串', '常用']
    ),
    new OHPMLibrary(
      'lib_crypto', '@ohos/crypto-js', '工具库',
      '加密解密工具库，支持 AES、RSA、MD5、SHA 等常见算法。',
      'OpenHarmony SIG', 1500, '1.2.0', '7.5万+',
      'ohpm install @ohos/crypto-js',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fcrypto-js',
      ['加密', '解密', 'AES', 'MD5']
    ),
    new OHPMLibrary(
      'lib_json', '@ohos/json-bigint', '工具库',
      'JSON 解析增强库，支持大整数、自定义序列化和反序列化。',
      '社区开发者', 420, '1.0.0', '1.8万+',
      'ohpm install @ohos/json-bigint',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fjson-bigint',
      ['JSON', '序列化', '解析', '大整数']
    ),
    // ---- 状态管理 ----
    new OHPMLibrary(
      'lib_redux', '@ohos/redux', '状态管理',
      'Redux 状态管理鸿蒙适配版，支持单向数据流和中间件机制。',
      'OpenHarmony SIG', 2300, '1.1.0', '10.4万+',
      'ohpm install @ohos/redux',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fredux',
      ['Redux', '状态管理', '数据流', '中间件']
    ),
    new OHPMLibrary(
      'lib_eventbus', '@ohos/eventbus', '状态管理',
      '事件总线库，用于跨组件和跨页面的通信，支持粘性事件。',
      '社区开发者', 1100, '1.0.1', '5.3万+',
      'ohpm install @ohos/eventbus',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Feventbus',
      ['事件总线', '通信', '跨组件', 'EventBus']
    ),
    // ---- 安全加密 ----
    new OHPMLibrary(
      'lib_security', '@ohos/security-kit', '安全加密',
      '安全工具集，提供设备指纹、安全存储、应用签名校验等功能。',
      'OpenHarmony SIG', 980, '1.0.0', '4.1万+',
      'ohpm install @ohos/security-kit',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fsecurity-kit',
      ['安全', '加密', '存储', '签名']
    ),
    // ---- 测试调试 ----
    new OHPMLibrary(
      'lib_logger', '@ohos/logger', '测试调试',
      '日志库，支持分级日志、文件输出、日志加密和远程上报。',
      'OpenHarmony SIG', 1600, '1.1.2', '8.6万+',
      'ohpm install @ohos/logger',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Flogger',
      ['日志', '调试', '输出', '上报']
    ),
    new OHPMLibrary(
      'lib_mock', '@ohos/mock-server', '测试调试',
      'Mock 服务库，用于模拟后端 API 响应，加速前端开发和测试。',
      '社区开发者', 550, '1.0.0', '2.2万+',
      'ohpm install @ohos/mock-server',
      'https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fmock-server',
      ['Mock', '测试', 'API', '模拟']
    ),
  ];
}

/** 根据分类筛选 */
export function filterByCategory(libs: OHPMLibrary[], category: string): OHPMLibrary[] {
  if (category === '全部') {
    return libs;
  }
  return libs.filter((l: OHPMLibrary) => l.category === category);
}

/** 根据关键词搜索 */
export function searchLibraries(libs: OHPMLibrary[], keyword: string): OHPMLibrary[] {
  if (!keyword || keyword.trim() === '') {
    return libs;
  }
  let kw = keyword.toLowerCase();
  return libs.filter((l: OHPMLibrary) =>
    l.name.toLowerCase().includes(kw) ||
    l.description.toLowerCase().includes(kw) ||
    l.tags.some((t: string) => t.toLowerCase().includes(kw)) ||
    l.author.toLowerCase().includes(kw)
  );
}
