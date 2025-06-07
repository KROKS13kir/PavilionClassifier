import { createApp } from 'vue'
import './fonts.css';
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faHome, faSignInAlt, faSignOutAlt, faUserCircle,
         faClipboardList, faUsers, faUserPlus, faChartLine, faBuildingColumns } from '@fortawesome/free-solid-svg-icons'


axios.defaults.baseURL = '/api'
axios.defaults.headers.post['Content-Type'] = 'application/json'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

const auth = useAuthStore()
auth.initialize()

library.add(faHome, faSignInAlt, faSignOutAlt, faUserCircle,
            faClipboardList, faUsers, faUserPlus, faBuildingColumns, faChartLine)
app.component('fa', FontAwesomeIcon)

app.use(router)
app.mount('#app')







