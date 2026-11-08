import { Component, ElementRef, ViewChild, AfterViewChecked, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatbotService } from './chatbot.service';
import { I18nService } from '../../core/i18n/i18n.service';

interface ChatMessage {
  role: 'user' | 'bot';
  text: string;
}

@Component({
  selector: 'app-chatbot-widget',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chatbot-widget.component.html',
  styleUrl: './chatbot-widget.component.scss',
})
export class ChatbotWidgetComponent implements AfterViewChecked {
  private chatbotService = inject(ChatbotService);
  readonly i18n = inject(I18nService);

  @ViewChild('messagesEl') messagesEl?: ElementRef<HTMLDivElement>;

  readonly isOpen = signal(false);
  readonly isSending = signal(false);
  readonly draft = signal('');
  readonly messages = signal<ChatMessage[]>([
    {
      role: 'bot',
      text: this.i18n.t('chatbot.greeting'),
    },
  ]);

  private shouldScroll = false;

  toggle(): void {
    this.isOpen.update((v) => !v);
  }

  send(): void {
    const text = this.draft().trim();
    if (!text || this.isSending()) return;

    this.messages.update((msgs) => [...msgs, { role: 'user', text }]);
    this.draft.set('');
    this.isSending.set(true);
    this.shouldScroll = true;

    this.chatbotService.sendMessage(text).subscribe({
      next: (res) => {
        this.messages.update((msgs) => [...msgs, { role: 'bot', text: res.answer }]);
        this.isSending.set(false);
        this.shouldScroll = true;
      },
      error: () => {
        this.messages.update((msgs) => [
          ...msgs,
          { role: 'bot', text: this.i18n.t('chatbot.error') },
        ]);
        this.isSending.set(false);
        this.shouldScroll = true;
      },
    });
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.send();
    }
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll && this.messagesEl) {
      this.messagesEl.nativeElement.scrollTop = this.messagesEl.nativeElement.scrollHeight;
      this.shouldScroll = false;
    }
  }
}
