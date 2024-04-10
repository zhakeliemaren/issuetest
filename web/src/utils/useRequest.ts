/* eslint-disable react-hooks/rules-of-hooks */
import { useRequest } from 'umi';
import type { CombineService, BaseOptions } from '@ahooksjs/use-request/lib/types';
import { notification, message } from 'antd';

const handleResponseError = (desc: string, msg?: string | undefined) => {
  notification.error({
    description: desc,
    message: msg || '请求错误',
  });
};

interface Options<R = any, P extends any[] = any> extends BaseOptions<R, P> {
  skipError?: boolean; // 接口正常(status code === 200)返回时, 跳过 success 为 false 的报错;
  skipStatusError?: boolean; // 接口不正常(status code !== 200 )返回时, 跳过状态码报错
}

/**
 * 异常处理程序
 */

const errorHandle = (error: any, onError: any, skipStatusError?: boolean) => {
  const { response, data } = error;
  if (onError) {
    onError(error);
  }

  if (!skipStatusError) {
    if (response && response.status) {
      handleResponseError(data?.msg || response.statusText);
    }
  }

  if (!response) {
    handleResponseError('您的网络发生异常，无法连接服务器', '网络异常');
  }

  return response;
};

const successHandle = (onSuccess: any, res: any, arg: any, skipError?: boolean, ) => {
  if (onSuccess) {
    onSuccess(res, ...arg);
  }
  if (!skipError && !res.success) {
    handleResponseError(res.msg || res.data?.message);
  }
};

const request: any = <R, P extends any[]>(service: CombineService<R, P>, options?: Options<R, P>) => {
  return useRequest(service, {
    manual: true,
    throwOnError: false,
    formatResult: (result: any) => result,
    ...options,
    onError: (error: any) => errorHandle(error, options?.onError, options?.skipStatusError),
    onSuccess: (res: any, ...arg: any[]) => successHandle(options?.onSuccess, res, arg, options?.skipError, ),
  });
};

export default request;
