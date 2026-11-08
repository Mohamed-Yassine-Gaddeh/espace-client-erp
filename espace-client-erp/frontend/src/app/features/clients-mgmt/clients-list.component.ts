import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { NavBarComponent } from '../../shared/nav-bar.component';
import { I18nService } from '../../core/i18n/i18n.service';
import { ClientsService } from './clients.service';
import { ClientRecord } from './client.model';

@Component({
  selector: 'app-clients-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, NavBarComponent],
  templateUrl: './clients-list.component.html',
  styleUrl: './clients-list.component.scss',
})
export class ClientsListComponent implements OnInit {
  private clientsService = inject(ClientsService);
  private fb = inject(FormBuilder);
  readonly i18n = inject(I18nService);

  readonly isLoading = signal(true);
  readonly loadError = signal<string | null>(null);
  readonly clients = signal<ClientRecord[]>([]);
  readonly isFormOpen = signal(false);
  readonly isSubmitting = signal(false);
  readonly formError = signal<string | null>(null);

  readonly form = this.fb.group({
    nom: ['', [Validators.required]],
    email: [''],
    telephone: [''],
    numero_tva: [''],
    siret: [''],
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.isLoading.set(true);
    this.loadError.set(null);
    this.clientsService.list().subscribe({
      next: (res) => {
        this.clients.set(res.clients);
        this.isLoading.set(false);
      },
      error: () => {
        this.loadError.set(this.i18n.t('clients.errorLoad'));
        this.isLoading.set(false);
      },
    });
  }

  toggleForm(): void {
    this.isFormOpen.update((v) => !v);
    this.formError.set(null);
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.isSubmitting.set(true);
    this.formError.set(null);

    this.clientsService.create(this.form.getRawValue() as any).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.form.reset();
        this.isFormOpen.set(false);
        this.load();
      },
      error: () => {
        this.isSubmitting.set(false);
        this.formError.set(this.i18n.t('clients.errorCreate'));
      },
    });
  }
}
