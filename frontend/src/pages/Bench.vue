<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getJSON, postJSON } from '../api'
import PanelCut from '../components/PanelCut.vue'
const route = useRoute(); const router = useRouter()
const windows = ref([]); const fabrics = ref([]); const wid = ref(1); const fid = ref(1)
const out = ref(null); const calcError = ref('')
const mode = ref('live'); const snap = ref(null); const loadError = ref('')
onMounted(async () => {
  try {
    const [ws, fs] = await Promise.all([getJSON('/api/windows'), getJSON('/api/fabrics')])
    windows.value = ws.items.filter(x=>x.data_quality==='clean')
    fabrics.value = fs.items.filter(x=>x.data_quality==='clean')
    if (windows.value.length) wid.value = windows.value[0].id
    if (fabrics.value.length) fid.value = fabrics.value[0].id
  } catch (e) { loadError.value = '基础数据加载失败' }
  const runId = route.query.run
  if (runId) {
    try {
      snap.value = await getJSON(`/api/runs/${runId}`)
      mode.value = 'snapshot'
      wid.value = snap.value.window_id
    } catch { loadError.value = '记录不存在或已删除' }
  }
})
async function go(save){
  calcError.value = ''
  try {
    out.value = save
      ? await postJSON('/api/estimate',{window_id:wid.value,fabric_id:fid.value,save:true})
      : await getJSON(`/api/estimate?window_id=${wid.value}&fabric_id=${fid.value}`)
  } catch (e) { calcError.value = e.message }
}
function recomputeLive() {
  const wid0 = snap.value.window_id
  mode.value = 'live'; snap.value = null
  router.replace({ path: '/bench', query: {} })
  if (windows.value.some(x => x.id === wid0)) wid.value = wid0
  go(false)
}
// 顶部导航在同一路由下清掉 query 时组件被复用、不会重挂载，这里只处理“退出快照”
watch(() => route.query.run, (v) => {
  if (!v && mode.value === 'snapshot') { mode.value = 'live'; snap.value = null }
})
</script>
<template><div class="page"><h1>算料</h1>
<p v-if="loadError" class="bad">{{ loadError }}</p>
<div v-if="mode==='snapshot' && snap" class="snapshot">
  <p class="bad">以下为落库快照（{{ new Date(snap.created_at).toLocaleString() }}），不随后续改窗变化</p>
  <p>{{ snap.window_name }} ／ {{ snap.fabric_name }}<span v-if="snap.note">（{{ snap.note }}）</span></p>
  <PanelCut :panels="snap.result.panels" :cut-height="snap.result.cut_height"
    :meters="snap.result.meters" :finished-width="snap.result.finished_width" />
</div>
<fieldset :disabled="mode==='snapshot'" style="border:0;padding:0;margin:0">
<select v-model.number="wid"><option v-for="x in windows" :key="x.id" :value="x.id">{{ x.name }}（{{ x.width }}m）</option></select>
<select v-model.number="fid"><option v-for="x in fabrics" :key="x.id" :value="x.id">{{ x.name }}</option></select>
<button @click="go(false)">试算</button><button @click="go(true)">保存</button>
</fieldset>
<p v-if="calcError" class="bad">{{ calcError }}</p>
<template v-if="mode==='live' && out">
  <p>本次计算所用窗宽：{{ out.window.width }} m（{{ out.window.name }}）</p>
  <PanelCut :panels="out.panels" :cut-height="out.cut_height" :meters="out.meters" :finished-width="out.finished_width" />
</template>
<button v-if="mode==='snapshot'" @click="recomputeLive">重新测算该窗</button>
</div></template>
