import { defineI18nUI } from 'fumadocs-ui/i18n';

export const i18n = defineI18nUI(
  {
    defaultLanguage: 'en',
    languages: ['en', 'pt-br', 'es', 'zh-cn'],
    hideLocale: 'default-locale',
  },
  {
    en: {
      displayName: 'English',
    },
    'pt-br': {
      displayName: 'Português (Brasil)',
      'Search(search dialog)': 'Pesquisar',
      'Search(search trigger)': 'Pesquisar',
      'No results found(search dialog)': 'Nenhum resultado encontrado',
      'On this page(table of contents)': 'Nesta página',
      'No Headings(table of contents)': 'Sem títulos',
      'Last updated on(page footer)': 'Última atualização em',
      'Choose a language(language switcher)': 'Escolha um idioma',
      'Next Page(pagination)': 'Próxima página',
      'Previous Page(pagination)': 'Página anterior',
      'Edit on GitHub(edit page)': 'Editar no GitHub',
    },
    es: {
      displayName: 'Español',
      'Search(search dialog)': 'Buscar',
      'Search(search trigger)': 'Buscar',
      'No results found(search dialog)': 'No se encontraron resultados',
      'On this page(table of contents)': 'En esta página',
      'No Headings(table of contents)': 'Sin encabezados',
      'Last updated on(page footer)': 'Última actualización el',
      'Choose a language(language switcher)': 'Elegir un idioma',
      'Next Page(pagination)': 'Página siguiente',
      'Previous Page(pagination)': 'Página anterior',
      'Edit on GitHub(edit page)': 'Editar en GitHub',
    },
    'zh-cn': {
      displayName: '简体中文',
      'Search(search dialog)': '搜索',
      'Search(search trigger)': '搜索',
      'No results found(search dialog)': '未找到结果',
      'On this page(table of contents)': '本页内容',
      'No Headings(table of contents)': '无标题',
      'Last updated on(page footer)': '最后更新于',
      'Choose a language(language switcher)': '选择语言',
      'Next Page(pagination)': '下一页',
      'Previous Page(pagination)': '上一页',
      'Edit on GitHub(edit page)': '在 GitHub 上编辑',
    },
  }
);
