import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { NavBarComponent } from '../../shared/nav-bar.component';
import { I18nService } from '../../core/i18n/i18n.service';
import { InvoicesService } from './invoices.service';
import { InvoiceDetail } from './invoice.model';
import { triggerBlobDownload } from '../../shared/download.util';

@Component({
  selector: 'app-invoice-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, NavBarComponent],
  templateUrl: './invoice-detail.component.html',
  styleUrl: './invoice-detail.component.scss',
})
export class InvoiceDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private invoicesService = inject(InvoicesService);
  readonly i18n = inject(I18nService);

  readonly isLoading = signal(true);
  readonly loadError = signal<string | null>(null);
  readonly invoice = signal<InvoiceDetail | null>(null);
  readonly isDownloading = signal(false);

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.invoicesService.get(id).subscribe({
      next: (res) => {
        this.invoice.set(res.invoice);
        this.isLoading.set(false);
      },
      error: () => {
        this.loadError.set(this.i18n.t('invoices.errorDetail'));
        this.isLoading.set(false);
      },
    });
  }

  downloadPdf(): void {
    const invoice = this.invoice();
    if (!invoice) return;
    this.isDownloading.set(true);
    this.invoicesService.downloadPdf(invoice.id).subscribe({
      next: (blob) => {
        triggerBlobDownload(blob, `facture_${invoice.numero}.pdf`);
        this.isDownloading.set(false);
      },
      error: () => this.isDownloading.set(false),
    });
  }
}
