/**
 * HRadarChart — 雷达图组件 (Canvas)
 * 用于知识地图全景展示
 */
import { ThemeTokens } from '../theme/tokens';

export interface RadarDataPoint {
  name: string;
  value: number;   // 0-100
  color: string;
}

@Component
export struct HRadarChart {
  @Prop data: string = '[]';           // JSON string of RadarDataPoint[]
  @Prop chartSize: number = 260;            // canvas size in vp
  @Prop levels: number = 4;            // grid levels
  @Prop maxValue: number = 100;
  @Prop labelSize: number = 11;
  @StorageProp('theme') theme: ThemeTokens | null = null;

  private settings: RenderingContextSettings = new RenderingContextSettings(true);
  private ctx: CanvasRenderingContext2D = new CanvasRenderingContext2D(this.settings);

  private getData(): RadarDataPoint[] {
    const raw: string = this.data;
    const result: RadarDataPoint[] = [];
    let current: RadarDataPoint = { name: '', value: 0, color: '#2563eb' };
    let key: string = '';
    let value: string = '';
    let inKey: boolean = false;
    let inValue: boolean = false;
    let braceDepth: number = 0;

    for (let i = 0; i < raw.length; i++) {
      const ch: string = raw[i];
      if (ch === '{') { braceDepth++; current = { name: '', value: 0, color: '#2563eb' }; key = ''; value = ''; inKey = false; }
      else if (ch === '}') { braceDepth--; if (current.name !== '') { result.push(current); } }
      else if (ch === '"' && braceDepth > 0) {
        if (!inKey && !inValue) { inKey = true; key = ''; }
        else if (inKey) { inKey = false; }
        else if (inValue) { inValue = false; }
      }
      else if (inKey) { key += ch; }
      else if (ch === ':' && braceDepth > 0 && !inKey && !inValue) { inValue = true; value = ''; }
      else if (inValue) {
        if (ch === ',' || ch === '}') { inValue = false; const numVal: number = parseFloat(value); if (!isNaN(numVal)) { if (key === 'value') current.value = numVal; else if (key === 'color') current.color = value.replace(/"/g, ''); } }
        else { value += ch; }
      }
    }
    return result;
  }

  build() {
    Canvas(this.ctx)
      .width(this.chartSize)
      .height(this.chartSize)
      .onReady((): void => {
        const points: RadarDataPoint[] = this.getData();
        if (points.length < 3) return;

        const cx: number = this.chartSize / 2;
        const cy: number = this.chartSize / 2;
        const radius: number = this.chartSize * 0.35;
        const count: number = points.length;
        const angleStep: number = (2 * Math.PI) / count;

        this.ctx.clearRect(0, 0, this.chartSize, this.chartSize);

        // Draw grid (concentric polygons)
        for (let level: number = 1; level <= this.levels; level++) {
          const r: number = (radius / this.levels) * level;
          this.ctx.beginPath();
          for (let i: number = 0; i <= count; i++) {
            const idx: number = i % count;
            const angle: number = angleStep * idx - Math.PI / 2;
            const x: number = cx + r * Math.cos(angle);
            const y: number = cy + r * Math.sin(angle);
            if (i === 0) { this.ctx.moveTo(x, y); } else { this.ctx.lineTo(x, y); }
          }
          this.ctx.closePath();
          this.ctx.strokeStyle = '#E5E5E5';
          this.ctx.lineWidth = 0.5;
          this.ctx.stroke();
        }

        // Draw axes
        for (let i: number = 0; i < count; i++) {
          const angle: number = angleStep * i - Math.PI / 2;
          const x: number = cx + radius * Math.cos(angle);
          const y: number = cy + radius * Math.sin(angle);
          this.ctx.beginPath();
          this.ctx.moveTo(cx, cy);
          this.ctx.lineTo(x, y);
          this.ctx.strokeStyle = '#E5E5E5';
          this.ctx.lineWidth = 0.5;
          this.ctx.stroke();
        }

        // Draw data polygon
        this.ctx.beginPath();
        for (let i: number = 0; i <= count; i++) {
          const idx: number = i % count;
          const p: RadarDataPoint = points[idx];
          const angle: number = angleStep * idx - Math.PI / 2;
          const r: number = radius * (p.value / this.maxValue);
          const x: number = cx + r * Math.cos(angle);
          const y: number = cy + r * Math.sin(angle);
          if (i === 0) { this.ctx.moveTo(x, y); } else { this.ctx.lineTo(x, y); }
        }
        this.ctx.closePath();
        this.ctx.fillStyle = 'rgba(37, 99, 235, 0.12)';
        this.ctx.fill();
        this.ctx.strokeStyle = '#2563eb';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();

        // Draw data points
        for (let i: number = 0; i < count; i++) {
          const p: RadarDataPoint = points[i];
          const angle: number = angleStep * i - Math.PI / 2;
          const r: number = radius * (p.value / this.maxValue);
          const x: number = cx + r * Math.cos(angle);
          const y: number = cy + r * Math.sin(angle);
          this.ctx.beginPath();
          this.ctx.arc(x, y, 4, 0, 2 * Math.PI);
          this.ctx.fillStyle = p.color !== '' ? p.color : '#2563eb';
          this.ctx.fill();
        }

        // Draw labels
        this.ctx.fillStyle = '#666666';
        this.ctx.font = this.labelSize.toString() + 'vp sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        for (let i: number = 0; i < count; i++) {
          const p: RadarDataPoint = points[i];
          const angle: number = angleStep * i - Math.PI / 2;
          const labelR: number = radius + 24;
          const lx: number = cx + labelR * Math.cos(angle);
          const ly: number = cy + labelR * Math.sin(angle);
          this.ctx.fillText(p.name, lx, ly);
        }
      })
  }
}
