interface ApiResponse<T> {
  data: Ref<T | null>
  error: Ref<string | null>
  loading: Ref<boolean>
  execute: () => Promise<T | null>
}

export function useApi() {
  const config = useRuntimeConfig()
  const baseUrl = config.public.apiBase as string

  async function request<T>(
    endpoint: string,
    options: {
      method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
      body?: Record<string, any>
      params?: Record<string, any>
    } = {}
  ): Promise<T> {
    const { method = 'GET', body, params } = options

    const url = new URL(`${baseUrl}${endpoint}`)
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          url.searchParams.set(key, String(value))
        }
      })
    }

    const fetchOptions: RequestInit = {
      method,
      headers: { 'Content-Type': 'application/json' },
    }

    if (body && method !== 'GET') {
      fetchOptions.body = JSON.stringify(body)
    }

    const response = await $fetch<T>(url.toString(), {
      method,
      body: body && method !== 'GET' ? body : undefined,
      params: params || undefined,
    })

    return response
  }

  function useApiRequest<T>(
    endpoint: string,
    options: {
      method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
      body?: Record<string, any>
      params?: Record<string, any>
      immediate?: boolean
    } = {}
  ): ApiResponse<T> {
    const data = ref<T | null>(null) as Ref<T | null>
    const error = ref<string | null>(null) as Ref<string | null>
    const loading = ref(false)

    const execute = async (): Promise<T | null> => {
      loading.value = true
      error.value = null
      try {
        const result = await request<T>(endpoint, options)
        data.value = result
        return result
      } catch (e: any) {
        error.value = e?.data?.message || e?.message || 'An error occurred'
        return null
      } finally {
        loading.value = false
      }
    }

    if (options.immediate !== false) {
      execute()
    }

    return { data, error, loading, execute }
  }

  const get = <T>(endpoint: string, params?: Record<string, any>) =>
    useApiRequest<T>(endpoint, { method: 'GET', params })

  const post = <T>(endpoint: string, body?: Record<string, any>) =>
    useApiRequest<T>(endpoint, { method: 'POST', body })

  const put = <T>(endpoint: string, body?: Record<string, any>) =>
    useApiRequest<T>(endpoint, { method: 'PUT', body })

  const del = <T>(endpoint: string) =>
    useApiRequest<T>(endpoint, { method: 'DELETE' })

  return { request, get, post, put, del, useApiRequest }
}
