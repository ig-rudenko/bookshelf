import assert from "node:assert/strict";
import { after, test } from "node:test";
import { createServer } from "vite";
import { createSSRApp, h } from "vue";
import { renderToString } from "@vue/server-renderer";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";
import ts from "typescript";

globalThis.history = { pushState() {} };
globalThis.window = { innerWidth: 1280, location: { pathname: "/", search: "" } };

const server = await createServer({
    server: { middlewareMode: true, watch: null },
    appType: "custom",
});
after(() => server.close());

const { default: api } = await server.ssrLoadModule("/src/services/api/index.ts");
const { default: books } = await server.ssrLoadModule("/src/services/books.ts");
const { default: shelves } = await server.ssrLoadModule("/src/services/bookshelves.ts");
const { FilterBook, FilterBookshelf, createFilterBook } = await server.ssrLoadModule("/src/filters.ts");
const { default: catalog } = await server.ssrLoadModule("/src/components/FullSearchBooks.vue");
const { default: bookshelfPage } = await server.ssrLoadModule("/src/pages/Bookshelves.vue");
const { default: bookPage } = await server.ssrLoadModule("/src/pages/BookPage.vue");
const { default: gallery } = await server.ssrLoadModule("/src/components/BookshelfImages.vue");
const { default: searchForm } = await server.ssrLoadModule("/src/components/SearchBookForm.vue");
const { default: recentBooks } = await server.ssrLoadModule("/src/components/RecentBooks.vue");
const { default: libraryBooks } = await server.ssrLoadModule("/src/components/LibraryBooks.vue");
globalThis.document = { title: "", documentElement: { classList: { add() {}, remove() {} } } };
globalThis.localStorage = {};
globalThis.window.matchMedia = () => ({ matches: false });
const { default: header } = await server.ssrLoadModule("/src/components/Header.vue");

test("обновление токенов Vuex принимает оба токена одним payload", () => {
    const source = readFileSync(new URL("../src/store/auth.module.ts", import.meta.url), "utf8");
    const { outputText } = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS } });
    const exports = {};
    runInNewContext(outputText, {
        exports,
        require: () => ({
            default: { getUser: () => null },
            tokenService: { getUserTokens: () => ({}) },
        }),
    });
    const state = {
        status: { loggedIn: false },
        userTokens: { accessToken: "old-access", refreshToken: "old-refresh" },
    };
    exports.auth.mutations.refreshToken(state, { accessToken: "new-access", refreshToken: "new-refresh" });
    assert.equal(state.status.loggedIn, true);
    assert.deepEqual(state.userTokens, { accessToken: "new-access", refreshToken: "new-refresh" });
});

function response(data) {
    return { data, status: 200, statusText: "OK", headers: {}, config: {} };
}

for (const [name, load] of [
    ["каталог", () => books.getBooksList(1, new FilterBook())],
    ["полки", () => shelves.getBookshelvesList(1, new FilterBookshelf())],
]) {
    test(`${name}: тот же запрос повторяется после ошибки и при новом открытии`, async () => {
        let attempts = 0;
        const data = { books: [], bookshelves: [], totalCount: 0 };
        api.defaults.adapter = async () => {
            attempts++;
            if (attempts === 1) throw new Error("offline");
            return response(data);
        };
        await assert.rejects(load(), /offline/);
        assert.deepEqual(await load(), data);
        assert.deepEqual(await load(), data);
        assert.equal(attempts, 3);
    });
}

test("каталог отличает ошибку от пустой выдачи и восстанавливается с тем же запросом", async () => {
    const state = {
        ...catalog.data.call({ initialCompactView: false }),
        authScrollToSearchBlock: false,
        initialPerPage: 25,
        replaceThumb: (value) => value,
    };
    state.filters.search = "Python";
    api.defaults.adapter = async () => {
        throw new Error("offline");
    };
    await catalog.methods.getBooksList.call(state, 1, state.filters);
    assert.ok(state.loadError);
    assert.equal(state.loadingBooks, false);
    assert.equal(state.filters.search, "Python");

    const data = { books: [], totalCount: 0, currentPage: 1, perPage: 25 };
    api.defaults.adapter = async () => response(data);
    await catalog.methods.getBooksList.call(state, 1, state.filters);
    assert.equal(state.loadError, "");
    assert.deepEqual(state.results, data);
});

