import {
  AfterViewInit,
  Component,
  ElementRef,
  Input,
  OnChanges,
  OnDestroy,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chart, ChartConfiguration, ChartType, registerables } from 'chart.js';

Chart.register(...registerables);

/**
 * Wrapper minimal autour de Chart.js, pensé pour un usage simple depuis
 * les templates (line/bar charts du dashboard). Ne réimplémente pas
 * Chart.js — se contente de créer/mettre à jour l'instance proprement à
 * chaque changement d'input, et de la détruire à la destruction du
 * composant (évite les fuites mémoire, fréquentes avec Chart.js dans les
 * apps à navigation fréquente entre pages).
 */
@Component({
  selector: 'app-chart',
  standalone: true,
  imports: [CommonModule],
  template: `<div class="chart-wrapper"><canvas #canvasEl></canvas></div>`,
  styles: [
    `
      .chart-wrapper {
        position: relative;
        width: 100%;
        height: 220px;
      }
      canvas {
        width: 100% !important;
        height: 100% !important;
      }
    `,
  ],
})
export class ChartComponent implements AfterViewInit, OnChanges, OnDestroy {
  @Input() type: ChartType = 'line';
  @Input() labels: string[] = [];
  @Input() datasets: ChartConfiguration['data']['datasets'] = [];

  @ViewChild('canvasEl') canvasEl!: ElementRef<HTMLCanvasElement>;

  private chart: Chart | null = null;

  ngAfterViewInit(): void {
    this.render();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (this.chart && (changes['labels'] || changes['datasets'])) {
      this.chart.data.labels = this.labels;
      this.chart.data.datasets = this.datasets;
      this.chart.update();
    }
  }

  ngOnDestroy(): void {
    this.chart?.destroy();
  }

  private render(): void {
    if (!this.canvasEl) return;
    this.chart = new Chart(this.canvasEl.nativeElement, {
      type: this.type,
      data: { labels: this.labels, datasets: this.datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: this.datasets.length > 1, position: 'bottom' } },
        scales: { y: { beginAtZero: true } },
      },
    });
  }
}
