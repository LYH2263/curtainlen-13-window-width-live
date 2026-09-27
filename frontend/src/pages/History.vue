<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const openId = ref(null)
onMounted(load)
async function load() { items.value = (await getJSON('/api/runs')).items }
function toggle(id) { openId.value = openId.value === id ? null : id }
</script>
<template><div class="page"><h1>记录</h1><ul><li v-for="r in items" :key="r.id">
  <a href="#" @click.prevent="toggle(r.id)">{{ r.window_name }} {{ r.result?.meters }}m</a>
  <div v-if="openId===r.id" class="run-detail">
    <p>落库结果（不受后续窗宽修改影响）：</p>
    <p>成品宽 {{ r.result?.finished_width }} m ｜ {{ r.result?.panels }} 幅 × {{ r.result?.cut_height }} m ＝ {{ r.result?.meters }} m</p>
  </div>
</li></ul></div></template>
