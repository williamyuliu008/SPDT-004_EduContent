/**
 * 入境 APP · 数据库服务
 * 基于 RDB（关系型数据库）存储卡片元数据
 * 链叙事文本使用文件系统存储
 */

import { relationalStore } from '@kit.ArkData';
import { Context } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { Card, Chain, Maturity, CardType, Subject, ChainType, ChatRecord, DashboardCounts, ChainRole } from '../model/DataModel';

const DOMAIN = 0x0000;
const TAG = 'DatabaseService';

const DB_NAME = 'rujing.db';
const DB_VERSION = 1;

// ─── SQL 建表 ───────────────────────────────────────

const SQL_CREATE_CARDS = `
  CREATE TABLE IF NOT EXISTS cards (
    card_id      TEXT PRIMARY KEY,
    chain_id     TEXT NOT NULL,
    chain_title  TEXT NOT NULL,
    card_type    TEXT NOT NULL DEFAULT '节点卡',
    chain_role   TEXT DEFAULT '中间过程',
    front        TEXT NOT NULL,
    back_core    TEXT NOT NULL,
    back_detail  TEXT DEFAULT '',
    maturity     TEXT NOT NULL DEFAULT '生',
    tags         TEXT DEFAULT '[]',
    is_new       INTEGER DEFAULT 1,
    last_marked  INTEGER DEFAULT 0
  )
`;

const SQL_CREATE_CHAINS = `
  CREATE TABLE IF NOT EXISTS chains (
    chain_id       TEXT PRIMARY KEY,
    title          TEXT NOT NULL,
    subject        TEXT NOT NULL,
    chain_type     TEXT NOT NULL,
    card_count     INTEGER DEFAULT 0,
    raw_count      INTEGER DEFAULT 0,
    cooked_count   INTEGER DEFAULT 0,
    last_viewed    INTEGER DEFAULT 0,
    created_at     INTEGER NOT NULL,
    updated_at     INTEGER NOT NULL,
    tags           TEXT DEFAULT '[]',
    related_chains TEXT DEFAULT '[]'
  )
`;

const SQL_CREATE_CHAT = `
  CREATE TABLE IF NOT EXISTS chat_history (
    id         TEXT PRIMARY KEY,
    chain_id   TEXT NOT NULL,
    role       TEXT NOT NULL,
    content    TEXT NOT NULL,
    timestamp  INTEGER NOT NULL
  )
`;

const SQL_CREATE_SESSIONS = `
  CREATE TABLE IF NOT EXISTS study_sessions (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_id           TEXT NOT NULL,
    start_time         INTEGER NOT NULL,
    cards_reviewed     INTEGER DEFAULT 0,
    cards_marked_raw   INTEGER DEFAULT 0,
    cards_marked_cooked INTEGER DEFAULT 0,
    completed          INTEGER DEFAULT 0
  )
`;

const SQL_CREATE_INDEXES = [
  'CREATE INDEX IF NOT EXISTS idx_cards_chain ON cards(chain_id)',
  'CREATE INDEX IF NOT EXISTS idx_cards_maturity ON cards(maturity)',
  'CREATE INDEX IF NOT EXISTS idx_chains_subject ON chains(subject)',
  'CREATE INDEX IF NOT EXISTS idx_chat_chain ON chat_history(chain_id)',
];

// ─── 数据库服务 ────────────────────────────────────

export class DatabaseService {
  private store: relationalStore.RdbStore | null = null;

  async initialize(context: Context): Promise<void> {
    const config: relationalStore.StoreConfig = {
      name: DB_NAME,
      securityLevel: relationalStore.SecurityLevel.S1
    };

    this.store = await relationalStore.getRdbStore(context, config);

    await this.store.executeSql(SQL_CREATE_CARDS);
    await this.store.executeSql(SQL_CREATE_CHAINS);
    await this.store.executeSql(SQL_CREATE_CHAT);
    await this.store.executeSql(SQL_CREATE_SESSIONS);

    for (const idx of SQL_CREATE_INDEXES) {
      await this.store.executeSql(idx);
    }
  }

