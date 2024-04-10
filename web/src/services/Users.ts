/* eslint-disable */
import { request } from '@alipay/bigfish';

/** get_user_info 获得用户信息 GET /cerobot/users/info */
export async function getUserInfo(
  params: {
    // query
    token?: any;
  },
  options?: { [key: string]: any },
) {
  return request<API.UserInfoResponse>('/cerobot/users/info', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  });
}
