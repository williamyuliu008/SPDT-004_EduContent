/**
 * HProgressBar — 进度条 (API 26 strict mode)
 */
import { ThemeTokens } from '../theme/tokens';

export type ProgressBarType = 'linear' | 'segments';
export type LabelFormat = 'percent' | 'fraction';

@Component
export struct HProgressBar {
  @Prop current: number = 0;
  @Prop total: number = 1;
  @Prop type: ProgressBarType = 'linear';
  @Prop segments: number = 7;
  @Prop completedSegments: number = 0;
  @Prop showLabel: boolean = true;
  @Prop showAnimation: boolean = true;
  @Prop color: string = '';
  @Prop trackColor: string = '';
  @Prop barHeight: number = 0;
  @Prop labelFormat: LabelFormat = 'fraction';
  @StorageProp('theme') theme: ThemeTokens | null = null;
  @State private animatedProgress: number = 0;
  private segmentItems: number[] = [];

  aboutToAppear(): void {
    for (let i = 0; i < this.segments; i++) { this.segmentItems.push(i); }
    if (this.showAnimation) {
      setTimeout(() => { animateTo({ duration: 600, curve: Curve.EaseOut }, () => { this.animatedProgress = this.getRatio(); }); }, 100);
    } else { this.animatedProgress = this.getRatio(); }
  }

  private getRatio(): number { return this.total <= 0 ? 0 : Math.min(1, Math.max(0, this.current / this.total)); }
  private getColor(): string { return this.color || this.theme?.primary || '#5B8C5A'; }
  private getTrack(): string { return this.trackColor || this.theme?.surfaceVariant || '#E8E8E8'; }
  private getH(): number { return this.barHeight > 0 ? this.barHeight : (this.type === 'segments' ? 12 : 8); }

  build() {
    Column({ space: this.theme?.spacingSmall ?? 4 }) {
      if (this.type === 'segments') {
        Row({ space: 2 }) {
          ForEach(this.segmentItems, (idx: number) => {
            Row().width(`${100 / this.segments - 1}%`).height(this.getH()).borderRadius(this.theme?.radiusSmall ?? 4)
              .backgroundColor(idx < this.completedSegments ? this.getColor() : this.getTrack())
          }, (idx: number): string => idx.toString())
        }.width('100%').borderRadius(this.theme?.radiusSmall ?? 4)
      } else {
        Stack({ alignContent: Alignment.Start }) {
          Row().width('100%').height(this.getH()).backgroundColor(this.getTrack()).borderRadius(this.getH() / 2)
          Row().width(`${this.animatedProgress * 100}%`).height(this.getH()).backgroundColor(this.getColor()).borderRadius(this.getH() / 2)
        }.width('100%')
      }
      if (this.showLabel) {
        Text(this.type === 'segments' ? `${this.completedSegments}/${this.segments}` : (this.labelFormat === 'percent' ? `${Math.round(this.getRatio() * 100)}%` : `${this.current}/${this.total}`))
          .fontSize(this.theme?.fontSizeCaption ?? 12).fontColor('#888888').fontWeight(this.theme?.fontWeightMedium ?? 500)
      }
    }.width('100%').alignItems(HorizontalAlign.End)
  }
}
