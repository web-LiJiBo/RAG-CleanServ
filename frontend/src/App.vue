<template>
  <div id="app">
    <el-container>
      <el-header>
        <h1>RAG-CleanServ 智能客服</h1>
        <el-menu mode="horizontal" :default-active="$route.path" router>
          <el-menu-item index="/chat">对话聊天</el-menu-item>
          <el-menu-item index="/knowledge">知识库管理</el-menu-item>
        </el-menu>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
</script>

<style>
#app {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  height: 100vh;
}
.el-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #409EFF;
  color: white;
  padding: 0 20px;
}
.el-header h1 {
  margin: 0;
  font-size: 20px;
}
.el-header .el-menu {
  background-color: transparent;
  border: none;
}
.el-header .el-menu-item {
  color: white !important;
}
.el-header .el-menu-item:hover {
  background-color: rgba(255,255,255,0.2) !important;
}
.el-main {
  padding: 20px;
  background-color: #f5f5f5;
  height: calc(100vh - 60px);
}
</style>
