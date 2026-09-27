<script setup>
import { computed, onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import PanelCut from '../components/PanelCut.vue'
const windows = ref([]); const fabrics = ref([]); const wid = ref(1); const fid = ref(1); const out = ref(null)
const selectedWindow = computed(() => windows.value.find(x => x.id === wid.value) || null)
onMounted(async () => {
  await refreshWindows()
  fabrics.value = (await getJSON('/api/fabrics')).items.filter(x=>x.data_quality==='clean')
  if (fabrics.value.length) fid.value = fabrics.value[0].id
})
async function refreshWindows() {
  // 每次进入/测算前都重新拉取，详情页改宽后这里不允许残留旧宽
  const fresh = (await getJSON('/api/windows')).items.filter(x=>x.data_quality==='clean')
  if (!fresh.some(x => x.id === wid.value) && fresh.length) wid.value = fresh[0].id
  windows.value = fresh
}
async function go(save){
  await refreshWindows()
  out.value = save
    ? await postJSON('/api/estimate',{window_id:wid.value,fabric_id:fid.value,save:true})
    : await getJSON(`/api/estimate?window_id=${wid.value}&fabric_id=${fid.value}`)
}
</script>
<template><div class="page"><h1>算料</h1>
<select v-model.number="wid"><option v-for="x in windows" :key="x.id" :value="x.id">{{ x.name }}（宽 {{ x.width }}）</option></select>
<select v-model.number="fid"><option v-for="x in fabrics" :key="x.id" :value="x.id">{{ x.name }}</option></select>
<button @click="go(false)">试算</button><button @click="go(true)">保存</button>
<p v-if="selectedWindow">当前窗宽 {{ selectedWindow.width }}（窗户列表实时口径）</p>
<PanelCut v-if="out" :panels="out.panels" :cut-height="out.cut_height" :meters="out.meters" />
<p v-if="out">成品宽 {{ out.finished_width }} m ＝ 窗宽 {{ out.window.width }} × 褶倍 {{ out.window.fullness }}</p>
</div></template>