for (const [name, page, method, initial, data] of [
    [
        "полки",
        bookshelfPage,
        "getBookshelvesList",
        { filter: new FilterBookshelf(), results: null },
        { bookshelves: [], totalCount: 0 },
    ],
    ["книга", bookPage, "getBook", { book: null, bookIdParam: 4 }, { id: 4, title: "Python" }],
]) {
    test(`${name}: ошибка загрузки допускает повторную попытку`, async () => {
        const state = { ...initial, loadError: "" };
        api.defaults.adapter = async () => {
            throw new Error("offline");
        };
        await page.methods[method].call(state, 1);
        assert.ok(state.loadError);
        api.defaults.adapter = async () => response(data);
        await page.methods[method].call(state, 1);
        assert.equal(state.loadError, "");
        assert.deepEqual(state.book || state.results, data);
    });
}

test("язык и диапазон страниц восстанавливаются из URL после обновления страницы", () => {
    const original = new FilterBook();
    original.language = "Русский";
    original.pagesGt = 100;
    original.pagesLt = 500;
    const restored = createFilterBook(Object.fromEntries(new URLSearchParams(original.urlParams)));
    assert.equal(restored.language, "Русский");
    assert.equal(restored.pagesGt, 100);
    assert.equal(restored.pagesLt, 500);
});

test("личные разделы сгруппированы в библиотеку и сохраняют свои адреса", () => {
    const items = header.computed.menuItems.call({
        loggedIn: true,
        user: {},
        themeIcon: "pi pi-circle",
        favoriteItem: { label: "Избранное", href: "/favorites", root: true },
        readItem: { label: "Прочитанное", href: "/read", root: true },
    });
    const library = items.find((item) => item.label === "Моя библиотека");
    assert.ok(library);
    assert.ok(!items.some((item) => item.href === "/favorites"));
    const links = library.items
        .flat()
        .flatMap((group) => group.items)
        .map((item) => item.href);
    assert.deepEqual(links, ["/favorites", "/read", "/last-viewed"]);
});

test("пагинация сохраняет третью страницу после повторного создания компонента", async () => {
    let receivedFirst;
    const empty = { inheritAttrs: false, render: () => null };
    const component = {
        ...catalog,
        components: { ...catalog.components, SearchBookForm: empty },
        data: () => ({
            ...catalog.data.call({ initialCompactView: false }),
            results: { books: [], currentPage: 3, perPage: 25, totalCount: 80 },
        }),
    };
    const app = createSSRApp(component);
    app.component("Button", empty);
    app.component("Skeleton", empty);
    app.component("Paginator", {
        props: ["first"],
        setup: (props) => () => {
            receivedFirst = props.first;
            return h("nav");
        },
    });
    await renderToString(app);
    assert.equal(receivedFirst, 50);
});

test("полка не открывает запоздавшую подсказку после ухода с обложки", async () => {
    let finish;
    api.defaults.adapter = () =>
        new Promise((resolve) => {
            finish = resolve;
        });
    let shown = false;
    const state = {
        ...gallery.data(),
        keepDetails() {},
        $refs: {
            bookDetails: {
                show() {
                    shown = true;
                },
                hide() {},
            },
        },
    };
    const request = gallery.methods.showDetails.call(state, { currentTarget: {} }, 4);
    await new Promise(setImmediate);
    state.detailsBookId = null;
    finish(response({ id: 4, title: "Python" }));
    await request;
    assert.equal(shown, false);
    assert.equal(state.currentBook, undefined);
});

function filterForm() {
    const events = [];
    const state = {
        ...searchForm.data.call({ initialCompactView: false }),
        filterData: Object.assign(new FilterBook(), { authors: "Билл", tags: ["Python"] }),
        $refs: { filterBooks: { toggle() {}, hide() {} } },
        $emit: (event, value) => events.push({ event, value }),
    };
    for (const [name, method] of Object.entries(searchForm.methods)) state[name] = method.bind(state);
    state.toggleFilterBooks({});
    state.filtersVisible = true;
    return { state, events };
}

