import { RouterLink, RouterView } from 'vue-router'

declare module '@vue/runtime-core' {
  export interface GlobalComponents {
    RouterLink: typeof RouterLink
    RouterView: typeof RouterView
  }
}

export {} 