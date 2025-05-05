<template>
  <Select id="book.language" v-model="_lang" :showClear="showClear" :options="languages"
          @update:modelValue="updateLanguage">
    <template #option="slotProps">
      <div class="flex items-center">
        <img :alt="slotProps.option.label" :src="`https://flagcdn.com/${slotProps.option.code}.svg`" class="mr-2"
             style="width: 18px"/>
        <div>{{ slotProps.option.label }}</div>
      </div>
    </template>
    <template #value="data">
      <div v-if="data.value" class="flex items-center">
        <img :alt="data.value.label" :src="`https://flagcdn.com/${data.value.code}.svg`" class="mr-2"
             style="width: 18px"/>
        <div>{{ data.value.label }}</div>
      </div>
    </template>
  </Select>
</template>

<script lang="ts">
import {defineComponent, PropType} from 'vue'

import {getLanguagePairByLabel, languagesList} from "@/languages";

export default defineComponent({
  name: "LanguageDropdown",
  props: {
    language: {required: true, type: String as PropType<string | null>},
    showClear: {required: false, type: Boolean, default: false},
  },
  emits: ["update"],
  data() {
    return {
      _lang: null as { label: string; code: string; } | null,
      languages: languagesList,
    }
  },
  mounted() {
    this.updateLang()
  },
  updated() {
    this.updateLang()
  },
  methods: {
    updateLanguage(v: { label: string, code: string } | null) {
      this.$emit("update", v ? v.label : v)
    },
    updateLang() {
      this._lang = this.language ? getLanguagePairByLabel(this.language) : null
    }
  }
})
</script>
