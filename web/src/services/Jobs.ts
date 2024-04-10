import { request } from 'umi';

/** listJobs 列出所有同步流 GET /cerobot/projects/${param0}/jobs */
export async function listJobs(
  params: {
    // query
    /** 同步工程搜索内容 */
    search?: string;
    /** 排序选项 */
    orderby?: string;
    // path
    name?: string;
  },
  options?: { [key: string]: any },
) {
  const { name: param0, ...queryParams } = params;
  return request<API.JobListResponse>(`/cerobot/projects/${param0}/jobs`, {
    method: 'GET',
    params: {
      ...queryParams,
    },
    ...(options || {}),
  });
}

/** createJob 创建一个同步流 POST /cerobot/projects/${param0}/jobs */
export async function createJob(
  params: {
    // path
    name?: string;
  },
  body?: API.CreateJobItem,
  options?: { [key: string]: any },
) {
  const { name: param0 } = params;
  return request<API.Response>(`/cerobot/projects/${param0}/jobs`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...params },
    data: body,
    ...(options || {}),
  });
}

/** deleteJob 通过id删除一个同步流 DELETE /cerobot/projects/${param0}/jobs */
export async function deleteJob(
  params: {
    // query
    /** 同步流id */
    id?: number;
    // path
    name?: string;
  },
  options?: { [key: string]: any },
) {
  const { name: param0, ...queryParams } = params;
  return request<API.Response>(`/cerobot/projects/${param0}/jobs`, {
    method: 'DELETE',
    params: {
      ...queryParams,
    },
    ...(options || {}),
  });
}
/** start_job 开启一个同步流 PUT /cerobot/projects/${param0}/jobs/${param1}/start */
export async function startJob(
  params: {
    // path
    name?: string;
    id?: number;
  },
  options?: { [key: string]: any },
) {
  const { name: param0, id: param1 } = params;
  return request<API.Response>(`/cerobot/projects/${param0}/jobs/${param1}/start`, {
    method: 'PUT',
    params: { ...params },
    ...(options || {}),
  });
}

/** stop_job 停止一个同步流 PUT /cerobot/projects/${param0}/jobs/${param1}/stop */
export async function stopJob(
  params: {
    // path
    name?: string;
    id?: number;
  },
  options?: { [key: string]: any },
) {
  const { name: param0, id: param1 } = params;
  return request<API.Response>(`/cerobot/projects/${param0}/jobs/${param1}/stop`, {
    method: 'PUT',
    params: { ...params },
    ...(options || {}),
  });
}

/** set_job_commit 通过id设置一个同步流的commit PUT /cerobot/projects/${param0}/jobs/${param1}/set_commit */
export async function setJobCommit(
  params: {
    // query
    /** commit */
    commit?: string;
    // path
    name?: string;
    id?: number;
  },
  options?: { [key: string]: any },
) {
  const { name: param0, id: param1, ...queryParams } = params;
  return request<API.Response>(`/cerobot/projects/${param0}/jobs/${param1}/set_commit`, {
    method: 'PUT',
    params: {
      ...queryParams,
    },
    ...(options || {}),
  });
}

/** get_job_log 列出所有同步流 GET /cerobot/projects/${param0}/jobs/${param1}/logs */
export async function getJobLog(
  params: {
    // path
    name?: string;
    id?: number;
  },
  options?: { [key: string]: any },
) {
  const { name: param0, id: param1 } = params;
  return request<API.LogListResponse>(`/cerobot/projects/${param0}/jobs/${param1}/logs`, {
    method: 'GET',
    params: { ...params },
    ...(options || {}),
  });
}
