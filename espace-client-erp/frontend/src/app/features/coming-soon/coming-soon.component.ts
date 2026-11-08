import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { NavBarComponent } from '../../shared/nav-bar.component';
import { I18nService } from '../../core/i18n/i18n.service';

@Component({
  selector: 'app-coming-soon',
  standalone: true,
  imports: [CommonModule, NavBarComponent],
  templateUrl: './coming-soon.component.html',
  styleUrl: './coming-soon.component.scss',
})
export class ComingSoonComponent {
  private route = inject(ActivatedRoute);
  readonly i18n = inject(I18nService);

  // La route fournit une clé de traduction (ex: 'nav.sales'), pas un libellé
  // brut, pour que le titre reste correct quelle que soit la langue choisie.
  get title(): string {
    const key = this.route.snapshot.data['titleKey'] ?? 'app.brand';
    return this.i18n.t(key);
  }
}
