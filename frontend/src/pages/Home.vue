<template>
    <div class="catalog-shell py-6 md:py-10">
        <header class="mb-5">
            <h1 class="page-title">Книги для IT-специалистов</h1>
        </header>
        <FullSearchBooks>
            <template #after-search><RecentBooks /></template>
        </FullSearchBooks>
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

import RecentBooks from "@/components/RecentBooks.vue";
import FullSearchBooks from "@/components/FullSearchBooks.vue";

export default defineComponent({
    name: "Home",
    components: { FullSearchBooks, RecentBooks },
});
</script>
