<template>
  <div class="user-management">
    <div class="management-header">
      <h3>Admin Users</h3>
      <p>Manage administrator accounts and permissions</p>
    </div>

    <div class="users-table">
      <table>
        <thead>
          <tr>
            <th>User</th>
            <th>Role</th>
            <th>Status</th>
            <th>Last Login</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>
              <div class="user-info">
                <strong>{{ user.full_name }}</strong>
                <small>{{ user.email }}</small>
                <span v-if="!user.is_approved" class="badge-pending">Pending Approval</span>
              </div>
            </td>
            <td>
              <select 
                v-if="isSuperAdmin && user.id !== currentUserId"
                v-model="user.role"
                @change="changeRole(user.id, user.role)"
                class="role-select"
                :disabled="loading"
              >
                <option value="super_admin">Super Admin</option>
                <option value="admin">Admin</option>
                <option value="viewer">Viewer</option>
              </select>
              <span v-else class="role-badge" :class="getRoleClass(user.role)">
                {{ formatRole(user.role) }}
              </span>
            </td>
            <td>
              <div class="status-controls">
                <span class="status-badge" :class="user.is_active ? 'status-active' : 'status-suspended'">
                  {{ user.is_active ? 'Active' : 'Suspended' }}
                </span>
                <span v-if="!user.is_approved && user.id !== currentUserId" class="status-badge status-pending">
                  Pending
                </span>
              </div>
            </td>
            <td>
              <span class="last-login">
                {{ user.last_login ? formatDate(user.last_login) : 'Never' }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button 
                  v-if="!user.is_approved && user.id !== currentUserId"
                  @click="approveUser(user.id)"
                  class="btn-approve"
                  :disabled="loading"
                  title="Approve User"
                >
                  ✓ Approve
                </button>
                
                <button 
                  v-if="user.is_approved && user.id !== currentUserId"
                  @click="toggleSuspend(user)"
                  class="btn-suspend"
                  :disabled="loading"
                  :title="user.is_active ? 'Suspend User' : 'Activate User'"
                >
                  {{ user.is_active ? '🔒 Suspend' : '🔓 Activate' }}
                </button>
                
                <button 
                  v-if="isSuperAdmin && user.id !== currentUserId"
                  @click="deleteUser(user.id)"
                  class="btn-delete"
                  :disabled="loading"
                  title="Delete User"
                >
                  🗑️ Delete
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Suspend Modal -->
    <div v-if="showSuspendModal" class="modal" @click.self="showSuspendModal = false">
      <div class="modal-content">
        <h3>{{ suspendUserData.is_active ? 'Suspend User' : 'Activate User' }}</h3>
        <p>
          {{ suspendUserData.is_active 
            ? `Are you sure you want to suspend ${suspendUserData.full_name}?` 
            : `Are you sure you want to activate ${suspendUserData.full_name}?` 
          }}
        </p>
        <div v-if="suspendUserData.is_active" class="form-group">
          <label>Reason for suspension (optional):</label>
          <textarea 
            v-model="suspendReason" 
            placeholder="Enter reason for suspension..."
            rows="3"
          ></textarea>
        </div>
        <div class="modal-actions">
          <button @click="confirmSuspend" class="btn-confirm" :disabled="loading">
            Confirm
          </button>
          <button @click="showSuspendModal = false" class="btn-cancel">
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal" @click.self="showDeleteModal = false">
      <div class="modal-content">
        <h3>Delete User</h3>
        <p>Are you sure you want to permanently delete {{ deleteUserName }}? This action cannot be undone.</p>
        <div class="modal-actions">
          <button @click="confirmDelete" class="btn-confirm" :disabled="loading">
            Confirm Delete
          </button>
          <button @click="showDeleteModal = false" class="btn-cancel">
            Cancel
          </button>
        </div>
      </div>
    </div>

    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>
  </div>
</template>

<script>
import authService from '@/services/auth'

export default {
  name: 'UserManagement',
  data() {
    return {
      users: [],
      loading: false,
      message: '',
      messageType: '',
      showSuspendModal: false,
      showDeleteModal: false,
      suspendUserData: {},
      suspendReason: '',
      deleteUserId: null,
      deleteUserName: '',
      currentUserId: null
    }
  },
  computed: {
    isSuperAdmin() {
      const user = authService.getUser()
      return user && user.role === 'super_admin'
    }
  },
  mounted() {
    this.loadUsers()
    const currentUser = authService.getUser()
    this.currentUserId = currentUser?.id
  },
  methods: {
    async loadUsers() {
      this.loading = true
      try {
        this.users = await authService.getUsers()
      } catch (error) {
        this.showMessage('Failed to load users', 'error')
      } finally {
        this.loading = false
      }
    },
    
    async approveUser(userId) {
      this.loading = true
      try {
        await authService.approveUser(userId)
        this.showMessage('User approved successfully!', 'success')
        this.loadUsers()
      } catch (error) {
        this.showMessage(error.response?.data?.error || 'Failed to approve user', 'error')
      } finally {
        this.loading = false
      }
    },
    
    toggleSuspend(user) {
      this.suspendUserData = user
      this.suspendReason = ''
      this.showSuspendModal = true
    },
    
    async confirmSuspend() {
      this.loading = true
      try {
        await authService.suspendUser(
          this.suspendUserData.id, 
          !this.suspendUserData.is_active,
          this.suspendReason
        )
        this.showMessage(
          `User ${this.suspendUserData.is_active ? 'suspended' : 'activated'} successfully!`, 
          'success'
        )
        this.showSuspendModal = false
        this.loadUsers()
      } catch (error) {
        this.showMessage(error.response?.data?.error || 'Operation failed', 'error')
      } finally {
        this.loading = false
      }
    },
    
    async changeRole(userId, newRole) {
      this.loading = true
      try {
        await authService.changeUserRole(userId, newRole)
        this.showMessage('User role updated successfully!', 'success')
        this.loadUsers()
      } catch (error) {
        this.showMessage(error.response?.data?.error || 'Failed to change role', 'error')
        this.loadUsers() // Reload to revert the select value
      } finally {
        this.loading = false
      }
    },
    
    deleteUser(user) {
      this.deleteUserId = user.id
      this.deleteUserName = user.full_name
      this.showDeleteModal = true
    },
    
    async confirmDelete() {
      this.loading = true
      try {
        await authService.deleteUser(this.deleteUserId)
        this.showMessage('User deleted successfully!', 'success')
        this.showDeleteModal = false
        this.loadUsers()
      } catch (error) {
        this.showMessage(error.response?.data?.error || 'Failed to delete user', 'error')
      } finally {
        this.loading = false
      }
    },
    
    formatRole(role) {
      const roles = {
        super_admin: 'Super Admin',
        admin: 'Admin',
        viewer: 'Viewer'
      }
      return roles[role] || role
    },
    
    getRoleClass(role) {
      return {
        'role-super': role === 'super_admin',
        'role-admin': role === 'admin',
        'role-viewer': role === 'viewer'
      }
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    showMessage(msg, type) {
      this.message = msg
      this.messageType = type
      setTimeout(() => {
        this.message = ''
      }, 3000)
    }
  }
}
</script>

<style scoped>
.user-management {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
}

.management-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f0f0f0;
}

.management-header h3 {
  color: var(--primary-blue);
  margin-bottom: 0.25rem;
}

.management-header p {
  color: #666;
  font-size: 0.9rem;
}

.users-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead th {
  text-align: left;
  padding: 1rem 0.75rem;
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e5e7eb;
}

tbody td {
  padding: 1rem 0.75rem;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: middle;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-info strong {
  color: var(--primary-blue);
}

.user-info small {
  color: #666;
  font-size: 0.85rem;
}

.badge-pending {
  display: inline-block;
  margin-top: 0.25rem;
  padding: 0.2rem 0.5rem;
  background: #fef3c7;
  color: #92400e;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
}

.role-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  cursor: pointer;
}

.role-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.role-super {
  background: #fef3c7;
  color: #92400e;
}

.role-admin {
  background: #dbeafe;
  color: #1e40af;
}

.role-viewer {
  background: #e5e7eb;
  color: #374151;
}

.status-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-active {
  background: #d1fae5;
  color: #065f46;
}

.status-suspended {
  background: #fee2e2;
  color: #991b1b;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.last-login {
  font-size: 0.85rem;
  color: #666;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-approve, .btn-suspend, .btn-delete {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s;
}

.btn-approve {
  background: #10b981;
  color: white;
}

.btn-approve:hover:not(:disabled) {
  background: #059669;
}

.btn-suspend {
  background: #f59e0b;
  color: white;
}

.btn-suspend:hover:not(:disabled) {
  background: #d97706;
}

.btn-delete {
  background: #ef4444;
  color: white;
}

.btn-delete:hover:not(:disabled) {
  background: #dc2626;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal Styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
}

.modal-content h3 {
  margin-bottom: 1rem;
  color: var(--primary-blue);
}

.modal-content p {
  margin-bottom: 1rem;
  color: #555;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-family: inherit;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.btn-confirm, .btn-cancel {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-confirm {
  background: #ef4444;
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  background: #dc2626;
}

.btn-cancel {
  background: #e5e7eb;
  color: #333;
}

.btn-cancel:hover {
  background: #d1d5db;
}

/* Message Styles */
.message {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  font-size: 0.9rem;
  animation: slideIn 0.3s ease;
  z-index: 1000;
}

.message.success {
  background: #d1fae5;
  color: #065f46;
  border-left: 4px solid #10b981;
}

.message.error {
  background: #fee2e2;
  color: #991b1b;
  border-left: 4px solid #ef4444;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }
  
  .btn-approve, .btn-suspend, .btn-delete {
    width: 100%;
  }
  
  .role-select {
    width: 100%;
  }
}
</style>
