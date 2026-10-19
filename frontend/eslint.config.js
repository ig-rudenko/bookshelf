import js from "@eslint/js";
import prettier from "eslint-config-prettier";
import vue from "eslint-plugin-vue";
import tseslint from "typescript-eslint";

export default [
    {
        ignores: ["dist/**", "node_modules/**", "coverage/**", "*.config.*"],
    },
    js.configs.recommended,
    ...tseslint.configs.recommended,
    ...vue.configs["flat/recommended"].map((config) => ({ ...config, files: ["**/*.vue"] })),
    {
        files: ["tests/**/*.mjs"],
        languageOptions: {
            globals: {
                URL: "readonly",
                URLSearchParams: "readonly",
                setImmediate: "readonly",
                window: "readonly",
                history: "readonly",
            },
        },
    },
    {
        files: ["src/**/*.{ts,vue}", "*.ts"],
        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "module",
            parserOptions: {
                parser: tseslint.parser,
            },
            globals: {
                console: "readonly",
                crypto: "readonly",
                document: "readonly",
                history: "readonly",
                localStorage: "readonly",
                location: "readonly",
                sessionStorage: "readonly",
                setInterval: "readonly",
                setTimeout: "readonly",
                clearInterval: "readonly",
                clearTimeout: "readonly",
                window: "readonly",
            },
        },
        rules: {
            "no-undef": "off",
            "no-control-regex": "off",
            "no-empty": "off",
            "no-unused-expressions": "off",
            "prefer-const": "off",
            "vue/component-definition-name-casing": "off",
            "vue/multi-word-component-names": "off",
            "vue/no-v-html": "off",
            "vue/attributes-order": "off",
            "vue/attribute-hyphenation": "off",
            "vue/first-attribute-linebreak": "off",
            "vue/no-mutating-props": "off",
            "vue/no-required-prop-with-default": "off",
            "vue/no-reserved-component-names": "off",
            "vue/no-reserved-keys": "off",
            "vue/no-side-effects-in-computed-properties": "off",
            "vue/no-unused-components": "off",
            "vue/order-in-components": "off",
            "vue/require-default-prop": "off",
            "vue/require-explicit-emits": "off",
            "vue/require-prop-types": "off",
            "vue/require-v-for-key": "off",
            "vue/return-in-computed-property": "off",
            "vue/valid-v-for": "off",
            "vue/v-on-event-hyphenation": "off",
            "@typescript-eslint/no-explicit-any": "off",
            "@typescript-eslint/ban-ts-comment": "off",
            "@typescript-eslint/no-unused-expressions": "off",
            "@typescript-eslint/no-unsafe-function-type": "off",
            "@typescript-eslint/no-unused-vars": "off",
            "@typescript-eslint/no-wrapper-object-types": "off",
        },
    },
    prettier,
];
