import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { NavBarComponent } from '../../shared/nav-bar.component';
import { I18nService } from '../../core/i18n/i18n.service';
import { OrdersService } from './orders.service';
import { OrderListItem } from './order.model';
import { triggerBlobDownload } from '../../shared/download.util';

@Component({
  selector: 'app-orders-list',
  standalone: true,
  imports: [CommonModule, RouterLink, NavBarComponent],
  templateUrl: './orders-list.component.html',
  styleUrl: './orders-list.component.scss',
})
export class OrdersListComponent implements OnInit {
  private ordersService = inject(OrdersService);
  readonly i18n = inject(I18nService);

  readonly isLoading = signal(true);
  readonly loadError = signal<string | null>(null);
  readonly orders = signal<OrderListItem[]>([]);
  readonly downloadingId = signal<number | null>(null);

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.isLoading.set(true);
    this.loadError.set(null);

    this.ordersService.list().subscribe({
      next: (res) => {
        this.orders.set(res.orders);
        this.isLoading.set(false);
      },
      error: () => {
        this.loadError.set(this.i18n.t('orders.errorLoad'));
        this.isLoading.set(false);
      },
    });
  }

  downloadPdf(order: OrderListItem, event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    this.downloadingId.set(order.id);
    this.ordersService.downloadPdf(order.id).subscribe({
      next: (blob) => {
        triggerBlobDownload(blob, `commande_${order.numero}.pdf`);
        this.downloadingId.set(null);
      },
      error: () => {
        this.downloadingId.set(null);
      },
    });
  }
}
