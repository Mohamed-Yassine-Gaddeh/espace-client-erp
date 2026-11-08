import { Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { DarkModeService } from './core/theme/dark-mode.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: `<router-outlet></router-outlet>`,
})
export class AppComponent {
  // L'injection suffit à démarrer l'effect qui applique la classe
  // dark-theme dès le chargement (avant même la nav-bar), pour que
  // la préférence soit respectée aussi sur les pages de connexion.
  private darkMode = inject(DarkModeService);
}
