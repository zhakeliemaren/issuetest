import { request } from 'umi';

/** listGithubAccount 展示GitHub账号信息 GET /cerobot/account/github_accounts */
export async function listGithubAccount(
  params: {
    // query
    /** 搜索内容 */
    search?: string;
    /** 排序选项 */
    orderby?: string;
  },
  options?: { [key: string]: any },
) {
  return request<API.AccountListResponse>('/cerobot/account/github_accounts', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  });
}

/** update_github_account 更新一条GitHub账号信息 PUT /cerobot/account/github_accounts */
export async function updateGithubAccount(
  body?: API.UpdateAccountItem,
  options?: { [key: string]: any },
) {
  return request<API.Response>('/cerobot/account/github_accounts', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** addGithubAccount 增加一条GitHub账号信息 POST /cerobot/account/github_accounts */
export async function addGithubAccount(
  body?: API.CreateAccountItem,
  options?: { [key: string]: any },
) {
  return request<API.Response>('/cerobot/account/github_accounts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** deleteGithubAccount 删除一条GitHub账号信息 DELETE /cerobot/account/github_accounts */
export async function deleteGithubAccount(
  params: {
    // query
    /** 阿里域账号 */
    domain?: string;
  },
  options?: { [key: string]: any },
) {
  return request<API.Response>('/cerobot/account/github_accounts', {
    method: 'DELETE',
    params: {
      ...params,
    },
    ...(options || {}),
  });
}

/** listGiteeAccount 展示Gitee账号信息 GET /cerobot/account/gitee_accounts */
export async function listGiteeAccount(
  params: {
    // query
    /** 搜索内容 */
    search?: string;
    /** 排序选项 */
    orderby?: string;
  },
  options?: { [key: string]: any },
) {
  return request<API.AccountListResponse>('/cerobot/account/gitee_accounts', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  });
}

/** update_gitee_account 更新一条Gitee账号信息 PUT /cerobot/account/gitee_accounts */
export async function updateGiteeAccount(
  body?: API.UpdateAccountItem,
  options?: { [key: string]: any },
) {
  return request<API.Response>('/cerobot/account/gitee_accounts', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** addGiteeAccount 增加一条Gitee账号信息 POST /cerobot/account/gitee_accounts */
export async function addGiteeAccount(
  body?: API.CreateAccountItem,
  options?: { [key: string]: any },
) {
  return request<API.Response>('/cerobot/account/gitee_accounts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** deleteGiteeAccount 删除一条Gitee账号信息 DELETE /cerobot/account/gitee_accounts */
export async function deleteGiteeAccount(
  params: {
    // query
    /** 阿里域账号 */
    domain?: string;
  },
  options?: { [key: string]: any },
) {
  return request<API.Response>('/cerobot/account/gitee_accounts', {
    method: 'DELETE',
    params: {
      ...params,
    },
    ...(options || {}),
  });
}
