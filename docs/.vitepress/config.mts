import { defineConfig } from "vitepress";

export default defineConfig({
  title: "ModelCub",
  description: "Open-source, local-first MLOps toolkit for computer vision",

  cleanUrls: true,

  head: [
    ["link", { rel: "icon", type: "image/svg+xml", href: "/logo.svg" }],
    ["meta", { name: "theme-color", content: "#3eaf7c" }],
  ],

  markdown: {
    lineNumbers: true,
  },

  themeConfig: {
    logo: "/logo.svg",
    siteTitle: "ModelCub",

    nav: [
      { text: "Guide", link: "/guide/introduction" },
      { text: "API", link: "/api/overview" },
      { text: "About", link: "/about/mission" },
    ],

    sidebar: {
      "/guide/": [
        {
          text: "Getting Started",
          items: [
            { text: "Introduction", link: "/guide/introduction" },
            { text: "Installation", link: "/guide/installation" },
            { text: "Quick Start", link: "/guide/quick-start" },
          ],
        },
      ],
      "/api/": [
        {
          text: "API Reference",
          items: [
            { text: "Overview", link: "/api/overview" },
            { text: "Project", link: "/api/project" },
          ],
        },
      ],
      "/about/": [
        {
          text: "About",
          items: [
            { text: "Mission", link: "/about/mission" },
            { text: "Philosophy", link: "/about/philosophy" },
          ],
        },
      ],
    },

    socialLinks: [
      { icon: "github", link: "https://github.com/yourusername/modelcub" },
    ],

    footer: {
      message: "Released under the MIT License.",
      copyright: "Copyright © 2024-present ModelCub",
    },

    search: {
      provider: "local",
    },
  },
});
