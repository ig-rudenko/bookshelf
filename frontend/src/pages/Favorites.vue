<template>
    <LibraryBooks kind="favorite" :userID="userID" />
</template>

<script setup lang="ts">
import LibraryBooks from "@/components/LibraryBooks.vue";

defineProps<{ userID?: number }>();
</script>
