<script setup lang="ts">
const settingsStore = useSettingsStore()
const saved = ref(false)

onMounted(() => {
  settingsStore.loadSettings()
})

function handleSave() {
  settingsStore.saveSettings()
  saved.value = true
  setTimeout(() => { saved.value = false }, 2000)
}

function handleReset() {
  settingsStore.resetDefaults()
  saved.value = true
  setTimeout(() => { saved.value = false }, 2000)
}

const platformOptions = [
  { label: 'TikTok', value: 'tiktok' },
  { label: 'Instagram Reels', value: 'instagram_reels' },
  { label: 'YouTube Shorts', value: 'youtube_shorts' },
  { label: 'Twitter / X', value: 'twitter' },
]

const formatOptions = [
  { label: 'MP4', value: 'mp4' },
  { label: 'WebM', value: 'webm' },
]

const captionOptions = [
  { label: 'Bold Centered', value: 'bold_centered' },
  { label: 'Bottom Bar', value: 'bottom_bar' },
  { label: 'Karaoke Style', value: 'karaoke' },
]
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-white">Settings</h1>
      <p class="text-sm text-zinc-500">Configure default parameters for video generation</p>
    </div>

    <div class="max-w-2xl space-y-6">
      <!-- Video Defaults -->
      <div class="rounded-xl border border-zinc-800 bg-zinc-900/50 p-6">
        <h2 class="mb-5 text-base font-semibold text-white">Video Defaults</h2>
        <div class="space-y-5">
          <!-- Platform -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-zinc-300">Default Platform</label>
            <select
              v-model="settingsStore.platform"
              class="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2.5 text-sm text-zinc-300 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            >
              <option v-for="opt in platformOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
            <p class="mt-1 text-xs text-zinc-600">Used as the default target platform for new videos</p>
          </div>

          <!-- Clip Length -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-zinc-300">
              Default Clip Length:
              <span class="text-indigo-400">{{ settingsStore.clipLength }}s</span>
            </label>
            <input
              v-model.number="settingsStore.clipLength"
              type="range"
              min="15"
              max="60"
              step="5"
              class="w-full accent-indigo-500"
            />
            <div class="mt-1 flex justify-between text-[10px] text-zinc-600">
              <span>15s</span>
              <span>30s</span>
              <span>45s</span>
              <span>60s</span>
            </div>
          </div>

          <!-- Output Format -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-zinc-300">Output Format</label>
            <select
              v-model="settingsStore.outputFormat"
              class="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2.5 text-sm text-zinc-300 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            >
              <option v-for="opt in formatOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>

          <!-- Caption Style -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-zinc-300">Caption Style</label>
            <select
              v-model="settingsStore.captionStyle"
              class="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2.5 text-sm text-zinc-300 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            >
              <option v-for="opt in captionOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
            <p class="mt-1 text-xs text-zinc-600">Style of auto-generated captions on videos</p>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-3">
        <button
          class="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-indigo-500"
          @click="handleSave"
        >
          Save Settings
        </button>
        <button
          class="rounded-lg border border-zinc-700 bg-zinc-800 px-5 py-2.5 text-sm font-medium text-zinc-300 transition-colors hover:bg-zinc-700"
          @click="handleReset"
        >
          Reset Defaults
        </button>
        <span
          v-if="saved"
          class="text-sm text-emerald-400 transition-opacity"
        >
          Saved!
        </span>
      </div>

      <!-- Storage Info -->
      <div class="rounded-xl border border-zinc-800/50 bg-zinc-900/30 p-4">
        <p class="text-xs text-zinc-600">
          Settings are stored locally in your browser. They will persist across sessions but not across devices.
        </p>
      </div>
    </div>
  </div>
</template>
