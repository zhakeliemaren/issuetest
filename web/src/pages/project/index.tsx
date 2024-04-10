import { useState } from 'react';
import { history, Link, useModel } from 'umi';
import { PageContainer } from '@ant-design/pro-layout';
import { QueryFilter, ProForm, ProFormText } from '@ant-design/pro-form';
import { List, Button, Popconfirm, message, Card } from 'antd';
import { getProject, deleteProject } from '@/services/Projects';
import useRequest from '@/utils/useRequest';
import ConfigModal from './components/ConfigModal';
import styles from './index.less';

export default () => {
  const { initSearchParams, projectSearchParams, setProjectSearchParams } = useModel('global');
  const [handleType, setHandleType] = useState('ADD');
  const [configModalVisible, setConfigModalVisible] = useState(false);
  const [itemDetail, setItemDetail] = useState<API.Project | undefined>({});
  const [form] = ProForm.useForm();

  const {
    run: fetchProject,
    data: projectData,
    loading,
  } = useRequest(getProject, { defaultParams: { ...projectSearchParams }, manual:  false });

  const loadData = (params?: API.SearchParams) => {
    const currentParams = params || projectSearchParams;
    setProjectSearchParams(currentParams);
    fetchProject(currentParams)
  }

  const { run: handleDelete } = useRequest(deleteProject, {
    onSuccess: ({ success }: API.Response) => {
      if (success) {
        message.success('删除工程成功');
        loadData();
      }
    },
  });

  const handleCondigModal = (type: string, record?: API.Project) => {
    setItemDetail(record);
    setHandleType(type);
    setConfigModalVisible(true);
  };

  const onChange = (pageNum: number, pageSize: number) => {
    loadData({ ...projectSearchParams, pageNum, pageSize  })
  }
  
  return (
    <PageContainer
      className="page_container"
      ghost
      extra={
        <Button
          type="primary"
          onClick={() => handleCondigModal('ADD')}
          key="new"
        >
          新建同步工程
        </Button>
      }
    >
      <Card className="searchCard">
        <QueryFilter
          form={form}
          initialValues={{ search: projectSearchParams?.search }}
          onFinish={(values) => {
            loadData({ ...projectSearchParams, ...values, pageNum: 1 });
          }}
          onReset={() => {
            form.setFieldsValue({
              search: undefined,
            });
            loadData({ ...initSearchParams, search: '' });
          }}
        >
          <ProFormText name="search" label="工程名称" />
        </QueryFilter>
      </Card>
      <Card>
        <List
          className={styles.projectList}
          dataSource={projectData?.data?.list || []}
          rowKey="id"
          loading={loading}
          pagination={{
            current: projectSearchParams.pageNum,
            pageSize: projectSearchParams.pageSize,
            defaultPageSize: 10,
            showSizeChanger: false,
            total: projectData?.data?.total,
            showTotal: (total) => `共 ${total} 条`,
            onChange,
          }}
          renderItem={(item: API.Project) => (
            <List.Item
              className={styles.projectRow}
              actions={[
                <Button
                  type="primary"
                  onClick={() => handleCondigModal('DETAIL', item)}
                  key="attr"
                >
                  属性
                </Button>,
                <Button
                  type="primary"
                  onClick={() =>
                    history.push(
                      `/obrobot/project/pull_request?name=${item.name}`,
                    )
                  }
                  key="pull_request"
                >
                  PullRequest
                </Button>,
                <Popconfirm
                  title="确认删除吗?"
                  onConfirm={() => handleDelete({ id: item.id })}
                >
                  <Button type="primary" key="delete">
                    删除
                  </Button>
                </Popconfirm>,
              ]}
            >
              <List.Item.Meta
                title={
                  <Link
                    className={styles.listTitle}
                    to={`/obrobot/project/process?name=${item.name}`}
                  >
                    {item.name}
                  </Link>
                }
              />
            </List.Item>
          )}
        />
      </Card>

      {configModalVisible && (
        <ConfigModal
          visible={configModalVisible}
          onCancel={() => setConfigModalVisible(false)}
          loadData={loadData}
          handleType={handleType}
          itemDetail={itemDetail}
        />
      )}
    </PageContainer>
  );
};
