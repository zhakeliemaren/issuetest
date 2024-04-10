import { Modal, Form, message, Button, Space } from 'antd';
import { ProForm, ProFormText } from '@ant-design/pro-form';
import { formItemLayout } from '@/constants';
import { createProject } from '@/services/Projects';
import useRequest from '@/utils/useRequest';

interface Props {
  visible: boolean;
  onCancel: () => void;
  loadData: () => void;
  handleType: string;
  itemDetail?: API.Project;
}

const { Item } = Form;

export default (props: Props) => {
  const { visible, onCancel, loadData, handleType, itemDetail } = props;
  const isDetail = handleType === 'DETAIL';
  const [form] = ProForm.useForm();

  const { run: handleCreateProject, loading } = useRequest(createProject, {
    onSuccess: ({ success }: API.Response) => {
      if (success) {
        message.success('新建工程成功');
        onCancel();
        loadData();
      }
    },
  });

  const onOk = () => {
    form.validateFields().then((values) => {
      handleCreateProject(values);
    });
  };

  return (
    <Modal
      title="新建同步工程"
      visible={visible}
      onCancel={onCancel}
      onOk={onOk}
      width={600}
      confirmLoading={loading}
      footer={
        isDetail ? <Button onClick={onCancel} >关闭</Button> :
        <>
          <Button onClick={onCancel} >取消</Button>
          <Button onClick={onOk} type="primary" >确定</Button>
        </>
      }
    >
      <ProForm
        layout="horizontal"
        submitter={false}
        form={form}
        {...formItemLayout}
      >
        {isDetail
          ? [
              <Item key="name" label="名字">
                {itemDetail?.name || '-'}
              </Item>,
              <Item key="gitlab_address" label="Gitlab 地址（内部仓库）">
                {itemDetail?.gitlab_address || '-'}
              </Item>,
              <Item key="github_address" label="Github 地址">
                {itemDetail?.github_address || '-'}
              </Item>,
              <Item key="gitee_address" label="Gitee 地址">
                {itemDetail?.gitee_address || '-'}
              </Item>,
              <Item key="code_china_address" label="CodeChina 地址">
                {itemDetail?.code_china_address || '-'}
              </Item>,
               <Item key="gitlink_address" label="Gitlink 地址">
               {itemDetail?.gitlink_address || '-'}
             </Item>,
            ]
          : [
              <ProFormText
                allowClear
                name="name"
                label="名字"
                placeholder="请输入"
                disabled={isDetail}
                rules={[{ required: true, message: '请输入名字' }]}
              />,
              <ProFormText
                allowClear
                name="gitlab_address"
                label="Gitlab 地址"
                placeholder="请输入"
                disabled={isDetail}
              />,
              <ProFormText
                allowClear
                name="github_address"
                label="Github 地址"
                placeholder="请输入"
                disabled={isDetail}
                // rules={[{ required: true, message: '请输入 Github 地址' }]}
              />,
              <ProFormText
                allowClear
                name="gitee_address"
                label="Gitee 地址"
                disabled={isDetail}
                placeholder="请输入"
              />,
              <ProFormText
                allowClear
                name="code_china_address"
                label="CodeChina 地址"
                disabled={isDetail}
                placeholder="请输入"
              />,
              <ProFormText
                allowClear
                name="gitlink_address"
                label="Gitlink 地址"
                disabled={isDetail}
                placeholder="请输入"
              />,
            ]}
      </ProForm>
    </Modal>
  );
};
