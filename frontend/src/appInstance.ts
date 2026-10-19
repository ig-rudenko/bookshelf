import { createApp } from "vue";
import { definePreset } from "@primeuix/themes";
import PrimeVue from "primevue/config";

import Material from "@primeuix/themes/material";

import App from "@/App.vue";

const MyPreset = definePreset(Material, {
    semantic: {
        primary: {
            50: "{indigo.50}",
            100: "{indigo.100}",
            200: "{indigo.200}",
            300: "{indigo.300}",
            400: "{indigo.400}",
            500: "{indigo.500}",
            600: "{indigo.600}",
            700: "{indigo.700}",
            800: "{indigo.800}",
            900: "{indigo.900}",
            950: "{indigo.950}",
        },
        colorScheme: {
            light: {
                primary: {
                    color: "{indigo.600}",
                    contrastColor: "{surface.0}",
                    hoverColor: "{indigo.700}",
                    activeColor: "{indigo.800}",
                },
            },
            dark: {
                surface: {
                    0: "#ffffff",
                    50: "#f8f9fb",
                    100: "#edf0f5",
                    200: "#dee3ea",
                    300: "#c5ccd5",
                    400: "#a5afbd",
                    500: "#76818f",
                    600: "#56616f",
                    700: "#343c46",
                    800: "#252a31",
                    900: "#1c1f23",
                    950: "#141619",
                },
                primary: {
                    color: "#b0baf2",
                    contrastColor: "{surface.950}",
                    hoverColor: "#c8cff8",
                    activeColor: "#9ca9e8",
                },
                formField: { background: "{surface.900}", borderColor: "{surface.700}" },
            },
        },
        formField: { borderRadius: "0.5rem" },
        content: { borderRadius: "0.5rem" },
    },
    components: {
        button: {
            root: { borderRadius: "0.5rem" },
            colorScheme: {
                dark: {
                    root: {
                        primary: {
                            background: "{primary.color}",
                            hoverBackground: "{primary.hover.color}",
                            activeBackground: "{primary.active.color}",
                            borderColor: "{primary.color}",
                            hoverBorderColor: "{primary.hover.color}",
                            activeBorderColor: "{primary.active.color}",
                            color: "{surface.950}",
                            hoverColor: "{surface.950}",
                            activeColor: "{surface.950}",
                        },
                    },
                    outlined: { primary: { borderColor: "{surface.600}" } },
                },
            },
        },
    },
});

export const app = createApp(App);
app.use(PrimeVue, {
    ripple: true,
    theme: {
        preset: MyPreset,
        options: {
            darkModeSelector: ".dark",
        },
    },
});
