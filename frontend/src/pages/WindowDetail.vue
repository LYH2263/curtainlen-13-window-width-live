<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, patchJSON } from '../api'
const props = defineProps({ id: String })
const w = ref(null)
const draftWidth = ref(null)
const saving = ref(false)
const error = ref('')
onMounted(async () => {
  try { w.value = await getJSON(`/api/windows/${props.id}`); draftWidth.value = w.value.width }
  catch (e) { error.value = '窗户加载失败' }
})
function friendly(e) {
  try { return JSON.parse(e.message).detail?.[0]?.msg || e.message }
  catch { return e.message }
}
async function save() {
  const v = Number(draftWidth.value)
  if (!Number.isFinite(v) || v <= 0) { error.value = '宽度必须为正数'; return }
  saving.value = true; error.value = ''
  try {
    w.value = await patchJSON(`/api/windows/${props.id}`, { width: v })
    draftWidth.value = w.value.width
  } catch (e) { error.value = friendly(e) }
  finally { saving.value = false }
}
</script>
<template><div class="page" v-if="w"><h1>{{ w.name }}</h1>
<p v-if="w.data_quality==='dirty'" class="bad">{{ w.note }}</p>
<p>宽
  <input type="number" step="0.01" min="0" v-model.number="draftWidth" :disabled="saving">
  <button @click="save" :disabled="saving">保存</button>
  <span v-if="error" class="bad">{{ error }}</span>
</p>
<p>高 {{ w.height }} 褶倍 {{ w.fullness }}</p>
</div></template>