test("закрытие фильтров без применения сохраняет прежние ограничения и темы", () => {
    const { state, events } = filterForm();
    assert.ok(state.draftFilter, "редактирование должно происходить в отдельном черновике");
    state.draftFilter.authors = "Другой автор";
    state.removeTag(0);
    state.filtersVisible = false;
    assert.equal(state.filterData.authors, "Билл");
    assert.deepEqual(state.filterData.tags, ["Python"]);
    assert.equal(events.length, 0);
    state.toggleFilterBooks({});
    assert.equal(state.draftFilter.authors, "Билл");
    assert.deepEqual(state.draftFilter.tags, ["Python"]);
});

test("применение фильтра включает набранную тему и не изменяет предыдущую выдачу до отправки", () => {
    const { state, events } = filterForm();
    assert.ok(state.draftFilter);
    state.draftFilter.authors = "Мэттью";
    state.currentTag = " Asyncio ";
    state.doFilter();
    assert.equal(events.length, 1);
    assert.equal(events[0].event, "filtered");
    assert.equal(events[0].value.authors, "Мэттью");
    assert.deepEqual(events[0].value.tags, ["Python", "Asyncio"]);
    assert.ok(events[0].value instanceof FilterBook);
    assert.equal(state.filterData.authors, "Билл");
    assert.deepEqual(state.filterData.tags, ["Python"]);
    assert.equal(state.currentTag, "");
});

test("удаление активного фильтра не применяет оставшийся черновик", () => {
    const { state, events } = filterForm();
    assert.ok(state.draftFilter);
    state.filterData.language = "Русский";
    state.draftFilter.authors = "Другой автор";
    state.currentTag = "Asyncio";
    state.filtersVisible = false;
    state.removeFilter("language");
    assert.equal(events[0].value.language, null);
    assert.equal(events[0].value.authors, "Билл");
    assert.deepEqual(events[0].value.tags, ["Python"]);
});

function historyCatalog(search) {
    const listeners = new Map();
    const pushes = [];
    window.location = { pathname: "/", search };
    window.addEventListener = (name, handler) => listeners.set(name, handler);
    window.removeEventListener = (name, handler) => {
        if (listeners.get(name) === handler) listeners.delete(name);
    };
    history.state = { position: 3, back: "/" };
    history.pushState = (state, _, url) => {
        pushes.push({ state, url });
        window.location.search = new URL(url, "http://localhost").search;
    };
    const params = new URLSearchParams(search);
    const state = {
        ...catalog.data.call({ initialCompactView: false }),
        $route: { query: { ...Object.fromEntries(params), tags: params.getAll("tags") } },
        authScrollToSearchBlock: false,
        initialPerPage: 25,
        replaceThumb: (value) => value,
    };
    for (const [name, method] of Object.entries(catalog.methods)) state[name] = method.bind(state);
    return { state, listeners, pushes };
}

test("каталог открывает страницу и все фильтры из URL без новой записи истории", async () => {
    const { state, pushes } = historyCatalog(
        "?page=3&per-page=50&tags=PostgreSQL&tags=SQL&language=Русский&pages-gt=100"
    );
    let requested;
    api.defaults.adapter = async (config) => {
        requested = new URL(config.url, "http://localhost").searchParams;
        return response({ books: [], totalCount: 200, currentPage: 3, perPage: 50 });
    };
    catalog.mounted.call(state);
    await new Promise(setImmediate);
    assert.equal(requested.get("page"), "3");
    assert.equal(requested.get("per-page"), "50");
    assert.deepEqual(requested.getAll("tags"), ["PostgreSQL", "SQL"]);
    assert.equal(state.filters.language, "Русский");
    assert.equal(state.filters.pagesGt, 100);
    assert.equal(pushes.length, 0);
});

