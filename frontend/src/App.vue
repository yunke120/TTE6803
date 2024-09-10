<script setup>
import Data from './components/Data.vue';
import Control from './components/Control.vue';
</script>

<template>
  <el-tabs type="border-card">
    <el-tab-pane label="控制指令"><Control></Control></el-tab-pane>
    <el-tab-pane label="遥测"><Data></Data></el-tab-pane>
    <!-- <el-tab-pane label="Role">Role</el-tab-pane>
    <el-tab-pane label="Task">Task</el-tab-pane> -->
  </el-tabs>
  
</template>