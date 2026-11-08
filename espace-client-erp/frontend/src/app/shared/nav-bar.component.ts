import { Component, ElementRef, HostListener, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../core/auth/auth.service';
import { I18nService } from '../core/i18n/i18n.service';
import { DarkModeService } from '../core/theme/dark-mode.service';
import { NotificationsService } from '../features/notifications/notifications.service';
import { NotificationItem } from '../features/notifications/notification.model';

@Component({
  selector: 'app-nav-bar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './nav-bar.component.html',
  styleUrl: './nav-bar.component.scss',
})
export class NavBarComponent implements OnInit {
  private authService = inject(AuthService);
  private notificationsService = inject(NotificationsService);
  private router = inject(Router);
  private elementRef = inject(ElementRef);

  readonly i18n = inject(I18nService);
  readonly darkMode = inject(DarkModeService);

  readonly isUserMenuOpen = signal(false);
  readonly unreadCount = signal(0);
  readonly isNotificationsOpen = signal(false);
  readonly notifications = signal<NotificationItem[]>([]);

  readonly userName = computed(() => this.authService.currentUser()?.nom ?? '');
  readonly userEmail = computed(() => this.authService.currentUser()?.email ?? '');
  readonly initials = computed(() => {
    const name = this.userName();
    if (!name) return '?';
    const parts = name.trim().split(/\s+/);
    return parts.length > 1
      ? (parts[0][0] + parts[1][0]).toUpperCase()
      : parts[0].slice(0, 2).toUpperCase();
  });

  ngOnInit(): void {
    // Si le profil n'est pas déjà en mémoire (ex: après un rechargement de page), on le récupère.
    if (!this.authService.currentUser()) {
      this.authService.fetchCurrentUser().subscribe({ error: () => {} });
    }

    this.notificationsService.list().subscribe({
      next: (res) => this.unreadCount.set(res.unread_count),
      error: () => {},
    });
  }

  toggleNotifications(): void {
    this.isNotificationsOpen.update((v) => !v);
    if (this.isNotificationsOpen()) {
      this.loadNotifications();
    }
  }

  loadNotifications(): void {
    this.notificationsService.list().subscribe({
      next: (res) => {
        this.notifications.set(res.notifications || []);
        this.unreadCount.set(res.unread_count || 0);
      },
      error: () => {},
    });
  }

  onNotificationClick(notification: NotificationItem): void {
    // mark read then navigate if link exists
    if (!notification.is_read) {
      this.notificationsService.markRead(notification.id).subscribe({ next: () => this.loadNotifications(), error: () => {} });
    }

    this.isNotificationsOpen.set(false);
    if (notification.link) {
      // Use router to navigate to the provided link (assumed internal route)
      this.router.navigateByUrl(notification.link);
    }
  }

  trackByNotification(_index: number, item: NotificationItem): number {
    return item.id;
  }

  toggleUserMenu(): void {
    this.isUserMenuOpen.update((v) => !v);
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    if (!this.elementRef.nativeElement.contains(event.target)) {
      this.isUserMenuOpen.set(false);
      this.isNotificationsOpen.set(false);
    }
  }

  logout(): void {
    this.isUserMenuOpen.set(false);
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
