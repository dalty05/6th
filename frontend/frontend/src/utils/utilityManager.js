// src/utils/titleManager.js

// Base site name
const SITE_NAME = 'Mount Kenya Milk - Meru Dairy'

// Title configurations for each route
const routeTitles = {
  '/': 'Home | Fresh Dairy Products from Mount Kenya',
  '/about': 'About Us | Kenya\'s Largest Dairy Co-operative',
  '/products': 'Our Products | Fresh Milk, Yoghurt, Lala & Ghee',
  '/shop': 'Shop Online | Buy Mount Kenya Milk Products',
  '/blog': 'Blog | Dairy News, Events & Stories',
  '/contact': 'Contact Us | Get in Touch with Meru Dairy',
  '/careers': 'Careers | Job Opportunities at Meru Dairy',
  '/csr': 'CSR | Community Impact & Sustainability'
}

// Dynamic title generators for routes with parameters
const dynamicTitleGenerators = {
  'product-detail': (params) => {
    // This will be called with the product name
    return `${params.productName} | Product Details - Mount Kenya Milk`
  },
  'blog-detail': (params) => {
    return `${params.postTitle} | Blog Post - Mount Kenya Milk`
  }
}

export const titleManager = {
  // Set page title
  setTitle(title, isDynamic = false) {
    if (isDynamic) {
      document.title = `${title} | ${SITE_NAME}`
    } else {
      document.title = title.includes(SITE_NAME) ? title : `${title} | ${SITE_NAME}`
    }
  },
  
  // Get title for a route
  getTitleForRoute(route, params = null) {
    const path = route.path
    const name = route.name
    
    // Check if it's a dynamic route
    if (name && dynamicTitleGenerators[name]) {
      return dynamicTitleGenerators[name](params)
    }
    
    // Check exact path match
    if (routeTitles[path]) {
      return routeTitles[path]
    }
    
    // Check parent path (for nested routes)
    const parentPath = '/' + path.split('/')[1]
    if (parentPath !== '/' && routeTitles[parentPath]) {
      return routeTitles[parentPath]
    }
    
    // Default title
    return SITE_NAME
  }
}

export default titleManager