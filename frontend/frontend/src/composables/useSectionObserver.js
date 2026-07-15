import { ref, onMounted, onUnmounted } from 'vue'

export function useSectionObserver(sections, options = {}) {
  const activeSection = ref('home')
  const visibleSections = ref(new Set())
  
  const defaultOptions = {
    threshold: 0.3,
    rootMargin: '-80px 0px 0px 0px',
    ...options
  }
  
  let observer = null
  
  const setupObserver = () => {
    observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        const sectionId = entry.target.id
        
        if (entry.isIntersecting) {
          visibleSections.value.add(sectionId)
          
          // Determine which section is most visible
          let maxRatio = 0
          let mostVisible = 'home'
          
          entries.forEach(e => {
            if (e.intersectionRatio > maxRatio) {
              maxRatio = e.intersectionRatio
              mostVisible = e.target.id
            }
          })
          
          activeSection.value = mostVisible
          
          // Update URL hash without scrolling
          if (mostVisible !== 'home') {
            history.replaceState(null, null, `#${mostVisible}`)
          } else {
            history.replaceState(null, null, window.location.pathname)
          }
        } else {
          visibleSections.value.delete(sectionId)
        }
      })
    }, defaultOptions)
    
    sections.forEach(section => {
      const element = document.getElementById(section)
      if (element) {
        observer.observe(element)
      }
    })
  }
  
  const cleanup = () => {
    if (observer) {
      observer.disconnect()
    }
  }
  
  onMounted(() => {
    setupObserver()
  })
  
  onUnmounted(() => {
    cleanup()
  })
  
  return {
    activeSection,
    visibleSections
  }
}