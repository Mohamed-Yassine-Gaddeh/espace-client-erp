import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../../core/auth/auth.service';
import { I18nService } from '../../../core/i18n/i18n.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './forgot-password.component.html',
  styleUrl: './forgot-password.component.scss',
})
export class ForgotPasswordComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  readonly i18n = inject(I18nService);

  readonly form = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
  });

  readonly isSubmitting = signal(false);
  readonly successMessage = signal<string | null>(null);

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.isSubmitting.set(true);
    const { email } = this.form.getRawValue();

    this.authService.forgotPassword(email!).subscribe({
      // On ignore volontairement res.message (toujours en français côté
      // backend) et on utilise la clé traduite pour rester cohérent avec
      // la langue choisie dans l'interface.
      next: () => {
        this.isSubmitting.set(false);
        this.successMessage.set(this.i18n.t('forgot.success'));
      },
      error: () => {
        this.isSubmitting.set(false);
        this.successMessage.set(this.i18n.t('forgot.success'));
      },
    });
  }
}
