import { defineStore } from 'pinia'

interface AppSettings {
  platform: 'tiktok' | 'instagram_reels' | 'youtube_shorts' | 'twitter'
  clipLength: number
  outputFormat: 'mp4' | 'webm'
  captionStyle: 'bold_centered' | 'bottom_bar' | 'karaoke'
}

const STORAGE_KEY = 'marketing-studio-settings'

const defaults: AppSettings = {
  platform: 'tiktok',
  clipLength: 30,
  outputFormat: 'mp4',
  captionStyle: 'bold_centered',
}

export const useSettingsStore = defineStore('settings', {
  state: (): AppSettings => ({ ...defaults }),

  actions: {
    loadSettings() {
      if (import.meta.client) {
        try {
          const raw = localStorage.getItem(STORAGE_KEY)
          if (raw) {
            const saved = JSON.parse(raw) as Partial<AppSettings>
            Object.assign(this, { ...defaults, ...saved })
          }
        } catch {
          // use defaults
        }
      }
    },

    saveSettings() {
      if (import.meta.client) {
        const data: AppSettings = {
          platform: this.platform,
          clipLength: this.clipLength,
          outputFormat: this.outputFormat,
          captionStyle: this.captionStyle,
        }
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
      }
    },

    resetDefaults() {
      Object.assign(this, defaults)
      this.saveSettings()
    },
  },
})