test("назад и вперёд восстанавливают выдачу, фильтры и размер страницы без добавления истории", async () => {
    const { state, listeners, pushes } = historyCatalog("?page=2&per-page=50&tags=PostgreSQL");
    const requests = [];
    api.defaults.adapter = async (config) => {
        const params = new URL(config.url, "http://localhost").searchParams;
        requests.push(params);
        return response({
            books: [],
            totalCount: 200,
            currentPage: Number(params.get("page")),
            perPage: Number(params.get("per-page")),
        });
    };
    catalog.mounted.call(state);
    await new Promise(setImmediate);
    const pop = listeners.get("popstate");
    assert.equal(typeof pop, "function");
    window.location.search = "?page=1&per-page=25";
    await pop();
    assert.deepEqual(state.filters.tags, []);
    assert.equal(state.results.currentPage, 1);
    assert.equal(state.results.perPage, 25);
    window.location.search = "?page=2&per-page=50&tags=PostgreSQL";
    await pop();
    assert.deepEqual(state.filters.tags, ["PostgreSQL"]);
    assert.equal(state.results.currentPage, 2);
    assert.equal(state.results.perPage, 50);
    assert.deepEqual(requests.at(-1).getAll("tags"), ["PostgreSQL"]);
    assert.equal(pushes.length, 0);
    catalog.beforeUnmount.call(state);
    assert.ok(!listeners.has("popstate"));
});

test("повторный запрос не дублирует историю и сохраняет состояние роутера", async () => {
    const { pushes } = historyCatalog("?page=1&per-page=25");
    api.defaults.adapter = async () => response({ books: [] });
    const filter = Object.assign(new FilterBook(), { tags: ["PostgreSQL"] });
    await books.getBooksList(1, filter, 25);
    await books.getBooksList(1, filter, 25);
    assert.equal(pushes.length, 1);
    assert.deepEqual(pushes[0].state, { position: 3, back: "/" });
});

test("кнопка повтора после ошибки истории использует текущий URL, а не старую выдачу", async () => {
    const { pushes } = historyCatalog("?page=1&per-page=50&tags=SQL");
    let requested;
    let retry;
    api.defaults.adapter = async (config) => {
        requested = new URL(config.url, "http://localhost").searchParams;
        return response({ books: [], totalCount: 0, currentPage: 1, perPage: 50 });
    };
    const empty = { inheritAttrs: false, render: () => null };
    const app = createSSRApp(
        {
            ...catalog,
            components: { ...catalog.components, SearchBookForm: empty },
            data: () => ({
                ...catalog.data.call({ initialCompactView: false }),
                results: { books: [], currentPage: 3, perPage: 25, totalCount: 200 },
                loadError: "offline",
            }),
        },
        { authScrollToSearchBlock: false }
    );
    app.component("Skeleton", empty);
    app.component("Paginator", empty);
    app.component("Button", {
        props: ["label"],
        setup(props, { attrs }) {
            if (props.label === "Повторить") retry = attrs.onClick;
            return () => null;
        },
    });
    await renderToString(app);
    await retry();
    assert.equal(requested.get("page"), "1");
    assert.equal(requested.get("per-page"), "50");
    assert.deepEqual(requested.getAll("tags"), ["SQL"]);
    assert.equal(pushes.length, 0);
});

test("запоздавший ответ старого фильтра не перезаписывает новую выдачу", async () => {
    const { state } = historyCatalog("?page=1&per-page=25");
    const pending = [];
    api.defaults.adapter = () => new Promise((resolve) => pending.push(resolve));
    const first = state.getBooksList(1, Object.assign(new FilterBook(), { tags: ["Python"] }));
    await new Promise(setImmediate);
    const second = state.getBooksList(1, Object.assign(new FilterBook(), { tags: ["PostgreSQL"] }));
    await new Promise(setImmediate);
    const latest = { books: [{ id: 291 }], currentPage: 1, perPage: 25 };
    pending[1](response(latest));
    await second;
    pending[0](response({ books: [{ id: 1 }], currentPage: 1, perPage: 25 }));
    await first;
    assert.deepEqual(state.results, latest);
});

function dragSurface(component) {
    const layers = [...component.mixins, component];
    const state = Object.assign({}, ...layers.map((layer) => layer.data()));
    for (const layer of layers) {
        for (const [name, method] of Object.entries(layer.methods)) state[name] = method.bind(state);
    }
    return state;
}

