import { HttpErrorResponse } from '@angular/common/http';
import { Lang } from '../core/i18n/translations';

/**
 * Interprète une erreur HTTP Angular et retourne un message actionnable.
 * - status === 0 : le navigateur n'a reçu aucune réponse (backend arrêté,
 *   mauvais port, ou requête bloquée par CORS). C'est la cause la plus
 *   fréquente d'un message générique incompréhensible pour l'utilisateur.
 * - body.errors.general / body.errors[field] : erreur métier renvoyée par le backend
 *   (ces messages viennent du serveur, actuellement en français uniquement).
 * - sinon : message générique de secours, traduit selon la langue courante.
 */
export function describeHttpError(err: unknown, lang: Lang = 'fr'): string {
  if (err instanceof HttpErrorResponse) {
    if (err.status === 0) {
      return lang === 'en'
        ? "Unable to reach the server. Make sure the backend is running " +
            "(python run.py, terminal showing 'Running on http://127.0.0.1:5000') " +
            'and the frontend is running on http://localhost:4200.'
        : "Impossible de contacter le serveur. Vérifiez que le backend est bien démarré " +
            "(python run.py, terminal affichant 'Running on http://127.0.0.1:5000') " +
            'et que le frontend tourne bien sur http://localhost:4200.';
    }

    const body = err.error as { errors?: Record<string, string> } | null;
    if (body?.errors?.['general']) {
      return body.errors['general'];
    }
    if (body?.errors) {
      const firstKey = Object.keys(body.errors)[0];
      if (firstKey) return body.errors[firstKey];
    }

    if (err.status >= 500) {
      return lang === 'en'
        ? `Internal server error (code ${err.status}). Please try again, or check the backend terminal for details.`
        : `Erreur interne du serveur (code ${err.status}). Réessayez, ou consultez le terminal backend pour le détail.`;
    }
  }

  return lang === 'en' ? 'Something went wrong. Please try again.' : 'Une erreur est survenue. Veuillez réessayer.';
}
