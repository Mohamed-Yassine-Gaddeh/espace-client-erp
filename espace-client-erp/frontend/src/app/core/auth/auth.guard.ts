import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

/** Bloque l'accès aux pages protégées si l'utilisateur n'est pas connecté. */
export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.getAccessToken()) {
    return true;
  }

  router.navigate(['/login']);
  return false;
};

/** Empêche un utilisateur déjà connecté de revoir les pages login/register. */
export const guestGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.getAccessToken()) {
    return true;
  }

  router.navigate(['/dashboard']);
  return false;
};
