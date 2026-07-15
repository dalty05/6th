// src/utils/scroll.js

export const scrollToSection = (sectionId, offset = 80) => {
  const cleanId = sectionId.replace(/^#/, '')
  const element = document.getElementById(cleanId)
  
  if (!element) {
    return false
  }
  
  const elementPosition = element.getBoundingClientRect().top
  const offsetPosition = elementPosition + window.pageYOffset - offset
  
  window.scrollTo({
    top: offsetPosition,
    behavior: 'smooth'
  })
  
  if (cleanId !== 'home') {
    history.pushState(null, null, `#${cleanId}`)
  } else {
    history.pushState(null, null, window.location.pathname)
  }
  
  return true
}

export const getCurrentSection = () => {
  const sections = ['home', 'about', 'products', 'blog', 'contact']
  const scrollPosition = window.scrollY + 100
  
  for (const section of sections) {
    const element = document.getElementById(section)
    if (element) {
      const offsetTop = element.offsetTop
      const offsetBottom = offsetTop + element.offsetHeight
      if (scrollPosition >= offsetTop && scrollPosition < offsetBottom) {
        return section
      }
    }
  }
  return 'home'
}

export const handleInitialHash = () => {
  const hash = window.location.hash.substring(1)
  if (hash && ['home', 'about', 'products', 'blog', 'contact'].includes(hash)) {
    setTimeout(() => {
      scrollToSection(hash, 80)
    }, 100)
  }
}

export const scrollToTop = (behavior = 'smooth') => {
  window.scrollTo({
    top: 0,
    behavior: behavior
  })
}

export const getScrollProgress = () => {
  const windowHeight = window.innerHeight
  const documentHeight = document.documentElement.scrollHeight
  const scrollTop = window.scrollY
  const scrolled = (scrollTop / (documentHeight - windowHeight)) * 100
  return Math.min(Math.max(scrolled, 0), 100)
}

export default {
  scrollToSection,
  getCurrentSection,
  handleInitialHash,
  scrollToTop,
  getScrollProgress
}