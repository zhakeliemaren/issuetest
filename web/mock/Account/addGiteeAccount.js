const Mock = require('mockjs');

const dist =
  // 接收 req 参数, 用于传递 req.query 或 req.body 等参数
  (req) => ({
    default: {
      headers: {},
      statusCode: 200,
      data: {
        // 生成大小在 0~10000 之间的整数
        code: '@integer(0, 10000)',
        // 生成长度在 0~32 之间的小写字母
        msg: '@string("lower", 0, 32)',
        // 生成一个布尔值，10% 的概率为 false, 90% 的概率为 true
        success: '@boolean(1, 9, false)',
        // 生成一个布尔值，10% 的概率为 false, 90% 的概率为 true
        finished: '@boolean(1, 9, false)',
      },
    },
  });

module.exports = {
  'POST /cerobot/account/gitee_accounts': (req, res) => {
    const response = Mock.mock(dist(req)['default']).data;
    res.status(200).send(response);
  },
};