  getStore(): relationalStore.RdbStore {
    if (!this.store) throw new Error('Database not initialized');
    return this.store;
  }

  // ─── 卡片 CRUD ──────────────────────────────────

  async upsertCard(card: Card): Promise<void> {
    const sql = `
      INSERT OR REPLACE INTO cards
        (card_id, chain_id, chain_title, card_type, chain_role,
         front, back_core, back_detail, maturity, tags, is_new, last_marked)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;
    const tags = JSON.stringify(card.tags ?? []);
    await this.store!.executeSql(sql, [
      card.card_id, card.chain_id, card.chain_title, card.card_type, card.chain_role ?? '中间过程',
      card.front, card.back_core, card.back_detail ?? '', card.maturity, tags,
      card.is_new ? 1 : 0, card.last_marked ?? 0
    ]);
  }

  async getCardsByChain(chain_id: string): Promise<Card[]> {
    const predicates = new relationalStore.RdbPredicates('cards');
    predicates.equalTo('chain_id', chain_id);
    const rs = await this.store!.query(predicates);
    return this.mapCards(rs);
  }

  async getCardsByMaturity(maturity: Maturity): Promise<Card[]> {
    const predicates = new relationalStore.RdbPredicates('cards');
    predicates.equalTo('maturity', maturity);
    const rs = await this.store!.query(predicates);
    return this.mapCards(rs);
  }

  async getCard(card_id: string): Promise<Card | null> {
    const predicates = new relationalStore.RdbPredicates('cards');
    predicates.equalTo('card_id', card_id);
    const rs = await this.store!.query(predicates);
    const cards = this.mapCards(rs);
    return cards.length > 0 ? cards[0] : null;
  }

  async markMaturity(card_id: string, maturity: Maturity): Promise<void> {
    const sql = 'UPDATE cards SET maturity = ?, last_marked = ? WHERE card_id = ?';
    await this.store!.executeSql(sql, [maturity, Date.now(), card_id]);

    // 同步更新链的生熟计数
    const card = await this.getCard(card_id);
    if (card) {
      await this.recalcChainCounts(card.chain_id);
    }
  }

  async getRawCardsCount(): Promise<number> {
    const sql = "SELECT COUNT(*) as c FROM cards WHERE maturity = '生'";
    const rs = await this.store!.querySql(sql);
    if (rs.goToFirstRow()) {
      return rs.getLong(0);
    }
    return 0;
  }

  async getTotalCardsCount(): Promise<number> {
    const sql = 'SELECT COUNT(*) as c FROM cards';
    const rs = await this.store!.querySql(sql);
    if (rs.goToFirstRow()) {
      return rs.getLong(0);
    }
    return 0;
  }

  async searchCards(query: string): Promise<Card[]> {
    const like: string = '%' + query + '%';
    const predicates = new relationalStore.RdbPredicates('cards');
    predicates.or()
      .contains('front', like)
      .contains('back_core', like)
      .contains('chain_title', like);
    const rs = await this.store!.query(predicates);
    return this.mapCards(rs);
  }

  // ─── 链 CRUD ────────────────────────────────────

  async upsertChain(chain: Chain): Promise<void> {
    // 已有链用 UPDATE（保留 subject/title/chain_type 等已有字段，只更新元数据）
    // 新链才 INSERT（首次导入时设 subject）
    // 关键：INSERT OR REPLACE 会覆盖已有 subject，所以必须先查再决定
    const checkSql = 'SELECT subject FROM chains WHERE chain_id = ?';
    const r = await this.store!.querySql(checkSql, [chain.chain_id]);
    if (r.goToFirstRow()) {
      // 已有链：只更新 title / tags / related_chains / narrative / updated_at，不碰 subject
      const updSql = `
        UPDATE chains SET
          title = ?, tags = ?, related_chains = ?,
          updated_at = ?
        WHERE chain_id = ?
      `;
      const tags = JSON.stringify(chain.tags ?? []);
      const related = JSON.stringify(chain.related_chains ?? []);
      await this.store!.executeSql(updSql, [
        chain.title,
        tags,
        related,
        Date.now(),
        chain.chain_id
      ]);
    } else {
      // 新链：INSERT
      const insSql = `
        INSERT OR REPLACE INTO chains
          (chain_id, title, subject, chain_type, card_count, raw_count, cooked_count,
           last_viewed, created_at, updated_at, tags, related_chains)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `;
      const tags = JSON.stringify(chain.tags ?? []);
      const related = JSON.stringify(chain.related_chains ?? []);
      const now = Date.now();
      await this.store!.executeSql(insSql, [
        chain.chain_id, chain.title, chain.subject, chain.chain_type,
        chain.card_count ?? 0, chain.raw_count ?? 0, chain.cooked_count ?? 0,
        chain.last_viewed ?? 0, chain.created_at ?? now, chain.updated_at ?? now,
        tags, related
      ]);
    }
    r.close();
  }

  /** 只更新 subject 字段（migration 专用，避免 INSERT OR REPLACE 覆盖已有字段） */
  async updateChainSubject(chain_id: string, subject: Subject): Promise<void> {
    const sql = 'UPDATE chains SET subject = ?, updated_at = ? WHERE chain_id = ?';
    await this.store!.executeSql(sql, [subject, Date.now(), chain_id]);
  }

  /** 只更新 title 字段（编号前缀专用，避免 INSERT OR REPLACE 覆盖 subject） */
  async updateChainTitle(chain_id: string, title: string): Promise<void> {
    const sql = 'UPDATE chains SET title = ?, updated_at = ? WHERE chain_id = ?';
    await this.store!.executeSql(sql, [title, Date.now(), chain_id]);
  }

  async getChainsBySubject(subject: string): Promise<Chain[]> {
    const predicates = new relationalStore.RdbPredicates('chains');
    predicates.equalTo('subject', subject);
    predicates.orderByAsc('chain_id');
    const rs = await this.store!.query(predicates);
    return this.mapChains(rs);
  }

  async getAllChains(): Promise<Chain[]> {
    const predicates = new relationalStore.RdbPredicates('chains');
    predicates.orderByAsc('chain_id');
    const rs = await this.store!.query(predicates);
    return this.mapChains(rs);
  }

  async getChain(chain_id: string): Promise<Chain | null> {
    const predicates = new relationalStore.RdbPredicates('chains');
    predicates.equalTo('chain_id', chain_id);
    const rs = await this.store!.query(predicates);
    const chains = this.mapChains(rs);
    return chains.length > 0 ? chains[0] : null;
  }

  async updateChainViewed(chain_id: string): Promise<void> {
    const sql = 'UPDATE chains SET last_viewed = ? WHERE chain_id = ?';
    await this.store!.executeSql(sql, [Date.now(), chain_id]);
  }

  async recalcChainCounts(chain_id: string): Promise<void> {
    const sql1 = "SELECT COUNT(*) as c FROM cards WHERE chain_id = ? AND maturity = '生'";
    const sql2 = "SELECT COUNT(*) as c FROM cards WHERE chain_id = ? AND maturity = '熟'";
    const sql3 = 'SELECT COUNT(*) as c FROM cards WHERE chain_id = ?';

    let raw = 0, cooked = 0, total = 0;
    let rs = await this.store!.querySql(sql1, [chain_id]);
    if (rs.goToFirstRow()) raw = rs.getLong(0);
    rs = await this.store!.querySql(sql2, [chain_id]);
    if (rs.goToFirstRow()) cooked = rs.getLong(0);
    rs = await this.store!.querySql(sql3, [chain_id]);
    if (rs.goToFirstRow()) total = rs.getLong(0);

    const update = 'UPDATE chains SET raw_count = ?, cooked_count = ?, card_count = ? WHERE chain_id = ?';
    await this.store!.executeSql(update, [raw, cooked, total, chain_id]);
  }

  // ─── 聊天历史 CRUD ─────────────────────────────

  async saveChatMessage(id: string, chain_id: string, role: string, content: string): Promise<void> {
    const sql = 'INSERT INTO chat_history (id, chain_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)';
    await this.store!.executeSql(sql, [id, chain_id, role, content, Date.now()]);
  }

  async getChatHistory(chain_id: string, limit: number = 20): Promise<ChatRecord[]> {
    const sql = 'SELECT id, role, content, timestamp FROM chat_history WHERE chain_id = ? ORDER BY timestamp ASC LIMIT ?';
    const rs = await this.store!.querySql(sql, [chain_id, limit]);
    const result: ChatRecord[] = [];
    while (rs.goToNextRow()) {
      const record: ChatRecord = {
        id: rs.getString(0),
        role: rs.getString(1),
        content: rs.getString(2),
        timestamp: rs.getLong(3)
      };
      result.push(record);
    }
    return result;
  }

  async clearChatHistory(chain_id: string): Promise<void> {
    const sql = 'DELETE FROM chat_history WHERE chain_id = ?';
    await this.store!.executeSql(sql, [chain_id]);
  }

  // ─── 仪表盘统计 ────────────────────────────────

  async getDashboardStats(): Promise<DashboardCounts> {
    let total = 0, chains = 0, raw = 0, cooked = 0;

    let rs = await this.store!.querySql('SELECT COUNT(*) FROM cards');
    if (rs.goToFirstRow()) total = rs.getLong(0);

    rs = await this.store!.querySql('SELECT COUNT(*) FROM chains');
    if (rs.goToFirstRow()) chains = rs.getLong(0);

    rs = await this.store!.querySql("SELECT COUNT(*) FROM cards WHERE maturity = '生'");
    if (rs.goToFirstRow()) raw = rs.getLong(0);

    rs = await this.store!.querySql("SELECT COUNT(*) FROM cards WHERE maturity = '熟'");
    if (rs.goToFirstRow()) cooked = rs.getLong(0);

    const stats: DashboardCounts = { total_cards: total, total_chains: chains, raw_count: raw, cooked_count: cooked };
    return stats;
  }

  // ─── 内部映射 ──────────────────────────────────

  private mapCards(rs: relationalStore.ResultSet): Card[] {
    const result: Card[] = [];
    while (rs.goToNextRow()) {
      let tags: string[] = [];
      try { tags = JSON.parse(rs.getString(9)) as string[]; } catch (_) {}

      const card: Card = {
        card_id: rs.getString(0),
        chain_id: rs.getString(1),
        chain_title: rs.getString(2),
        card_type: rs.getString(3) as CardType,
        chain_role: (rs.getString(4) ?? ChainRole.PROCESS) as ChainRole,
        front: rs.getString(5),
        back_core: rs.getString(6),
        back_detail: rs.getString(7) ?? '',
        maturity: rs.getString(8) as Maturity,
        tags: tags,
        is_new: rs.getLong(10) === 1,
        last_marked: rs.getLong(11)
      };
      result.push(card);
    }
    return result;
  }

  private mapChains(rs: relationalStore.ResultSet): Chain[] {
    const result: Chain[] = [];
    while (rs.goToNextRow()) {
      let tags: string[] = [];
      let related: string[] = [];
      try { tags = JSON.parse(rs.getString(10)) as string[]; } catch (_) {}
      try { related = JSON.parse(rs.getString(11)) as string[]; } catch (_) {}

      const chain: Chain = {
        chain_id: rs.getString(0),
        title: rs.getString(1),
        subject: rs.getString(2) as Subject,
        chain_type: rs.getString(3) as ChainType,
        card_count: rs.getLong(4),
        raw_count: rs.getLong(5),
        cooked_count: rs.getLong(6),
        last_viewed: rs.getLong(7),
        created_at: rs.getLong(8),
        updated_at: rs.getLong(9),
        tags: tags,
        related_chains: related,
        narrative: '',
        child_cards: []
      };
      result.push(chain);
    }
    return result;
  }

  /**
   * 数据迁移（v6，2026-07-31）：
   *   ⑤ 无条件迁移：墨骨山河% 链强制设为书法（最优先，防止任何遗留 subject 错误）
   *   ① GAOKAO_EP* 链：HISTORY → 古诗文
   *   ② 墨骨山河* / CHAIN_CAFA_Ep* 链：HISTORY → 书法（书法史）
   *   ③ 其余所有 CHAIN_* 链（文言语法/诗词鉴赏）：HISTORY → 古诗文
   * 注意：CHAIN_近代* / CHAIN_现代* / CHAIN_全球关联* / CHAIN_现代外交* 是历史链，
   *       但它们不在 gaokao_guwen_cards 里，不会被误迁。
   *       真正的近代史链在 history_v3_cards 里，导入时 subject 已是 HISTORY。
   */
  async migrateSubjectOwnership(): Promise<number> {
    const now = Date.now();
    let migrated = 0;
    let r: relationalStore.ResultSet;

    // ⑤ 无条件迁移：墨骨山河% 链强制设为书法（最优先，防止任何遗留 subject 错误）
    // 注意：用 updateChainSubject 而非 upsertChain（后者 INSERT OR REPLACE 会覆盖 subject）
    r = await this.store!.querySql(
      `SELECT chain_id FROM chains WHERE chain_id LIKE '墨骨山河%'`
    );
    let migCount = 0;
    while (r.goToNextRow()) {
      await this.updateChainSubject(r.getString(0), Subject.CALLIGRAPHY);
      migCount++;
    }
    r.close();
    if (migCount > 0) {
      migrated += migCount;
      hilog.info(DOMAIN, TAG, '[migrate] 墨骨山河链: 强制设为书法 %d 条', migCount);
    }

    // ① 古诗文（GAOKAO_EP* 前缀）
    r = await this.store!.querySql(
      `SELECT COUNT(*) FROM chains WHERE chain_id LIKE 'GAOKAO_%' AND subject = ?`,
      [Subject.HISTORY]
    );
    if (r.goToFirstRow() && r.getLong(0) > 0) {
      await this.store!.executeSql(
        `UPDATE chains SET subject = ?, updated_at = ? WHERE chain_id LIKE 'GAOKAO_%' AND subject = ?`,
        [Subject.GUWEN, now, Subject.HISTORY]
      );
      migrated += r.getLong(0);
    }

    // ② 书法史（墨骨山河* 系列）
    r = await this.store!.querySql(
      `SELECT COUNT(*) FROM chains WHERE chain_id LIKE '墨骨山河%' AND subject = ?`,
      [Subject.HISTORY]
    );
    if (r.goToFirstRow() && r.getLong(0) > 0) {
      await this.store!.executeSql(
        `UPDATE chains SET subject = ?, updated_at = ? WHERE chain_id LIKE '墨骨山河%' AND subject = ?`,
        [Subject.CALLIGRAPHY, now, Subject.HISTORY]
      );
      migrated += r.getLong(0);
    }

    // ③ 古诗文（CAFA 古汉语三链 unconditional：修复 inferSubject 误判 CALLIGRAPHY 的问题）
    // 无论当前 subject 是什么，都强制设为 GUWEN
    const guwenCafa = [
      'CHAIN_CAFA_古汉语基础', 'CHAIN_CAFA_句读标志', 'CHAIN_CAFA_译篆要诀'
    ];
    for (const cid of guwenCafa) {
      r = await this.store!.querySql(
        `SELECT COUNT(*) FROM chains WHERE chain_id = ?`, [cid]
      );
      if (r.goToFirstRow() && r.getLong(0) > 0) {
        const before = r.getLong(0);
        await this.store!.executeSql(
          `UPDATE chains SET subject = ?, updated_at = ? WHERE chain_id = ?`,
          [Subject.GUWEN, now, cid]
        );
        migrated += before;
      }
    }

    // ④ 书法史（CHAIN_CAFA_Ep* unconditional：墨骨山河 CAFA 版本）
    // 无论当前 subject，都强制设为 CALLIGRAPHY（泛规则排除 CAFA_Ep% 后需要显式迁）
    r = await this.store!.querySql(
      `SELECT COUNT(*) FROM chains WHERE chain_id LIKE 'CHAIN_CAFA_Ep%'`
    );
    if (r.goToFirstRow() && r.getLong(0) > 0) {
      const before = r.getLong(0);
      await this.store!.executeSql(
        `UPDATE chains SET subject = ?, updated_at = ? WHERE chain_id LIKE 'CHAIN_CAFA_Ep%'`,
        [Subject.CALLIGRAPHY, now]
      );
      migrated += before;
    }

    // ⑤ 泛规则：其余所有 CHAIN_* 链（文言语法/诗词/鉴赏）→ 古诗文
    // 排除近代史/现代史链（NOT (LIKE ...) 修复 _ 下划线通配符 Bug：
    //   - LIKE 'CHAIN_近代%' 的 % 会匹配 _，导致 'CHAIN_近代探索_01' 被错误捕获
    //   - 改用 NOT (LIKE ...) 等价于 startsWith 语义：精确排除以 'CHAIN_近代' 开头的链
    // 排除 CAFA 古汉语/CAFA_Ep 系列（已在步骤③/④单独处理）
    r = await this.store!.querySql(
      `SELECT COUNT(*) FROM chains WHERE chain_id LIKE 'CHAIN_%'
       AND NOT (chain_id LIKE 'CHAIN_近代%')
       AND NOT (chain_id LIKE 'CHAIN_现代%')
       AND NOT (chain_id LIKE 'CHAIN_全球关联%')
       AND NOT (chain_id LIKE 'CHAIN_现代外交%')
       AND NOT (chain_id LIKE 'CHAIN_CAFA_古汉语基础')
       AND NOT (chain_id LIKE 'CHAIN_CAFA_句读标志')
       AND NOT (chain_id LIKE 'CHAIN_CAFA_译篆要诀')
       AND NOT (chain_id LIKE 'CHAIN_CAFA_Ep%')
       AND subject = ?`,
      [Subject.HISTORY]
    );
    if (r.goToFirstRow() && r.getLong(0) > 0) {
      await this.store!.executeSql(
        `UPDATE chains SET subject = ?, updated_at = ?
         WHERE chain_id LIKE 'CHAIN_%'
           AND NOT (chain_id LIKE 'CHAIN_近代%')
           AND NOT (chain_id LIKE 'CHAIN_现代%')
           AND NOT (chain_id LIKE 'CHAIN_全球关联%')
           AND NOT (chain_id LIKE 'CHAIN_现代外交%')
           AND NOT (chain_id LIKE 'CHAIN_CAFA_古汉语基础')
           AND NOT (chain_id LIKE 'CHAIN_CAFA_句读标志')
           AND NOT (chain_id LIKE 'CHAIN_CAFA_译篆要诀')
           AND NOT (chain_id LIKE 'CHAIN_CAFA_Ep%')
           AND subject = ?`,
        [Subject.GUWEN, now, Subject.HISTORY]
      );
      migrated += r.getLong(0);
    }

    return migrated;
  }
}

// 单例
export const db = new DatabaseService();
