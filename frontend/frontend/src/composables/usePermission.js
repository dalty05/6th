// src/composables/usePermission.js
import { computed } from 'vue'
import authService from '@/services/auth'

export function usePermission() {
  const user = computed(() => authService.getUser())
  
  const getDefaultPermissions = (role) => {
    switch(role) {
      case 'super_admin':
        return {
          products: { create: true, read: true, update: true, delete: true },
          blog: { create: true, read: true, update: true, delete: true },
          jobs: { create: true, read: true, update: true, delete: true }, 
          users: { create: true, read: true, update: true, delete: true },
          partners: { create: true, read: true, update: true, delete: true },
          referrals: { create: true, read: true, update: true, delete: true },
          statistics: { create: true, read: true, update: true, delete: true },
          contacts: { create: true, read: true, update: true, delete: true },
          newsletter: { create: true, read: true, update: true, delete: true },
          outlets: { create: true, read: true, update: true, delete: true }
        }
      case 'admin':
        return {
          newsletter: { create: true, read: true, update: true, delete: false },
          products: { create: true, read: true, update: true, delete: false },
          blog: { create: true, read: true, update: true, delete: false },
          jobs: { create: true, read: true, update: true, delete: false }, 
          users: { create: false, read: true, update: false, delete: false },
          partners: { create: true, read: true, update: true, delete: false },
          referrals: { create: true, read: true, update: true, delete: false },
          statistics: { create: false, read: true, update: false, delete: false },
          contacts: { create: false, read: true, update: true, delete: false },
          outlets: { create: true, read: true, update: true, delete: false }
        }
      case 'partner':
        return {
          products: { create: false, read: true, update: false, delete: false },
          blog: { create: false, read: true, update: false, delete: false },
          jobs: { create: false, read: true, update: false, delete: false },  // ← Added jobs (partners can only view)
          users: { create: false, read: false, update: false, delete: false },
          partners: { create: false, read: false, update: false, delete: false },
          referrals: { create: true, read: true, update: true, delete: false },
          statistics: { create: false, read: true, update: false, delete: false },
          contacts: { create: false, read: false, update: false, delete: false }
        }
      default:
        return {}
    }
  }
  
  const permissions = computed(() => {
    const userData = user.value
    if (!userData) return {}
    
    // If user has custom permissions stored, use them
    if (userData.permissions) {
      return userData.permissions
    }
    
    // Otherwise use role-based defaults
    return getDefaultPermissions(userData.role)
  })
  
  // Permission check function
  const can = (resource, action) => {
    if (!user.value) return false
    if (user.value.role === 'super_admin') return true
    
    const resourcePerms = permissions.value[resource]
    return resourcePerms?.[action] === true
  }
  
  // Convenience methods
  const canView = (resource) => can(resource, 'read')
  const canCreate = (resource) => can(resource, 'create')
  const canUpdate = (resource) => can(resource, 'update')
  const canDelete = (resource) => can(resource, 'delete')
  
  // Role check functions - these return booleans directly, not refs
  const isSuperAdmin = () => user.value?.role === 'super_admin'
  const isAdmin = () => user.value?.role === 'admin' || user.value?.role === 'super_admin'
  const isPartner = () => user.value?.role === 'partner'
  
  // Role display name - returns string
  const getRoleDisplayName = () => {
    const role = user.value?.role
    switch(role) {
      case 'super_admin':
        return 'Super Administrator'
      case 'admin':
        return 'Administrator'
      case 'partner':
        return 'Marketing Partner'
      default:
        return 'User'
    }
  }
  
  return {
    can,
    canView,
    canCreate,
    canUpdate,
    canDelete,
    isSuperAdmin,
    isAdmin,
    isPartner,
    getRoleDisplayName,
    permissions
  }
}