import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavBarComponent } from '../../shared/nav-bar.component';
import { I18nService } from '../../core/i18n/i18n.service';
import { NotificationsService } from './notifications.service';
import { NotificationItem } from './notification.model';

@Component({
  selector: 'app-notifications-page',
  standalone: true,
  imports: [CommonModule, NavBarComponent],
  templateUrl: './notifications-page.component.html',
  styleUrl: './notifications-page.component.scss',
})
export class NotificationsPageComponent implements OnInit {
  private notificationsService = inject(NotificationsService);
  readonly i18n = inject(I18nService);

  readonly isLoading = signal(true);
  readonly loadError = signal<string | null>(null);
  readonly notifications = signal<NotificationItem[]>([]);
  readonly unreadCount = signal(0);

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.isLoading.set(true);
    this.loadError.set(null);

    this.notificationsService.list().subscribe({
      next: (res) => {
        this.notifications.set(res.notifications);
        this.unreadCount.set(res.unread_count);
        this.isLoading.set(false);
      },
      error: () => {
        this.loadError.set(this.i18n.t('notifications.errorLoad'));
        this.isLoading.set(false);
      },
    });
  }

  markRead(notification: NotificationItem): void {
    if (notification.is_read) return;
    this.notificationsService.markRead(notification.id).subscribe({
      next: () => this.load(),
    });
  }

  markAllRead(): void {
    this.notificationsService.markAllRead().subscribe({
      next: () => this.load(),
    });
  }
}
