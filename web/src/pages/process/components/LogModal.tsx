import { useEffect } from 'react';
import { Modal, Button, Spin } from 'antd';
import { getJobLog } from '@/services/Jobs';
import useRequest from '@/utils/useRequest';
import moment from 'moment';

interface Props {
  visible: boolean;
  onCancel: () => void;
  name?: string;
  id?: number
}

export default (props: Props) => {
  const { visible, onCancel, name, id } = props;
  const { run: fetchJobLog, loading, data: logsData } = useRequest(getJobLog);

  useEffect(() => {
    fetchJobLog({ name, id });
  }, [])

  return (
    <Modal
      title="查看日志"
      visible={visible}
      onCancel={onCancel}
      width={800}
      footer={<Button onClick={onCancel} >关闭</Button>}
      bodyStyle={{ overflow: 'auto', maxHeight: 600 }}
    >
      <Spin spinning={loading} >
        {
          logsData?.data?.list?.map((item: API.Log, index: number) => (
            <>
              <div>{moment(item.create_time).format('YYYY-MM-DD HH:mm:ss')}【{item.log_type}】{item.log}</div>
              {index === logsData?.data?.list?.length ? <br/> : null }
            </>
          ))
        }
      </Spin>
    </Modal>
  );
};
