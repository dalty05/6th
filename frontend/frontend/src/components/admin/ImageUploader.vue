<script setup>
// Update the uploadFile function in ImageUploader.vue

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
    
    // Use singular endpoint names (product, blog) not plural (products, blogs)
    if (props.entityId && props.entityType) {
      // Use singular form: product or blog
      const endpoint = props.entityType === 'products' ? 'product' : 
                      props.entityType === 'blogs' ? 'blog' : 
                      props.entityType.slice(0, -1)  // Remove trailing 's'
      
      response = await api.post(
        `/admin/${endpoint}/${props.entityId}/upload-image`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
    } else {
      // Generic upload
      response = await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    
    imageUrl.value = response.data.url
    emit('update:modelValue', imageUrl.value)
    emit('uploaded', imageUrl.value)
    toast.success('Image uploaded successfully')
    
  } catch (err) {
    
    error.value = err.response?.data?.error || 'Failed to upload image'
    toast.error(error.value)
  } finally {
    uploading.value = false
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}
</script>