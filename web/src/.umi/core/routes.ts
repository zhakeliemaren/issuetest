// @ts-nocheck
import React from 'react';
import { ApplyPluginsType } from '/root/ob-repository-synchronize/web/node_modules/umi/node_modules/@umijs/runtime';
import * as umiExports from './umiExports';
import { plugin } from './plugin';

export function getRoutes() {
  const routes = [
  {
    "path": "/",
    "component": require('@/layouts/index').default,
    "routes": [
      {
        "path": "/",
        "redirect": "/obrobot/project",
        "exact": true
      },
      {
        "name": "同步工程管理",
        "path": "/obrobot/project",
        "component": require('@/pages/project/index').default,
        "exact": true,
        "icon": "project"
      },
      {
        "name": "同步流",
        "path": "/obrobot/project/process",
        "component": require('@/pages/process/index').default,
        "exact": true,
        "hideInMenu": true
      },
      {
        "name": "Pull Request",
        "path": "/obrobot/project/pull_request",
        "component": require('@/pages/pullRequest/index').default,
        "exact": true,
        "hideInMenu": true
      },
      {
        "name": "Github 关联账号管理",
        "path": "/obrobot/account",
        "component": require('@/pages/account/index').default,
        "exact": true,
        "icon": "account"
      }
    ]
  }
];

  // allow user to extend routes
  plugin.applyPlugins({
    key: 'patchRoutes',
    type: ApplyPluginsType.event,
    args: { routes },
  });

  return routes;
}
