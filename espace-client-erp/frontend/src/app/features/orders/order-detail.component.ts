import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { NavBarComponent } from '../../shared/nav-bar.component';
import { I18nService } from '../../core/i18n/i18n.service';
import { OrdersService } from './orders.service';
import { OrderDetail } from './order.model';
import { triggerBlobDownload } from '../../shared/download.util';

@Component({
  selector: 'app-order-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, NavBarComponent],
  templateUrl: './order-detail.component.html',
  styleUrl: './order-detail.component.scss',
})
export class OrderDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private ordersService = inject(OrdersService);
  readonly i18n = inject(I18nService);

  readonly isLoading = signal(true);
  readonly loadError = signal<string | null>(null);
  readonly order = signal<OrderDetail | null>(null);
  readonly isDownloading = signal(false);

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.ordersService.get(id).subscribe({
      next: (res) => {
        this.order.set(res.order);
        this.isLoading.set(false);
      },
      error: () => {
        this.loadError.set(this.i18n.t('orders.errorDetail'));
        this.isLoading.set(false);
      },
    });
  }

  downloadPdf(): void {
    const order = this.order();
    if (!order) return;
    this.isDownloading.set(true);
    this.ordersService.downloadPdf(order.id).subscribe({
      next: (blob) => {
        triggerBlobDownload(blob, `commande_${order.numero}.pdf`);
        this.isDownloading.set(false);
      },
      error: () => this.isDownloading.set(false),
    });
  }
}
