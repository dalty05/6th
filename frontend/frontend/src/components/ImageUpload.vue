<template>
  <div class="image-upload">
    <div class="upload-area" @click="triggerUpload" @dragover.prevent @drop.prevent="handleDrop">
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        style="display: none"
        @change="handleFileSelect"
      />
      
      <div v-if="!imageUrl && !previewUrl" class="upload-placeholder">
        <i class="fas fa-cloud-upload-alt"></i>
        <p>Click or drag image here</p>
        <small>PNG, JPG, GIF up to 16MB</small>
      </div>
      
      <div v-else class="image-preview">
        <img :src="previewUrl || imageUrl" :alt="altText">
        <div class="image-actions">
          <button @click.stop="changeImage" class="change-btn">Change</button>
          <button @click.stop="removeImage" class="remove-btn">Remove</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ImageUpload',
  props: {
    currentImage: {
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
    }
  },
  data() {
    return {
      imageUrl: this.currentImage,
      previewUrl: '',
      uploading: false
    }
  },
  watch: {
    currentImage(newVal) {
      this.imageUrl = newVal
    }
  },
  methods: {
    triggerUpload() {
      this.$refs.fileInput.click()
    },
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.uploadFile(file)
      }
    },
    handleDrop(event) {
      const file = event.dataTransfer.files[0]
      if (file && file.type.startsWith('image/')) {
        this.uploadFile(file)
      }
    },
    async uploadFile(file) {
      if (file.size > 16 * 1024 * 1024) {
        alert('File too large. Maximum size is 16MB.')
        return
      }
      
      this.uploading = true
      const formData = new FormData()
      formData.append('file', file)
      formData.append('folder', this.folder)
      
      try {
        let response
        
        if (this.entityId && this.entityType) {
          // Upload directly to entity
          response = await axios.post(
            `/api/admin/${this.entityType}s/${this.entityId}/image`,
            formData,
            { headers: { 'Content-Type': 'multipart/form-data' } }
          )
        } else {
          // Generic upload
          response = await axios.post('/api/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
        }
        
        this.imageUrl = response.data.url
        this.previewUrl = URL.createObjectURL(file)
        this.$emit('image-uploaded', this.imageUrl)
      } catch (error) {
        console.error('Upload error:', error)
        alert('Failed to upload image')
      } finally {
        this.uploading = false
      }
    },
    changeImage() {
      this.triggerUpload()
    },
    removeImage() {
      this.imageUrl = ''
      this.previewUrl = ''
      this.$emit('image-removed')
    }
  }
}
</script>

<style scoped>
.image-upload {
  margin: 1rem 0;
}

.upload-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: var(--primary-blue);
  background: #f8f9fa;
}

.upload-placeholder {
  text-align: center;
  padding: 2rem;
}

.upload-placeholder i {
  font-size: 3rem;
  color: var(--primary-blue);
  margin-bottom: 1rem;
}

.image-preview {
  position: relative;
  width: 100%;
}

.image-preview img {
  width: 100%;
  max-height: 300px;
  object-fit: cover;
  border-radius: 8px;
}

.image-actions {
  position: absolute;
  bottom: 10px;
  right: 10px;
  display: flex;
  gap: 0.5rem;
}

.change-btn, .remove-btn {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.change-btn {
  background: var(--primary-blue);
  color: white;
}

.remove-btn {
  background: #dc2626;
  color: white;
}
</style>