test("лента последних книг перетаскивается мышью и не открывает книгу после движения", () => {
    const state = dragSurface(recentBooks);
    let captured;
    const strip = {
        scrollLeft: 100,
        setPointerCapture: (id) => {
            captured = id;
        },
    };
    const event = { pointerType: "mouse", button: 0, pointerId: 7, clientX: 200, currentTarget: strip };
    state.startDrag(event);
    state.moveDrag({ ...event, clientX: 140 });
    assert.equal(strip.scrollLeft, 160);
    assert.equal(captured, 7);
    state.endDrag();
    let prevented = false;
    state.clickBook({
        preventDefault() {
            prevented = true;
        },
        stopPropagation() {},
    });
    assert.equal(prevented, true);
});

test("малое движение мыши сохраняет клик по книге, touch остаётся нативным", () => {
    const state = dragSurface(recentBooks);
    const strip = {
        scrollLeft: 100,
        setPointerCapture() {
            assert.fail("малое движение не должно захватывать указатель");
        },
    };
    const event = { pointerType: "mouse", button: 0, pointerId: 7, clientX: 200, currentTarget: strip };
    state.startDrag(event);
    state.moveDrag({ ...event, clientX: 198 });
    state.endDrag();
    state.clickBook({
        preventDefault() {
            assert.fail("обычный клик должен работать");
        },
        stopPropagation() {},
    });
    state.startDrag({ ...event, pointerType: "touch" });
    state.moveDrag({ ...event, pointerType: "touch", clientX: 100 });
    assert.equal(strip.scrollLeft, 100);
});

test("мышь листает только свёрнутую полку и скрывает подсказку при движении", () => {
    const state = dragSurface(gallery);
    let hidden = 0;
    state.$refs = {
        bookDetails: {
            hide() {
                hidden++;
            },
        },
    };
    state.detailsBookId = 291;
    const strip = { scrollLeft: 0, setPointerCapture() {} };
    const event = { pointerType: "mouse", button: 0, pointerId: 7, clientX: 200, currentTarget: strip };
    state.startShelfDrag(event);
    state.moveShelfDrag({ ...event, clientX: 100 });
    assert.equal(strip.scrollLeft, 100);
    assert.equal(state.detailsBookId, null);
    assert.equal(hidden, 1);
    state.endDrag();
    state.maximize = true;
    state.startShelfDrag(event);
    state.moveShelfDrag({ ...event, clientX: 50 });
    assert.equal(strip.scrollLeft, 100);
    assert.equal(hidden, 1);
});

test("полка не запрашивает и не показывает подсказку во время перетаскивания", async () => {
    const state = dragSurface(gallery);
    state.dragging = true;
    api.defaults.adapter = () => {
        assert.fail("подсказка при движении не нужна");
    };
    await state.showDetails({ currentTarget: {} }, 291);
    assert.equal(state.currentBook, undefined);
    assert.equal(state.detailsBookId, null);
});

function libraryState(kind, userID = 0) {
    const { pushes, listeners } = historyCatalog("?page=1&per-page=25");
    window.location.pathname = userID
        ? "/admin/users"
        : { favorite: "/favorites", read: "/read", history: "/last-viewed" }[kind];
    const state = { ...libraryBooks.data(), kind, userID };
    state.endpoint = libraryBooks.computed.endpoint.call(state);
    for (const [name, method] of Object.entries(libraryBooks.methods)) state[name] = method.bind(state);
    return { state, pushes, listeners };
}

