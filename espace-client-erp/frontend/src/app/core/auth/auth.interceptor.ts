import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const isAuthRoute = req.url.includes('/auth/login') || req.url.includes('/auth/register');
  const token = authService.getAccessToken();

  const authReq = token && !isAuthRoute
    ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : req;

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      // Token expiré : on tente un refresh une seule fois, puis on rejoue la requête.
      const isRefreshRoute = req.url.includes('/auth/refresh');
      if (error.status === 401 && !isRefreshRoute && authService.getRefreshToken()) {
        return authService.refreshAccessToken().pipe(
          switchMap(({ access_token }) => {
            const retriedReq = req.clone({
              setHeaders: { Authorization: `Bearer ${access_token}` },
            });
            return next(retriedReq);
          }),
          catchError((refreshError) => {
            router.navigate(['/login']);
            return throwError(() => refreshError);
          }),
        );
      }
      return throwError(() => error);
    }),
  );
};
