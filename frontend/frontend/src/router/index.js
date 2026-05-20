import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import Products from '../views/Products.vue'
import ProductDetail from '../views/ProductDetail.vue'
import Shop from '../views/Shop.vue'
import Blog from '../views/Blog.vue'
import BlogDetail from '../views/BlogDetail.vue'
import Contact from '../views/Contact.vue'
import Careers from '../views/Careers.vue'
import CSR from '../views/CSR.vue'
import AdminDashboard from '../views/admin/Dashboard.vue'

const routes = [
  { 
    path: '/', 
    name: 'Home', 
    component: Home,
    meta: { 
      title: 'Home | Fresh Dairy Products from Mount Kenya',
      description: 'Welcome to Meru Central Dairy - Kenya\'s biggest dairy co-operative. Discover our fresh Mount Kenya Milk products.'
    }
  },
  { 
    path: '/about', 
    name: 'About', 
    component: About,
    meta: { 
      title: 'About Us | Kenya\'s Largest Dairy Co-operative',
      description: 'Learn about Meru Central Dairy Co-operative Union Ltd, our history, mission, and commitment to quality dairy products.'
    }
  },
  { 
    path: '/products', 
    name: 'Products', 
    component: Products,
    meta: { 
      title: 'Our Products | Fresh Milk, Yoghurt, Lala & Ghee',
      description: 'Explore our range of Mount Kenya Milk products including fresh milk, yoghurt, lala, and pure ghee.'
    }
  },
  { 
    path: '/products/:id', 
    name: 'ProductDetail', 
    component: ProductDetail,
    meta: { 
      title: 'Product Details | Mount Kenya Milk',
      dynamicTitle: true
    }
  },
  { 
    path: '/shop', 
    name: 'Shop', 
    component: Shop,
    meta: { 
      title: 'Shop Online | Buy Mount Kenya Milk Products',
      description: 'Order fresh dairy products online from Mount Kenya Milk. Convenient delivery to your doorstep.'
    }
  },
  { 
    path: '/blog', 
    name: 'Blog', 
    component: Blog,
    meta: { 
      title: 'Blog | Dairy News, Events & Stories',
      description: 'Stay updated with the latest news, events, and stories from Meru Central Dairy.'
    }
  },
  { 
    path: '/blog/:slug', 
    name: 'BlogDetail', 
    component: BlogDetail,
    meta: { 
      title: 'Blog Post | Mount Kenya Milk',
      dynamicTitle: true
    }
  },
  { 
    path: '/contact', 
    name: 'Contact', 
    component: Contact,
    meta: { 
      title: 'Contact Us | Get in Touch with Meru Dairy',
      description: 'Reach out to Meru Central Dairy for inquiries, support, or partnership opportunities.'
    }
  },
  { 
    path: '/careers', 
    name: 'Careers', 
    component: Careers,
    meta: { 
      title: 'Careers | Job Opportunities at Meru Dairy',
      description: 'Join Kenya\'s leading dairy co-operative. Explore career opportunities at Meru Central Dairy.'
    }
  },
  { 
    path: '/csr', 
    name: 'CSR', 
    component: CSR,
    meta: { 
      title: 'CSR | Community Impact & Sustainability',
      description: 'Learn about our corporate social responsibility initiatives and community impact.'
    }
  },
  { 
    path: '/admin/dashboard', 
    name: 'AdminDashboard', 
    component: AdminDashboard,
    meta: { 
      title: 'Admin Dashboard | Manage Content',
      description: 'Administrative dashboard for managing products and blog content.'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Global navigation guard for dynamic titles
router.beforeEach(async (to, from, next) => {
  // Default title
  let pageTitle = to.meta.title || 'Mount Kenya Milk - Meru Dairy'
  
  // Handle dynamic titles for product detail
  if (to.name === 'ProductDetail' && to.params.id) {
    try {
      // Fetch product data to get the name
      const response = await fetch(`/api/products/${to.params.id}`)
      const product = await response.json()
      pageTitle = `${product.name} | Product Details - Mount Kenya Milk`
    } catch (error) {
      console.error('Error fetching product for title:', error)
      pageTitle = 'Product Details | Mount Kenya Milk'
    }
  }
  
  // Handle dynamic titles for blog detail
  if (to.name === 'BlogDetail' && to.params.slug) {
    try {
      // Fetch blog post data to get the title
      const response = await fetch(`/api/blog/${to.params.slug}`)
      const post = await response.json()
      pageTitle = `${post.title} | Blog Post - Mount Kenya Milk`
    } catch (error) {
      console.error('Error fetching blog post for title:', error)
      pageTitle = 'Blog Post | Mount Kenya Milk'
    }
  }
  
  // Set the document title
  document.title = pageTitle
  
  // Optional: Update meta description
  if (to.meta.description) {
    let metaDescription = document.querySelector('meta[name="description"]')
    if (metaDescription) {
      metaDescription.setAttribute('content', to.meta.description)
    }
  }
  
  next()
})

export default router