import { request } from 'umi';

/** getProject 通过工程名获取一个同步工程 GET /cerobot/projects */
export async function getProject(
  params: {
    // query
    /** 同步工程搜索内容 */
    search?: string;
    /** 排序选项 */
    orderby?: string;
  },
  options?: { [key: string]: any },
) {
  return request<API.ProjectListResponse>('/cerobot/projects', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  });
}

/** createProject 创建一个同步工程 POST /cerobot/projects */
export async function createProject(
  body?: API.CreateProjectItem,
  options?: { [key: string]: any },
) {
  return request<API.Response>('/cerobot/projects', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** deleteProject 通过id删除一个同步工程 DELETE /cerobot/projects */
export async function deleteProject(
  params: {
    // query
    /** 同步工程id */
    id?: number;
  },
  options?: { [key: string]: any },
) {
  return request<API.Response>('/cerobot/projects', {
    method: 'DELETE',
    params: {
      ...params,
    },
    ...(options || {}),
  });
}
