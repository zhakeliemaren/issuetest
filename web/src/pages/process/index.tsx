import { useState } from 'react';
import { history, useModel } from 'umi';
import type { ColumnsType } from 'antd/es/table';
import { PageContainer } from '@ant-design/pro-layout';
import { QueryFilter, ProFormText } from '@ant-design/pro-form';
import { Button, Table, Card, Popconfirm, message, Tag, Divider, Input, Form, Row, Col } from 'antd';
import ConfigModal from './components/ConfigModal';
import LogModal from './components/LogModal';
import { listJobs, deleteJob, startJob, stopJob, setJobCommit } from '@/services/Jobs';
import useRequest from '@/utils/useRequest';

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
  const [configModalVisible, setConfigModalVisible] = useState(false);
  const [logModalVisible, setLogModalVisible] = useState(false);
  const [selectId, setSelectId] = useState(undefined);

  const {
    run: fetchJobs,
    data: jobsData,
    loading,
  } = useRequest(listJobs, { defaultParams: { ...searchParams, name}, manual: false });
  const loadData = (params?: API.SearchParams) => {
    const currentParams = params || searchParams;
    setSearchParams(currentParams);
    fetchJobs({ ...currentParams, name });
  };

  const { run: handleDelete } = useRequest(deleteJob, {
    onSuccess: ({ success }: API.Response) => {
      if (success) {
        message.success('删除同步流成功');
        loadData();
      }
    },
  });

  const { run: handleStart } = useRequest(startJob, {
    onSuccess: ({ success }: API.Response) => {
      if(success){
        message.success('操作开启成功')
        loadData();
      }
    }
  });
  
  const { run: handleStop } = useRequest(stopJob, {
    onSuccess: ({ success }: API.Response) => {
      if(success){
        message.success('操作关闭成功')
        loadData();
      }
    }
  });

  const { run: handleSetCommit } = useRequest(setJobCommit, {
    onSuccess: ({ success }: API.Response) => {
      if(success){
        message.success('修改 commit 成功')
        loadData();
      }
    }
  });

  const handleSwitch = (id: number, status: number) => {
    if(status === 1){
      handleStop({ id, name });
    } else {
      handleStart({ id, name });
    }
  }

  const handleCommitChange = (value: string, text: string, id: number) => {
    if(value === text) return;
    handleSetCommit({ id, name, commit: value })
  }

  const onTableChange = ({ current, pageSize }: { current: number, pageSize: number }) => {
    loadData({ ...searchParams, pageNum: current, pageSize });
  }

  const expandedRowRender = (record: API.Job) => {
    const subContent = [
      {
        title: '同步方式',
        content: record.type || '-',
      },
      {
        title: '主仓库',
        content: record.base || '-',
      },
      {
        title: 'commit',
        content: record.type === 'TwoWay' ? record.commit : <Input defaultValue={record.commit} placeholder="请输入 commit 信息" onBlur={(e) => handleCommitChange(e.target.value, record.commit, record.id)} />
      },
    ];

    return (
      <Card>
        <Form>
          <Row>
            {subContent.map((item) => (
              <Col key={item.title} span={8}>
                <Form.Item label={item.title}> {item.content} </Form.Item>
              </Col>
            ))}
          </Row>
        </Form>
      </Card>
    );
  };

  const columns: ColumnsType<API.Job> = [
    {
      title: 'Gitlab 分支',
      dataIndex: 'gitlab_branch',
      render: (text) => text || '-',
    },
    {
      title: 'Github 分支',
      dataIndex: 'github_branch',
      render: (text) => text || '-',
    },
    {
      title: 'Gitee 分支',
      dataIndex: 'gitee_branch',
      render: (text) => text || '-',
    },
    {
      title: 'CodeChina 分支',
      dataIndex: 'code_china_branch',
      render: (text) => text || '-',
    },
    {
      title: 'Gitlink 分支',
      dataIndex: 'gitlink_branch',
      render: (text) => text || '-',
    },
    {
      title: '同步状态',
      dataIndex: 'status',
      render: (text) =>
        text ? <Tag color="success">成功</Tag> : <Tag color="error">失败</Tag>,
    },
    
    {
      title: '操作',
      dataIndex: 'handle',
      fixed: 'right',
      width: 180,
      render: (text, record) => {
        const actionTitle = record.status === 1 ? '关闭' : '开启';
        return (
          <>
            <Popconfirm
              title={`确认${actionTitle}吗?`}
              onConfirm={() => handleSwitch(record.id, record.status)}
            >
              <a>{actionTitle}</a>
            </Popconfirm>
            <Divider type="vertical" />
            <a onClick={() => { setLogModalVisible(true); setSelectId(record.id)}} >查看日志</a>
            <Divider type="vertical" />
            <Popconfirm
              title="确认删除吗?"
              onConfirm={() => handleDelete({ id: record.id, name })}
            >
              <a>删除</a>
            </Popconfirm>
          </>
        )
      }
    },
  ];

  const extra = [
    <Button
      type="primary"
      onClick={() => setConfigModalVisible(true)}
      key="new"
    >
      新建同步分支
    </Button>,
    <Button onClick={() => history.goBack()} key="go_back">
      返回
    </Button>,
  ];

  return (
    <PageContainer ghost header={{ title: name }} extra={extra}>
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
          loading={loading}
          columns={columns}
          dataSource={jobsData?.data?.list || []}
          rowKey="id"
          onChange={onTableChange}
          expandable={{ expandedRowRender }}
          pagination={{
            current: searchParams?.pageNum,
            pageSize: 10,
            defaultPageSize: 10,
            showSizeChanger: false,
            total: jobsData?.data?.total,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>
      {configModalVisible && (
        <ConfigModal
          visible={configModalVisible}
          onCancel={() => setConfigModalVisible(false)}
          loadData={loadData}
          name={name}
        />
      )}
      {
        logModalVisible && (
          <LogModal
            visible={logModalVisible}
            onCancel={() => setLogModalVisible(false)}
            id={selectId}
            name={name}
          />
        )
      }
    </PageContainer>
  );
};
