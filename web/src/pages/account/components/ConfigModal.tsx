import { Modal, message } from 'antd';
import { ProForm, ProFormText } from '@ant-design/pro-form';
import { addGithubAccount, updateGithubAccount } from '@/services/Account';
import useRequest from '@/utils/useRequest';

interface Props {
  visible: boolean;
  onCancel: () => void;
  loadData: () => void;
  itemDetail?: API.GithubAccount;
  modalType: string;
}

const formItemLayout = {
  labelCol: { span: 6 },
  wrapperCol: { span: 16 },
};

export default (props: Props) => {
  const { visible, onCancel, loadData, itemDetail, modalType } = props;
  const [form] = ProForm.useForm();
  const modalTypeTitle = modalType === 'ADD' ? "新建" : '编辑'

  const onSuccess = ({ success }: API.Response) => {
    if (success) {
      message.success(`${modalTypeTitle}关联账户成功`);
      onCancel();
      loadData();
    }
  }

  const { run: handleUpdateAccount, loading: updateLoading } = useRequest(updateGithubAccount, {
    onSuccess: onSuccess,
  });
  const { run: handleAddAccount, loading: addLoading } = useRequest(addGithubAccount, {
    onSuccess: onSuccess,
  });

  const onOk = () => {
    form.validateFields().then((values) => {
      modalType === 'ADD' ? handleAddAccount(values) : handleUpdateAccount({ ...values, id: itemDetail?.id})
    });
  };

  return (
    <Modal
      title={`${modalTypeTitle}关联账号`}
      visible={visible}
      onCancel={onCancel}
      onOk={onOk}
      confirmLoading={addLoading || updateLoading}
      width={800}
    >
      <ProForm
        layout="horizontal"
        submitter={false}
        form={form}
        {...formItemLayout}
        initialValues={itemDetail}
      >
        <ProFormText
          allowClear
          name="domain"
          label="员工号"
          placeholder="请输入"
          rules={[{ required: true, message: '请输入员工号' }]}
        />
        <ProFormText
          allowClear
          name="nickname"
          label="花名"
          placeholder="请输入"
          rules={[{ required: true, message: '请输入花名' }]}
        />
        <ProFormText
          allowClear
          name="account"
          label="Github 账户"
          placeholder="请输入"
          rules={[{ required: true, message: '请输入Github 账户' }]}
        />
        <ProFormText
          allowClear
          name="email"
          label="邮箱"
          placeholder="请输入"
          rules={[{ required: true, message: '请输入邮箱' }]}
        />
      </ProForm>
    </Modal>
  );
};
