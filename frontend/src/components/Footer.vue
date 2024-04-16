<template>

  <div style="padding-bottom: 150px;">
    <div class="border-300 border-top-1 footer w-full">
      <div class="flex justify-content-center my-5 align-items-center">
        <Avatar image="/img/bookshelf_icon.png" size="normal" shape="square" />
        <div class="mr-5">
          <span class="px-2">&copy; 2024</span>
          Книги для IT специалистов
        </div>
        <a href="https://github.com/ig-rudenko/bookshelf" class="no-decoration" target="_blank">
          <i class="pi pi-github" style="font-size: 2.5rem"/>
        </a>
      </div>

    </div>
  </div>

</template>

<script lang="ts" setup>
</script>

<style>

.footer {
  bottom: 0;
  position: absolute;
}

.no-decoration {
  text-decoration: none;
}
</style>