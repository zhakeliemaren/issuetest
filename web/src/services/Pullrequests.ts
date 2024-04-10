import { request } from 'umi';

/** listPullRequest 列出pull request GET /cerobot/projects/${param0}/pullrequests */
export async function listPullRequest(
  params: {
    // query
    /** 搜索内容 */
    search?: string;
    /** 排序选项 */
    orderby?: string;
    // path
    name?: string;
  },
  options?: { [key: string]: any },
) {
  const { name: param0, ...queryParams } = params;
  return request<API.PullRequestListResponse>(
    `/cerobot/projects/${param0}/pullrequests`,
    {
      method: 'GET',
      params: {
        ...queryParams,
      },
      ...(options || {}),
    },
  );
}

/** syncPullRequest 列出pull request GET /cerobot/projects/${param0}/pullrequests/sync */
export async function syncPullRequest(
  params: {
    // path
    name?: string;
  },
  options?: { [key: string]: any },
) {
  const { name: param0 } = params;
  return request<API.Response>(`/cerobot/projects/${param0}/pullrequests/sync`, {
    method: 'GET',
    params: { ...params },
    ...(options || {}),
  });
}

/** approvePullRequest 同意一个pull request GET /cerobot/projects/${param0}/pullrequests/${param1}/approve */
export async function approvePullRequest(
  params: {
    // path
    name?: string;
    id?: number;
  },
  options?: { [key: string]: any },
) {
  const { name: param0, id: param1 } = params;
  return request<API.Response>(
    `/cerobot/projects/${param0}/pullrequests/${param1}/approve`,
    {
      method: 'GET',
      params: { ...params },
      ...(options || {}),
    },
  );
}

/** mergePullRequest 合并一个pull request GET /cerobot/projects/${param0}/pullrequests/${param1}/merge */
export async function mergePullRequest(
  params: {
    // path
    name?: string;
    id?: number;
  },
  options?: { [key: string]: any },
) {
  const { name: param0, id: param1 } = params;
  return request<API.Response>(
    `/cerobot/projects/${param0}/pullrequests/${param1}/merge`,
    {
      method: 'GET',
      params: { ...params },
      ...(options || {}),
    },
  );
}

/** closePullRequest 关闭一个pull request GET /cerobot/projects/${param0}/pullrequests/${param1}/close */
export async function closePullRequest(
  params: {
    // path
    name?: string;
    id?: number;
  },
  options?: { [key: string]: any },
) {
  const { name: param0, id: param1 } = params;
  return request<API.Response>(
    `/cerobot/projects/${param0}/pullrequests/${param1}/close`,
    {
      method: 'GET',
      params: { ...params },
      ...(options || {}),
    },
  );
}

/** pressPullRequest 催促一个pull request GET /cerobot/projects/${param0}/pullrequests/${param1}/press */
export async function pressPullRequest(
  params: {
    // path
    name?: string;
    id?: number;
  },
  options?: { [key: string]: any },
) {
  const { name: param0, id: param1 } = params;
  return request<API.Response>(
    `/cerobot/projects/${param0}/pullrequests/${param1}/press`,
    {
      method: 'GET',
      params: { ...params },
      ...(options || {}),
    },
  );
}
