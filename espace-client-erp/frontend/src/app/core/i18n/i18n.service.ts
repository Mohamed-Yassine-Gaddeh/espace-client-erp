import { Injectable, signal } from '@angular/core';
import { Lang, TRANSLATIONS } from './translations';

const STORAGE_KEY = 'ece_lang';
const DEFAULT_LANG: Lang = 'fr';

@Injectable({ providedIn: 'root' })
export class I18nService {
  private readonly langSignal = signal<Lang>(this.readInitialLang());

  readonly lang = this.langSignal.asReadonly();

  private readInitialLang(): Lang {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored === 'fr' || stored === 'en') return stored;
    } catch {
      // localStorage indisponible (mode privé strict, etc.) : on retombe sur le défaut
    }
    return DEFAULT_LANG;
  }

  setLang(lang: Lang): void {
    this.langSignal.set(lang);
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch {
      // silencieux : la préférence ne sera juste pas mémorisée
    }
  }

  toggle(): void {
    this.setLang(this.langSignal() === 'fr' ? 'en' : 'fr');
  }

  /**
   * Traduit une clé pour la langue courante. Lit le signal `langSignal`,
   * ce qui rend l'appel réactif quand il est utilisé directement dans un
   * template Angular (signal-based reactivity).
   * Supporte un remplacement simple de type {placeholder}.
   */
  t(key: string, params?: Record<string, string | number>): string {
    const currentLang = this.langSignal();
    const entry = TRANSLATIONS[key];
    if (!entry) {
      // Clé manquante : on l'affiche telle quelle pour la repérer facilement en dev,
      // plutôt que de faire planter l'affichage.
      return key;
    }
    let text = entry[currentLang] ?? entry[DEFAULT_LANG];
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        text = text.replace(`{${k}}`, String(v));
      }
    }
    return text;
  }
}
