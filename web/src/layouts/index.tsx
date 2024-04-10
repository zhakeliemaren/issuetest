import ProLayout from '@ant-design/pro-layout';
import { AppstoreOutlined, UserSwitchOutlined } from '@ant-design/icons';
import { Link } from 'umi';

const menuIcon = {
  project: <AppstoreOutlined />,
  account: <UserSwitchOutlined />,
};

export default (props: any) => {
  const menuDataRender = (menuList: any) => {
    return menuList.map((item: any) => ({
      ...item,
      icon: menuIcon[item.icon],
    }));
  };

  return (
    <ProLayout
      title="代码开源同步工具"
      menuDataRender={menuDataRender}
      menuItemRender={(menuItemProps, defaultDom) => (
        <Link to={menuItemProps.path}>{defaultDom}</Link>
      )}
      breadcrumbRender={(router) =>
        router?.map((item) => {
          const { path, ...rest } = item;
          return { ...rest };
        })
      }
      siderWidth={240}
      fixSiderbar
      {...props}
    />
  );
};
