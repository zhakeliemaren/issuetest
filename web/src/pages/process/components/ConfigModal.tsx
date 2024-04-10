import { useState } from 'react';
import { Modal, message } from 'antd';
import { ProForm, ProFormText, ProFormSelect } from '@ant-design/pro-form';
import { formItemLayout } from '@/constants';
import { createJob } from '@/services/Jobs';
import useRequest from '@/utils/useRequest';

interface Props {
  visible: boolean;
  onCancel: () => void;
  loadData: () => void;
  name?: string;
}

const syncWay = [
  { label: 'OneWay', value: 'OneWay' },
  { label: 'TwoWay', value: 'TwoWay' },
]

const gitType = [
  { label: 'GitHub', value: 'GitHub' },
  { label: 'Gitee', value: 'Gitee' },
]

export default (props: Props) => {
  const { visible, onCancel, loadData, name } = props;
  const [form] = ProForm.useForm();
  const [selectType, setSelectType] = useState('');

  const { run: handleCreateJob, loading } = useRequest(createJob, {
    onSuccess: ({ success }: API.Response) => {
      if (success) {
        message.success('新建同步流成功');
        onCancel();
        loadData();
      }
    },
    skipErrorHandler: true,
  });

  const onOk = () => {
    form.validateFields().then((values) => {
      handleCreateJob({ name }, { ...values });
    });
  };

  const onValuesChange = (values: { type: string }) => {
    const keys = Object.keys(values);
    if(keys.includes('type')){
      setSelectType(values.type);
    }
  }

  return (
    <Modal
      title="新建同步分支"
      visible={visible}
      onCancel={onCancel}
      onOk={onOk}
      confirmLoading={loading}
      width={600}
    >
      <ProForm
        layout="horizontal"
        submitter={false}
        form={form}
        {...formItemLayout}
        onValuesChange={onValuesChange}
      >
        <ProFormText
          allowClear
          name="gitlab_branch"
          label="Gitlab 分支"
          placeholder="请输入"
        />
        <ProFormText
          allowClear
          name="github_branch"
          label="Github 分支"
          placeholder="请输入"
          // rules={[{ required: true, message: '请输入Github 分支' }]}
        />
        <ProFormText
          allowClear
          name="gitee_branch"
          label="Gitee 分支"
          placeholder="请输入"
        />
        <ProFormText
          allowClear
          name="code_china_branch"
          label="CodeChina 分支"
          placeholder="请输入"
        />
        <ProFormText
          allowClear
          name="gitlink_branch"
          label="Gitlink 分支"
          placeholder="请输入"
        />
        <ProFormSelect
          name="type"
          label="同步方式"
          placeholder="请选择"
          options={syncWay}
          rules={[{ required: true, message: '请选择同步方式' }]}
        />
        {
          selectType === 'OneWay' && (
            <ProFormSelect
              name="base"
              label="主仓库"
              placeholder="请选择"
              options={gitType}
              rules={[{ required: true, message: '请选择主仓库' }]}
            />
          )
        }
      </ProForm>
    </Modal>
  );
};
