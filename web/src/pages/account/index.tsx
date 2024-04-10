import { useState } from 'react';
import { useModel } from 'umi';
import type { ColumnsType } from 'antd/es/table';
import { PageContainer } from '@ant-design/pro-layout';
import { QueryFilter, ProFormText } from '@ant-design/pro-form';
import { Button, Table, Card, Popconfirm, Divider, message } from 'antd';
import ConfigModal from './components/ConfigModal';
import { listGithubAccount, deleteGithubAccount } from '@/services/Account';
import useRequest from '@/utils/useRequest';

export default () => {
  const [configModalVisible, setConfigModalVisible] = useState(false);
  const [modalType, setModalType] = useState('ADD');
  const [itemDetail, setItemDetail] = useState<API.GithubAccount>({});
  const { initSearchParams } = useModel('global');
  const [searchParams, setSearchParams] = useState<API.SearchParams>(initSearchParams);

  const {
    run: fetchAccount,
    data: accountData,
    loading,
  } = useRequest(listGithubAccount, { manual: false });
  const loadData = (params?: API.SearchParams) => {
    const currentParams = params || searchParams;
    setSearchParams(currentParams);
    fetchAccount(currentParams);
  }

  const { run: handleDelete } = useRequest(deleteGithubAccount, {
    onSuccess: ({ success }: API.Response) => {
      if (success) {
        message.success('删除账户成功');
        loadData();
      }
    },
  });

  const onTableChange = ({ current, pageSize }: { current: number, pageSize: number }) => {
    loadData({ ...searchParams, pageNum: current, pageSize });
  }

  const columns: ColumnsType<API.GithubAccount> = [
    {
      title: '员工号',
      dataIndex: 'domain',
      render: (text) => text || '-',
    },
    {
      title: '花名',
      dataIndex: 'nickname',
      render: (text) => text || '-',
    },
    {
      title: 'Github 账户',
      dataIndex: 'account',
      render: (text) => text || '-',
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      render: (text) => text || '-',
    },
    {
      title: '操作',
      dataIndex: 'handle',
      fixed: 'right',
      width: 120,
      render: (text, record) => [
        <a
          onClick={() => {
            setModalType('EDIT');
            setItemDetail(record);
            setConfigModalVisible(true);
          }}
        >
          编辑
        </a>,
        <Divider type="vertical" />,
        <Popconfirm
          title="确认删除吗?"
          onConfirm={() => handleDelete({ id: record.id })}
        >
          <a>删除</a>
        </Popconfirm>,
      ],
    },
  ];

  return (
    <PageContainer
      ghost
      extra={
        <Button type="primary" onClick={() => { setConfigModalVisible(true); setModalType('ADD'); }}>
          新建关联账号
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
          <ProFormText name="search" label="员工号" />
        </QueryFilter>
      </Card>
      <Card>
        <Table
          columns={columns}
          loading={loading}
          dataSource={accountData?.data?.list || []}
          rowKey="id"
          onChange={onTableChange}
          pagination={{
            current: searchParams?.pageNum,
            pageSize: 10,
            defaultPageSize: 10,
            showSizeChanger: false,
            total: accountData?.data?.total,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>
      {configModalVisible && (
        <ConfigModal
          visible={configModalVisible}
          onCancel={() => {
            setItemDetail({});
            setConfigModalVisible(false);
          }}
          loadData={loadData}
          itemDetail={itemDetail}
          modalType={modalType}
        />
      )}
    </PageContainer>
  );
};
