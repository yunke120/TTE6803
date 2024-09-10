// import { createApp } from 'vue'
// import './style.css'
// import App from './App.vue'
// createApp(App).mount('#app')

import { createApp } from 'vue';
import ElementPlus from 'element-plus' // 使用element plus ui
import App from './App.vue'
import 'element-plus/dist/index.css'
import { io } from 'socket.io-client'; // 使用socket.io交互前后端
import { createPinia } from 'pinia'    // 使用pinia存储

const socket = io('http://localhost:5000');
//Element-plus
const app = createApp(App);

app.provide('socket', socket); // 提供全局的 Socket 实例
app.use(ElementPlus)
app.use(createPinia())
app.mount('#app');
