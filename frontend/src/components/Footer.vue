<template>
    <footer class="mt-10 border-t border-surface-200 dark:border-surface-800">
        <div
            class="page-shell flex flex-wrap justify-center gap-4 py-5 items-center text-sm text-surface-600 dark:text-surface-400"
        >
            <div class="mr-3">
                <img src="/img/bookshelf_icon.png" alt="" class="w-8 h-8" />
            </div>
            <div class="mr-5">
                <span class="pr-2">&copy; 2024-{{ new Date().getFullYear() }}</span>
                Книги для IT специалистов
            </div>
            <a
                href="https://github.com/ig-rudenko/bookshelf"
                class="no-decoration"
                target="_blank"
                aria-label="Исходный код на GitHub"
            >
                <i class="pi pi-github text-3xl!" />
            </a>
        </div>
    </footer>
</template>