for (const [kind, endpoint] of [
    ["favorite", "/bookmarks/favorite"],
    ["read", "/bookmarks/read"],
    ["history", "/books/last-viewed"],
]) {
    test(`${kind}: поиск и фильтры отправляются в текущую коллекцию с сохранением размера страницы`, async () => {
        const { state } = libraryState(kind);
        let requested;
        api.defaults.adapter = async (config) => {
            requested = new URL(config.url, "http://localhost");
            return response({ books: [], totalCount: 0, currentPage: 1, perPage: 50 });
        };
        state.page = 3;
        state.perPage = 50;
        const filter = Object.assign(new FilterBook(), {
            search: "Ada",
            authors: "Grace",
            publisher: "Technical",
            language: "Русский",
            pagesGt: 100,
            tags: ["SQL", "Databases"],
        });
        await state.applyFilters(filter);
        assert.equal(requested.pathname, endpoint);
        assert.equal(requested.searchParams.get("page"), "1");
        assert.equal(requested.searchParams.get("per-page"), "50");
        assert.equal(requested.searchParams.get("search"), "Ada");
        assert.equal(requested.searchParams.get("authors"), "Grace");
        assert.equal(requested.searchParams.get("publisher"), "Technical");
        assert.equal(requested.searchParams.get("language"), "Русский");
        assert.equal(requested.searchParams.get("pages-gt"), "100");
        assert.deepEqual(requested.searchParams.getAll("tags"), ["SQL", "Databases"]);
        assert.notEqual(window.location.pathname, "/");
    });

    test(`${kind}: история восстанавливает фильтры, а теги и издатели не переводят в общий каталог`, async () => {
        const { state, pushes } = libraryState(kind);
        api.defaults.adapter = async (config) => {
            assert.equal(new URL(config.url, "http://localhost").pathname, endpoint);
            return response({ books: [], totalCount: 0, currentPage: 2, perPage: 50 });
        };
        window.location.search = "?page=2&per-page=50&tags=SQL&tags=Databases";
        await state.restoreFromUrl();
        assert.deepEqual(state.filters.tags, ["SQL", "Databases"]);
        assert.equal(state.page, 2);
        assert.equal(state.perPage, 50);
        assert.equal(pushes.length, 0);
        window.location.search = "?page=1&per-page=25";
        await state.restoreFromUrl();
        assert.deepEqual(state.filters.tags, []);
        await state.selectTag("Python");
        await state.selectPublisher("Technical");
        assert.equal(state.page, 1);
        assert.equal(state.filters.publisher, "Technical");
        assert.deepEqual(state.filters.tags, ["Python"]);
        await state.clearFilters();
        assert.equal(state.filters.urlParams, "");
    });

    test(`${kind}: фильтрация списка пользователя в админке не меняет URL администратора`, async () => {
        const { state, pushes } = libraryState(kind, 42);
        let requested;
        api.defaults.adapter = async (config) => {
            requested = new URL(config.url, "http://localhost");
            return response({ books: [], totalCount: 0, currentPage: 1, perPage: 25 });
        };
        await state.applyFilters(Object.assign(new FilterBook(), { tags: ["SQL"] }));
        assert.equal(requested.pathname, `/admin/users/42/${kind === "history" ? "last-viewed" : kind}`);
        assert.deepEqual(requested.searchParams.getAll("tags"), ["SQL"]);
        assert.equal(pushes.length, 0);
        assert.equal(window.location.pathname, "/admin/users");
    });
}

test("в каждом личном разделе показана общая панель поиска с обработчиком фильтрации", async () => {
    for (const kind of ["favorite", "read", "history"]) {
        let filtered;
        const empty = { inheritAttrs: false, render: () => null };
        const app = createSSRApp(
            {
                ...libraryBooks,
                components: {
                    ...libraryBooks.components,
                    SearchBookForm: {
                        props: ["filterData"],
                        setup(props, { attrs }) {
                            assert.ok(props.filterData instanceof FilterBook);
                            filtered = attrs.onFiltered;
                            return () => h("form", { "aria-label": "Поиск книг" });
                        },
                    },
                },
            },
            { kind }
        );
        for (const name of ["Button", "Skeleton", "Paginator", "MeterGroup"]) app.component(name, empty);
        const html = await renderToString(app);
        assert.match(html, /Поиск книг/);
        assert.equal(typeof filtered, "function");
    }
});

test("меню библиотеки содержит сердце, отметку прочтения и глаз", () => {
    const state = { favoriteCount: 10, readCount: 11 };
    const favoriteItem = header.computed.favoriteItem.call(state);
    const readItem = header.computed.readItem.call(state);
    const items = header.computed.menuItems.call({
        loggedIn: true,
        user: {},
        themeIcon: "pi pi-circle",
        favoriteItem,
        readItem,
    });
    const links = items
        .find((item) => item.label === "Моя библиотека")
        .items.flat()
        .flatMap((group) => group.items);
    assert.deepEqual(
        links.map((item) => item.icon),
        ["pi pi-heart-fill", "pi pi-check-square", "pi pi-eye"]
    );
});
