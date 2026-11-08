import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { NavBarComponent } from '../../shared/nav-bar.component';
import { I18nService } from '../../core/i18n/i18n.service';
import { InvoicesService } from './invoices.service';
import { InvoiceListItem } from './invoice.model';
import { triggerBlobDownload } from '../../shared/download.util';

@Component({
  selector: 'app-invoices-list',
  standalone: true,
  imports: [CommonModule, RouterLink, NavBarComponent],
  templateUrl: './invoices-list.component.html',
  styleUrl: './invoices-list.component.scss',
})
export class InvoicesListComponent implements OnInit {
  private invoicesService = inject(InvoicesService);
  readonly i18n = inject(I18nService);

  readonly isLoading = signal(true);
  readonly loadError = signal<string | null>(null);
  readonly invoices = signal<InvoiceListItem[]>([]);
  readonly downloadingId = signal<number | null>(null);

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.isLoading.set(true);
    this.loadError.set(null);

    this.invoicesService.list().subscribe({
      next: (res) => {
        this.invoices.set(res.invoices);
        this.isLoading.set(false);
      },
      error: () => {
        this.loadError.set(this.i18n.t('invoices.errorLoad'));
        this.isLoading.set(false);
      },
    });
  }

  downloadPdf(invoice: InvoiceListItem, event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    this.downloadingId.set(invoice.id);
    this.invoicesService.downloadPdf(invoice.id).subscribe({
      next: (blob) => {
        triggerBlobDownload(blob, `facture_${invoice.numero}.pdf`);
        this.downloadingId.set(null);
      },
      error: () => this.downloadingId.set(null),
    });
  }
}
