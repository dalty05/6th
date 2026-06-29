<template>
  <div class="tour-staff-management">
    <div class="page-header">
      <div>
        <h2><i class="fas fa-users-cog"></i> Tour Staff Management</h2>
        <p class="subtitle">Create and manage tour managers and assistants</p>
      </div>
      <button @click="openCreateModal" class="btn-primary">
        <i class="fas fa-plus"></i> Add Tour Staff
      </button>
    </div>

    <!-- Staff List -->
    <div class="staff-list">
      <div class="table-wrapper">
        <table class="staff-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6" class="text-center">
                <div class="loading-spinner small"></div>
                <span>Loading staff...</span>
              </td>
            </tr>
            <tr v-else-if="staffList.length === 0">
              <td colspan="6" class="text-center no-data">
                <i class="fas fa-users"></i>
                <p>No tour staff found</p>
                <button @click="openCreateModal" class="btn-primary small">
                  <i class="fas fa-plus"></i> Add First Staff
                </button>
              </td>
            </tr>
            <tr v-for="staff in staffList" :key="staff.id">
              <td>
                <div class="user-info">
                  <span class="name">{{ staff.full_name }}</span>
                </div>
              </td>
              <td>{{ staff.email }}</td>
              <td>
                <span class="role-badge" :class="staff.is_tour_manager ? 'manager' : 'assistant'">
                  <i :class="staff.is_tour_manager ? 'fas fa-user-tie' : 'fas fa-user'"></i>
                  {{ staff.is_tour_manager ? 'Tour Manager' : 'Tour Assistant' }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="staff.is_active ? 'active' : 'inactive'">
                  <i :class="staff.is_active ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
                  {{ staff.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>{{ formatDate(staff.created_at) }}</td>
              <td>
                <div class="action-buttons">
                  <button @click="editStaff(staff)" class="btn-action edit" title="Edit">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button @click="toggleStaffStatus(staff)" class="btn-action toggle" :title="staff.is_active ? 'Deactivate' : 'Activate'">
                    <i :class="staff.is_active ? 'fas fa-pause' : 'fas fa-play'"></i>
                  </button>
                  <button @click="deleteStaff(staff)" class="btn-action delete" title="Delete">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'TourStaffManagement',
  setup() {
    const staffList = ref([])
    const loading = ref(false)

    const loadStaff = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/admin/users')
        // Filter users who are tour staff
        staffList.value = response.data.filter(u => 
          u.is_tour_manager || u.is_tour_assistant
        )
      } catch (error) {
        console.error('Error loading staff:', error)
        alert('Failed to load staff list')
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return 'N/A'
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    }

    const openCreateModal = () => {
      alert('Create Tour Staff - This would open a modal to create new tour staff members.\n\nFor now, you can create tour staff through the User Management page.')
    }

    const editStaff = (staff) => {
      alert(`Edit Staff: ${staff.full_name}\n\nEmail: ${staff.email}\nRole: ${staff.is_tour_manager ? 'Tour Manager' : 'Tour Assistant'}\nStatus: ${staff.is_active ? 'Active' : 'Inactive'}\n\nEdit functionality coming soon.`)
    }

    const toggleStaffStatus = async (staff) => {
      if (!confirm(`Are you sure you want to ${staff.is_active ? 'deactivate' : 'activate'} ${staff.full_name}?`)) return
      
      try {
        await axios.put(`/api/admin/users/${staff.id}`, {
          is_active: !staff.is_active
        })
        await loadStaff()
      } catch (error) {
        console.error('Error toggling staff status:', error)
        alert('Failed to update staff status')
      }
    }

    const deleteStaff = (staff) => {
      if (!confirm(`Are you sure you want to delete ${staff.full_name}?`)) return
      
      // For now just show a message
      alert(`Delete Staff: ${staff.full_name}\n\nDelete functionality coming soon.`)
    }

    onMounted(() => {
      loadStaff()
    })

    return {
      staffList,
      loading,
      openCreateModal,
      editStaff,
      toggleStaffStatus,
      deleteStaff,
      formatDate
    }
  }
}
</script>

<style scoped>
.tour-staff-management {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  color: #1e3a8a;
  margin: 0;
}

.page-header h2 i {
  color: #f59e0b;
  margin-right: 12px;
}

.subtitle {
  color: #6b7280;
  margin: 4px 0 0;
}

.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover {
  background: #d97706;
  transform: translateY(-2px);
}

.btn-primary.small {
  padding: 6px 14px;
  font-size: 13px;
}

.table-wrapper {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.staff-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.staff-table thead {
  background: #f8fafc;
}

.staff-table th {
  text-align: left;
  padding: 12px 16px;
  color: #4b5563;
  font-weight: 600;
  border-bottom: 2px solid #e5e7eb;
}

.staff-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
}

.staff-table tbody tr:hover td {
  background: #f8fafc;
}

.user-info .name {
  font-weight: 500;
  color: #1f2937;
}

.role-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.role-badge.manager {
  background: #dbeafe;
  color: #1e40af;
}

.role-badge.assistant {
  background: #fef3c7;
  color: #92400e;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.btn-action {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-action.edit {
  background: #dbeafe;
  color: #1e40af;
}

.btn-action.toggle {
  background: #fef3c7;
  color: #92400e;
}

.btn-action.delete {
  background: #fee2e2;
  color: #991b1b;
}

.btn-action:hover {
  transform: scale(1.1);
}

.text-center {
  text-align: center;
}

.loading-spinner.small {
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 2px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
  vertical-align: middle;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.no-data {
  text-align: center;
  padding: 40px 0;
  color: #6b7280;
}

.no-data i {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
  opacity: 0.3;
}

.no-data p {
  margin: 0 0 16px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .staff-table {
    font-size: 12px;
  }
  
  .staff-table th,
  .staff-table td {
    padding: 8px 10px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }
}
</style>