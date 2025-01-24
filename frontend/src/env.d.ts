/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'vue-router' {
  import { RouteRecordRaw, Router } from '@vue/runtime-dom'
  export { RouteRecordRaw, Router }
  export const createRouter: any
  export const createWebHistory: any
  export const RouterView: any
  export const RouterLink: any
}

declare module 'pinia' {
  import { Store } from '@vue/runtime-dom'
  export { Store }
  export const createPinia: () => any
  export const defineStore: any
}

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $router: Router
  }
}

declare module 'vue' {
  import { Component, ComponentOptions } from '@vue/runtime-core'
  
  export * from '@vue/runtime-core'
  
  export const createApp: (rootComponent: Component | ComponentOptions) => any
  export const defineProps: <Props>() => Readonly<Props>
  export const defineEmits: <E>() => E
  export const defineSlots: <S>() => S
  export const defineExpose: <E>() => E
  export const defineOptions: Function
  export const defineModel: Function
  export const withDefaults: Function
  export const ref: <T>(value: T) => { value: T }
  export const onMounted: (callback: () => void) => void
  export type Ref<T> = { value: T }
}
  