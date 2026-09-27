<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const props = defineProps({ id: String })
const w = ref(null)
const widthInput = ref('')
const err = ref('')
const saved = ref(false)
onMounted(load)
async function load() {
  w.value = await getJSON(`/api/windows/${props.id}`)
  widthInput.value = w.value.width
}
async function save() {
  err.value = ''; saved.value = false
  const v = Number(widthInput.value)
  if (!Number.isFinite(v) || v <= 0) {
    err.value = '窗宽必须为正数'
    return
  }
  try {
    // 保存后以后端回读的落库行为准（同一仓储口径）
    w.value = await putJSON(`/api/windows/${props.id}`, { width: v })
    widthInput.value = w.value.width
    saved.value = true
  } catch (e) {
    err.value = '保存失败：窗宽必须为正数'
  }
}
</script>
<template><div class="page" v-if="w"><h1>{{ w.name }}</h1><p v-if="w.data_quality==='dirty'" class="bad">{{ w.note }}</p><p>高 {{ w.height }} 褶倍 {{ w.fullness }}</p>
<div class="fab"><label>窗宽 <input v-model="widthInput" type="number" step="0.01" min="0.01"></label> <button @click="save">保存</button></div>
<p v-if="err" class="bad">{{ err }}</p><p v-if="saved" class="ok">已保存，宽 {{ w.width }}</p>
</div></template>
