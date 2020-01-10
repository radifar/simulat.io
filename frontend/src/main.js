import Vue from 'vue'
import store from '@/store'
import router from '@/router'


import { createProvider } from '@/apollo'






import App from '@/App.vue'
import './registerServiceWorker'

Vue.config.productionTip = false







new Vue({
  router,
  store,
  provide: createProvider().provide(),
  render: h => h(App)
}).$mount('#app')
