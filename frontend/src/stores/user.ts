import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types/user'

export const useUserStore = defineStore('user', () => {
  const user = ref<User>({
    id: 'user_001',
    name: '考研同学',
    avatar: '',
    target_school: '',
  })

  function setUser(newUser: Partial<User>) {
    user.value = { ...user.value, ...newUser }
  }

  return { user, setUser }
})
