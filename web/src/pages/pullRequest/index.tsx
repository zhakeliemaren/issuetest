import { useState } from 'react';
import { history, useModel } from 'umi';
import type { ColumnsType } from 'antd/es/table';
import { PageContainer } from '@ant-design/pro-layout';
import { QueryFilter, ProFormText } from '@ant-design/pro-form';
import { Button, Table, Card, Modal, Divider, Tooltip, message } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import useRequest from '@/utils/useRequest';
import {
  listPullRequest,
  approvePullRequest,
  mergePullRequest,
  pressPullRequest,
} from '@/services/Pullrequests';

interface Props {
  location?: {
    query?: {
      name?: string;
    };
  };
}

export default (props: Props) => {
  const { name } = props?.location?.query || {};
  const { initSearchParams } = useModel('global');
  const [searchParams, setSearchParams] = useState<API.SearchParams>(initSearchParams);

  const {
    run: fetchPullRequest,
    data: pullRequestData,
    loading,
  } = useRequest(listPullRequest, { defaultParams: { ...searchParams, name }, manual: false  });

  const loadData = (params?: API.SearchParams) => {
    const currentParams = params || searchParams;
    setSearchParams(currentParams);
    fetchPullRequest({ ...currentParams, name });
  }

  const { run: handleApprove } = useRequest(approvePullRequest);
  const { run: handleMerge } = useRequest(mergePullRequest);
  const { run: handlePress } = useRequest(pressPullRequest);

  const handleActions = (id: number, type: string) => {
    let request: any;
    switch (type) {
      case '同意':
        request = () => handleApprove({ name, id });
        break;
      case '催促':
        request = () => handlePress({ name, id });
        break;
      case '合并':
        request = () => handleMerge({ name, id });
        break;
      default:
        break;
    }
    Modal.confirm({
      title: `确定对 PullRequest: ${id} 执行${type}操作吗?`,
      icon: <ExclamationCircleOutlined />,
      onOk: async () => {
        request().then(({ success }: API.Response) => {
          if (success) {
            message?.destroy();
            message.success('操作成功');
            loadData();
          }
        })
      },
    });
  };

  const onTableChange = ({ current, pageSize }: { current: number, pageSize: number }) => {
    loadData({ ...searchParams, pageNum: current, pageSize });
  }

  const columns: ColumnsType<API.PullRequest> = [
    {
      title: 'ID',
      dataIndex: 'id',
      render: (text) => text || '-',
    },
    {
      title: '题目',
      dataIndex: 'title',
      render: (text) =>
        text ? (
          <Tooltip placement="topLeft" title={text}>
            <div className="ellipsis">{text}</div>
          </Tooltip>
        ) : (
          '-'
        ),
    },
    {
      title: '操作',
      fixed: 'right',
      width: 300,
      dataIndex: 'handle',
      render: (text, record) => [
        <a href={record.address} target="_blank" key="detail">
          详情
        </a>,
        <Divider type="vertical" key="divider-1" />,
        <a onClick={() => handleActions(record.id, '同意')} key="argee">
          同意
        </a>,
        <Divider type="vertical" key="divider-2" />,
        <a onClick={() => handleActions(record.id, '催促')} key="urged">
          催促
        </a>,
        <Divider type="vertical" key="divider-3" />,
        <a onClick={() => handleActions(record.id, '合并')} key="merge">
          合并
        </a>,
      ],
    },
  ];

  return (
    <PageContainer
      ghost
      header={{ title: name }}
      extra={
        <Button onClick={() => history.goBack()} key="go_back">
          返回
        </Button>
      }
    >
      <Card className="searchCard">
        <QueryFilter
          onFinish={(values) => {
            loadData({ ...searchParams, ...values, pageNum: 1 });
          }}
          onReset={() => {
            loadData({ ...initSearchParams });
          }}
        >
          <ProFormText name="search" label="关键词" />
        </QueryFilter>
      </Card>
      <Card>
        <Table
          columns={columns}
          dataSource={pullRequestData?.data?.list || []}
          loading={loading}
          rowKey="id"
          onChange={onTableChange}
          pagination={{
            current: searchParams?.pageNum,
            pageSize: 10,
            defaultPageSize: 10,
            showSizeChanger: false,
            total: pullRequestData?.data?.total,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>
    </PageContainer>
  );
};
