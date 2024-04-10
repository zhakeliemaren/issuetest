import { defineConfig } from 'umi';

export default defineConfig({
  nodeModulesTransform: {
    type: 'none',
  },
  routes: [
    {
      path: '/',
      component: '@/layouts/index',
      routes: [
        { path: '/', redirect: '/obrobot/project' },
        {
          name: '同步工程管理',
          path: '/obrobot/project',
          component: '@/pages/project/index',
          exact: true,
          icon: 'project',
        },
        {
          name: '同步流',
          path: '/obrobot/project/process',
          component: '@/pages/process/index',
          exact: true,
          hideInMenu: true,
        },
        {
          name: 'Pull Request',
          path: '/obrobot/project/pull_request',
          component: '@/pages/pullRequest/index',
          exact: true,
          hideInMenu: true,
        },
        {
          name: 'Github 关联账号管理',
          path: '/obrobot/account',
          component: '@/pages/account/index',
          exact: true,
          icon: 'account',
        },
      ],
    },
  ],
  fastRefresh: {},
  mfsu: {},
  proxy: {
    '/cerobot': {
      // localhost
      target: 'http://0.0.0.0:8000',
      headers: {
        Host: '0.0.0.0:8000',
      }
    },
  },
  favicon: '/assets/favicon.ico'
});
