import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { NavBarComponent } from '../../shared/nav-bar.component';
import { I18nService } from '../../core/i18n/i18n.service';
import { ArticlesService } from './articles.service';
import { ArticleOptions, ArticleRecord } from './article.model';

@Component({
  selector: 'app-articles-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, NavBarComponent],
  templateUrl: './articles-list.component.html',
  styleUrl: './articles-list.component.scss',
})
export class ArticlesListComponent implements OnInit {
  private articlesService = inject(ArticlesService);
  private fb = inject(FormBuilder);
  readonly i18n = inject(I18nService);

  readonly isLoading = signal(true);
  readonly loadError = signal<string | null>(null);
  readonly articles = signal<ArticleRecord[]>([]);
  readonly options = signal<ArticleOptions>({ familles: [], tvas: [] });
  readonly isFormOpen = signal(false);
  readonly isSubmitting = signal(false);
  readonly formError = signal<string | null>(null);

  readonly form = this.fb.group({
    nom: ['', [Validators.required]],
    reference: [''],
    prix_vente_ht: [0, [Validators.required, Validators.min(0)]],
    prix_vente_ttc: [0, [Validators.required, Validators.min(0)]],
    stock_disponible: [0, [Validators.min(0)]],
    famille_article_id: [null as number | null],
    tva_id: [null as number | null],
  });

  ngOnInit(): void {
    this.load();
    this.articlesService.options().subscribe({ next: (opts) => this.options.set(opts) });
  }

  load(): void {
    this.isLoading.set(true);
    this.loadError.set(null);
    this.articlesService.list().subscribe({
      next: (res) => {
        this.articles.set(res.articles);
        this.isLoading.set(false);
      },
      error: () => {
        this.loadError.set(this.i18n.t('articles.errorLoad'));
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

    this.articlesService.create(this.form.getRawValue() as any).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.form.reset({ prix_vente_ht: 0, prix_vente_ttc: 0, stock_disponible: 0 });
        this.isFormOpen.set(false);
        this.load();
      },
      error: () => {
        this.isSubmitting.set(false);
        this.formError.set(this.i18n.t('articles.errorCreate'));
      },
    });
  }

  deleteArticle(article: ArticleRecord): void {
    if (!confirm(this.i18n.t('articles.deleteConfirm', { name: article.nom }))) return;
    this.articlesService.delete(article.id).subscribe({ next: () => this.load() });
  }
}
