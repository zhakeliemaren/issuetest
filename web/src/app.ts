// 运行时配置
import type { RequestConfig } from 'umi';

export const request: RequestConfig = {
  errorConfig: {
    adaptor: () => {
      return {
        showType: 0
      }
    },
  },
  requestInterceptors: [
    (url, options) => {
      return {
        url: url,
        options: { ...options },
      };
    },
  ],
};
