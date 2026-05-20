// src/composables/useTitle.js
import { watch } from 'vue'
import { useRoute } from 'vue-router'

const SITE_NAME = 'Mount Kenya Milk - Meru Dairy'

export function useTitle() {
  const route = useRoute()
  
  const setTitle = (title) => {
    if (title) {
      document.title = `${title} | ${SITE_NAME}`
    } else {
      document.title = SITE_NAME
    }
  }
  
  const updateTitleFromRoute = () => {
    const meta = route.meta
    if (meta && meta.title) {
      document.title = meta.title.includes(SITE_NAME) ? meta.title : `${meta.title} | ${SITE_NAME}`
    } else {
      document.title = SITE_NAME
    }
  }
  
  // Watch for route changes
  watch(() => route.path, () => {
    updateTitleFromRoute()
  }, { immediate: true })
  
  return {
    setTitle,
    updateTitleFromRoute
  }
}

export default useTitle