<template>
  <div class="image-uploader">
    <div 
      class="upload-area"
      :class="{ 'has-image': imageUrl, 'uploading': uploading, 'error': error }"
      @click="triggerFileUpload"
      @dragover.prevent
      @drop.prevent="handleDrop"
    >
      <input
        ref="fileInput"
        type="file"
        accept="image/jpeg,image/png,image/jpg,image/gif,image/webp"
        style="display: none"
        @change="handleFileSelect"
      />
      
      <!-- Image Preview -->
      <div v-if="imageUrl" class="image-preview">
        <img :src="imageUrl" :alt="altText">
        <div class="image-overlay">
          <button type="button" class="change-btn" @click.stop="triggerFileUpload">
            <i class="fas fa-sync-alt"></i> Change
          </button>
          <button type="button" class="remove-btn" @click.stop="removeImage">
            <i class="fas fa-trash"></i> Remove
          </button>
        </div>
      </div>
      
      <!-- Upload Placeholder -->
      <div v-else class="upload-placeholder">
        <i class="fas fa-cloud-upload-alt"></i>
        <p>Click or drag image here</p>
        <small>PNG, JPG, GIF, WEBP up to 5MB</small>
      </div>
      
      <!-- Uploading State -->
      <div v-if="uploading" class="uploading-overlay">
        <div class="spinner"></div>
        <p>Uploading...</p>
      </div>
      
      <!-- Error State -->
      <div v-if="error" class="error-message">
        <i class="fas fa-exclamation-circle"></i>
        {{ error }}
      </div>
    </div>
    
    <!-- Image URL Input (Optional) -->
    <div class="url-input" v-if="showUrlInput">
      <label>Or enter image URL:</label>
      <input 
        type="text" 
        v-model="imageUrlInput" 
        placeholder="https://..."
        @blur="handleUrlInput"
      >
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { toast } from 'vue3-toastify'
import api from '@/services/api'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  altText: {
    type: String,
    default: 'Uploaded image'
  },
  folder: {
    type: String,
    default: 'general'
  },
  entityId: {
    type: [Number, String],
    default: null
  },
  entityType: {
    type: String,
    default: '' // 'product' or 'blog'
  },
  showUrlInput: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'uploaded', 'removed'])

const imageUrl = ref(props.modelValue)
const imageUrlInput = ref(props.modelValue)
const uploading = ref(false)
const error = ref('')
const fileInput = ref(null)

watch(() => props.modelValue, (newVal) => {
  imageUrl.value = newVal
  imageUrlInput.value = newVal
})

const triggerFileUpload = () => {
  fileInput.value?.click()
}

const handleFileSelect = async (event) => {
  const file = event.target.files[0]
  if (file) {
    await uploadFile(file)
  }
}

const handleDrop = async (event) => {
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    await uploadFile(file)
  }
}

const uploadFile = async (file) => {
  // Validate file size (5MB)
  if (file.size > 5 * 1024 * 1024) {
    error.value = 'File size must be less than 5MB'
    setTimeout(() => error.value = '', 3000)
    return
  }
  
  uploading.value = true
  error.value = ''
  
  const formData = new FormData()
  formData.append('file', file)
  formData.append('folder', props.folder)
  
  try {
    let response
    
    // Check if this is a direct upload to a specific entity (product or blog)
    if (props.entityId && props.entityType) {
      // Build the endpoint WITHOUT /api/ prefix because api service adds it
      let endpoint = ''
      
      if (props.entityType === 'product') {
        endpoint = `admin/product/${props.entityId}/upload-image`
      } else if (props.entityType === 'blog') {
        endpoint = `admin/blog/${props.entityId}/upload-image`
      } else {
        endpoint = `admin/${props.entityType}/${props.entityId}/upload-image`
      }
      
      
      response = await api.post(
        endpoint,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
    } else {
      response = await api.post('upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    
    // Extract the URL from response (your backend returns { url: '...' })
    imageUrl.value = response.data.url
    emit('update:modelValue', imageUrl.value)
    emit('uploaded', imageUrl.value)
    toast.success('Image uploaded successfully')
    
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to upload image'
    toast.error(error.value)
  } finally {
    uploading.value = false
    // Reset file input
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

const removeImage = () => {
  imageUrl.value = ''
  imageUrlInput.value = ''
  emit('update:modelValue', '')
  emit('removed')
  toast.info('Image removed')
}

const handleUrlInput = () => {
  if (imageUrlInput.value && imageUrlInput.value !== imageUrl.value) {
    imageUrl.value = imageUrlInput.value
    emit('update:modelValue', imageUrl.value)
    toast.success('Image URL set')
  }
}
</script>

<style scoped>
.image-uploader {
  width: 100%;
}

.upload-area {
  border: 2px dashed #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
  background: #f8fafc;
  min-height: 200px;
}

.upload-area:hover {
  border-color: #f59e0b;
  background: #fef3c7;
}

.upload-area.has-image {
  border-color: #10b981;
  background: white;
}

.upload-area.uploading {
  opacity: 0.6;
  cursor: wait;
}

.upload-area.error {
  border-color: #ef4444;
  background: #fee2e2;
}

.upload-placeholder {
  text-align: center;
  padding: 2rem;
}

.upload-placeholder i {
  font-size: 3rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.upload-placeholder p {
  margin: 0.5rem 0;
  color: #6b7280;
}

.upload-placeholder small {
  font-size: 0.75rem;
  color: #9ca3af;
}

.image-preview {
  position: relative;
  width: 100%;
  height: 200px;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-preview:hover .image-overlay {
  opacity: 1;
}

.change-btn, .remove-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.change-btn {
  background: #3b82f6;
  color: white;
}

.change-btn:hover {
  background: #2563eb;
}

.remove-btn {
  background: #ef4444;
  color: white;
}

.remove-btn:hover {
  background: #dc2626;
}

.uploading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  position: absolute;
  bottom: 10px;
  left: 10px;
  right: 10px;
  background: #ef4444;
  color: white;
  padding: 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  text-align: center;
  z-index: 10;
}

.url-input {
  margin-top: 0.75rem;
}

.url-input label {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.url-input input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.85rem;
}

.url-input input:focus {
  outline: none;
  border-color: #f59e0b;
}
</style>