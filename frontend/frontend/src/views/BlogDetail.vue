<template>
  <main>
    <section class="blog-detail" v-if="post">
      <div class="container">
        <article>
          <h1>{{ post.title }}</h1>
          
          <div class="post-meta">
            <span class="author">By {{ post.author }}</span>
            <span class="date">{{ formatDate(post.created_at) }}</span>
            <span class="views">👁️ {{ post.views }} views</span>
          </div>
          
          <img v-if="post.featured_image" :src="post.featured_image" :alt="post.title" class="featured-image">
          
          <div class="post-content" v-html="formattedContent"></div>
          
          <div class="post-navigation">
            <router-link to="/blog" class="btn btn-outline">← Back to Blog</router-link>
          </div>
        </article>
      </div>
    </section>
    
    <div v-else class="loading">
      <p>Loading post...</p>
    </div>
  </main>
</template>

<script>
import axios from 'axios'
import { useTitle } from '../composables/useTitle'

export default {
  name: 'BlogDetail',
  data() {
    return {
      post: null
    }
  },
  setup() {
    const { setTitle } = useTitle()
    return { setTitle }
  },
  mounted() {
    this.fetchPost()
  },
  methods: {
    async fetchPost() {
      try {
        
        // const slug = this.$route.params.slug

        const slug = this.$route.params.slug
            console.log("SLUG:", slug)




        const response = await axios.get(`/api/blog/${slug}`)
          console.log("POST RESPONSE:", response.data)

          this.post =
            response.data.item ||
            response.data.post ||
            response.data
        


        // Set dynamic title with blog post title
        if (this.post && this.post.title) {
          this.setTitle(this.post.title)
        }
      } catch (error) {
        console.error('Error fetching blog post:', error)
        this.$router.push('/blog')
      }
    }
  },
  watch: {
    post: {
      handler(newPost) {
        if (newPost && newPost.title) {
          this.setTitle(newPost.title)
        }
      },
      deep: true
    }
  }
}
</script>

<style scoped>
.blog-detail {
  padding: 4rem 0;
  min-height: 70vh;
}

article {
  max-width: 800px;
  margin: 0 auto;
}

article h1 {
  color: var(--primary-blue);
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.post-meta {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
  color: var(--gray);
}

.featured-image {
  width: 100%;
  border-radius: 12px;
  margin: 1.5rem 0;
}

.post-content {
  line-height: 1.8;
  font-size: 1.1rem;
  color: #444;
}

.post-navigation {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid #eee;
}

.loading {
  text-align: center;
  padding: 3rem;
}
</style>