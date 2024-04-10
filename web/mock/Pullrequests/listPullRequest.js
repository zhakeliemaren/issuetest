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
        data: {
          // 生成大小在 0~10000 之间的整数
          total: '@integer(0, 10000)',
          'list|1-3': [
            {
              id: '@guid',
              title: '@ctitle(0,16)',
              // 生成长度在 0~32 之间的小写字母
              project: '@string("lower", 0, 32)',
              // 生成长度在 0~32 之间的小写字母
              type: '@string("lower", 0, 32)',
              // 生成长度在 0~32 之间的小写字母
              address: '@string("lower", 0, 32)',
              // 生成长度在 0~32 之间的小写字母
              author: '@string("lower", 0, 32)',
              email: '@email',
              // 生成长度在 0~32 之间的小写字母
              target_branch: '@string("lower", 0, 32)',
              // 生成长度在 0~32 之间的小写字母
              latest_commit: '@string("lower", 0, 32)',
            },
          ],
        },
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
  'GET /cerobot/projects/:name/pullrequests': (req, res) => {
    const response = Mock.mock(dist(req)['default']).data;
    res.status(200).send(response);
  },
};
