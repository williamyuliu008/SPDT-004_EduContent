/**
 * gaokao-volunteer · 院校数据服务
 * 从 rawfile/universities.json 读取并查询
 */

import { School } from '../model/SchoolModel';
import { util } from '@kit.ArkTS';

interface ScoreMatch {
  reach: School[];
  match: School[];
  safety: School[];
}

const ALL_PROVINCES = ['北京', '上海', '江苏', '浙江', '广东', '湖北', '四川', '陕西', '湖南', '安徽', '福建', '天津', '吉林', '辽宁', '黑龙江', '重庆']
const ALL_TYPES = ['综合', '理工', '师范', '文科', '医药', '农林', '艺术', '军事']
const ALL_TAGS = ['985', '211', '双一流', '公办']

export class SchoolService {
  private schools: School[] = [];
  private loaded: boolean = false;

  async loadSchools(context: Context): Promise<void> {
    if (this.loaded) return;
    try {
      const resMgr = context.resourceManager;
      const rawData: Uint8Array = await resMgr.getRawFileContent('universities.json');
      const decoder: util.TextDecoder = util.TextDecoder.create('utf-8', { ignoreBOM: true });
      const jsonStr: string = decoder.decode(rawData);
      const data: Object[] = JSON.parse(jsonStr) as Object[];
      this.schools = data.map((item: Object) => item as School);
      this.loaded = true;
    } catch (e) {
      console.error('Failed to load schools:', JSON.stringify(e));
      this.schools = [];
    }
  }

  getAllSchools(): School[] {
    return this.schools;
  }

  getSchoolById(id: string): School | undefined {
    return this.schools.find((s: School) => s.id === id);
  }

  searchSchools(keyword: string): School[] {
    if (!keyword || keyword.trim() === '') return this.schools;
    const kw: string = keyword.trim().toLowerCase();
    return this.schools.filter((s: School) =>
      s.name.toLowerCase().includes(kw) ||
      s.province.includes(kw) ||
      s.city.includes(kw) ||
      s.type.includes(kw) ||
      s.tags.some((t: string) => t.toLowerCase().includes(kw))
    );
  }

  filterByProvince(province: string): School[] {
    if (!province || province === '全部') return this.schools;
    return this.schools.filter((s: School) => s.province === province);
  }

  filterByType(type: string): School[] {
    if (!type || type === '全部') return this.schools;
    return this.schools.filter((s: School) => s.type === type);
  }

  filterByTag(tag: string): School[] {
    if (!tag || tag === '全部') return this.schools;
    return this.schools.filter((s: School) => s.tags.includes(tag));
  }

  filterByScore(score: number): School[] {
    if (!score || score <= 0) return this.schools;
    return this.schools.filter((s: School) => s.minScore > 0 && score >= s.minScore);
  }

  sortByRank(): School[] {
    return [...this.schools].sort((a: School, b: School) => a.rank_national - b.rank_national);
  }

  sortByScore(ascending: boolean = false): School[] {
    return [...this.schools].sort((a: School, b: School) =>
      ascending ? a.minScore - b.minScore : b.minScore - a.minScore
    );
  }

  getProvinces(): string[] {
    return ALL_PROVINCES;
  }

  getTypes(): string[] {
    return ALL_TYPES;
  }

  getTags(): string[] {
    return ALL_TAGS;
  }

  getTotalCount(): number {
    return this.schools.length;
  }

  matchByScore(userScore: number): ScoreMatch {
    const reach: School[] = [];
    const match: School[] = [];
    const safety: School[] = [];
    for (const school of this.schools) {
      const diff = userScore - school.minScore;
      if (diff < -15) {
        reach.push(school);
      } else if (diff >= -15 && diff <= 10) {
        match.push(school);
      } else {
        safety.push(school);
      }
    }
    return { reach, match, safety };
  }
}

export const schoolService = new SchoolService();
