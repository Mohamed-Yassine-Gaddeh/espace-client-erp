import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../core/auth/auth.service';
import { I18nService } from '../../core/i18n/i18n.service';
import { DashboardService } from './dashboard.service';
import { DashboardSummary } from './dashboard.model';
import { ErpOverview } from './erp-overview.model';
import { ChatbotWidgetComponent } from '../chatbot/chatbot-widget.component';
import { NavBarComponent } from '../../shared/nav-bar.component';
import { ChartComponent } from '../../shared/chart/chart.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, ChatbotWidgetComponent, NavBarComponent, ChartComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
  private dashboardService = inject(DashboardService);
  private authService = inject(AuthService);
  private router = inject(Router);
  readonly i18n = inject(I18nService);

  readonly isLoading = signal(true);
  readonly loadError = signal<string | null>(null);
  readonly summary = signal<DashboardSummary | null>(null);

  readonly isOverviewLoading = signal(true);
  readonly overview = signal<ErpOverview | null>(null);

  ngOnInit(): void {
    this.loadSummary();
    this.loadOverview();
  }

  loadOverview(): void {
    this.isOverviewLoading.set(true);
    this.dashboardService.getErpOverview().subscribe({
      next: (data) => {
        this.overview.set(data);
        this.isOverviewLoading.set(false);
      },
      error: () => {
        // Non bloquant : le reste du dashboard (solde, finance globale déjà
        // affichée) continue de fonctionner même si ce bloc échoue.
        this.isOverviewLoading.set(false);
      },
    });
  }

  loadSummary(): void {
    this.isLoading.set(true);
    this.loadError.set(null);

    this.dashboardService.getSummary().subscribe({
      next: (data) => {
        this.summary.set(data);
        this.isLoading.set(false);
      },
      error: () => {
        this.loadError.set(this.i18n.t('dashboard.errorLoad'));
        this.isLoading.set(false);
      },
    });
  }

  markAsRead(notificationId: number): void {
    this.dashboardService.markNotificationRead(notificationId).subscribe({
      next: () => this.loadSummary(),
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  statusEntries(): { status: string; count: number }[] {
    const summary = this.summary();
    if (!summary?.order_status_summary) return [];
    return Object.entries(summary.order_status_summary).map(([status, count]) => ({
      status,
      count: count as number,
    }));
  }

  // --- Datasets pour les graphiques (format attendu par Chart.js) ---

  revenueVsExpensesDatasets() {
    const o = this.overview();
    if (!o) return [];
    return [
      { label: this.i18n.t('dashboard.salesInvoices'), data: o.charts.chiffre_affaires_mensuel, backgroundColor: '#2c4a7c' },
      { label: this.i18n.t('dashboard.expenses'), data: o.charts.depenses_mensuel, backgroundColor: '#d64545' },
    ];
  }

  profitDatasets() {
    const o = this.overview();
    if (!o) return [];
    return [
      {
        label: this.i18n.t('dashboard.netMargin'),
        data: o.charts.benefice_mensuel,
        borderColor: '#1c6b3f',
        backgroundColor: 'rgba(28, 107, 63, 0.15)',
        fill: true,
        tension: 0.3,
      },
    ];
  }

  quickActions(): { icon: string; labelKey: string; route: string }[] {
    // Uniquement des pages qui existent réellement dans l'application —
    // pas de lien vers un formulaire de création de facture/commande/devis,
    // qui n'existe pas encore côté client.
    return [
      { icon: '👥', labelKey: 'clients.new', route: '/clients' },
      { icon: '🗂️', labelKey: 'articles.new', route: '/articles' },
    ];
  }

  navigateTo(route: string): void {
    this.router.navigate([route]);
  }
}
