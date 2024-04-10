import { useState } from 'react';

export default () => {
  const initSearchParams: API.SearchParams = {
    pageSize: 10,
    pageNum: 1,
  }
  const [projectSearchParams, setProjectSearchParams] = useState<API.SearchParams>(initSearchParams);
  return {
    initSearchParams,
    projectSearchParams,
    setProjectSearchParams,
  };
};
