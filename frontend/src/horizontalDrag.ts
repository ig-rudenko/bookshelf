import { defineComponent } from "vue";

export default defineComponent({
    data() {
        return {
            dragStartX: null as number | null,
            dragScrollLeft: 0,
            dragging: false,
            dragged: false,
        };
    },
    methods: {
        startDrag(event: PointerEvent) {
            if (event.pointerType !== "mouse" || event.button !== 0) return;
            this.dragStartX = event.clientX;
            this.dragScrollLeft = (event.currentTarget as HTMLElement).scrollLeft;
            this.dragged = false;
        },
        moveDrag(event: PointerEvent) {
            if (this.dragStartX === null) return;
            const distance = event.clientX - this.dragStartX;
            if (!this.dragging && Math.abs(distance) < 6) return;
            const strip = event.currentTarget as HTMLElement;
            if (!this.dragging) strip.setPointerCapture(event.pointerId);
            this.dragging = true;
            this.dragged = true;
            strip.scrollLeft = this.dragScrollLeft - distance;
        },
        endDrag() {
            this.dragStartX = null;
            this.dragging = false;
        },
        clickBook(event: MouseEvent) {
            if (!this.dragged) return;
            event.preventDefault();
            event.stopPropagation();
            this.dragged = false;
        },
    },
});
