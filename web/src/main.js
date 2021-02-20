import Vue from 'vue'
import App from './App.vue'

import firebase from 'firebase/app'
import { firebaseConfig } from './firebase.js'

Vue.config.productionTip = false

firebase.initializeApp(firebaseConfig);

new Vue({
  render: h => h(App)
}).$mount('#app')
