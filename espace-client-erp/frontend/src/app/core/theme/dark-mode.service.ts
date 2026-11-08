import { Injectable, effect, signal } from '@angular/core';

const STORAGE_KEY = 'ece_dark_mode';

@Injectable({ providedIn: 'root' })
export class DarkModeService {
  private readonly isDarkSignal = signal<boolean>(this.readInitial());

  readonly isDark = this.isDarkSignal.asReadonly();

  constructor() {
    // Applique/retire la classe globale à chaque changement du signal.
    effect(() => {
      document.body.classList.toggle('dark-theme', this.isDarkSignal());
    });
  }

  private readInitial(): boolean {
    try {
      return localStorage.getItem(STORAGE_KEY) === 'true';
    } catch {
      return false;
    }
  }

  toggle(): void {
    const next = !this.isDarkSignal();
    this.isDarkSignal.set(next);
    try {
      localStorage.setItem(STORAGE_KEY, String(next));
    } catch {
      // silencieux : la préférence ne sera juste pas mémorisée
    }
  }
}
