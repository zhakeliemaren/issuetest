
from .code import Code
from extras.obfastapi.frame import OBHTTPException as HTTPException


class Errors:

    FORBIDDEN = HTTPException(Code.FORBIDDEN, '权限不足')
    QUERY_FAILD = HTTPException(Code.OPERATION_FAILED, '记录查询失败')
    INSERT_FAILD = HTTPException(Code.OPERATION_FAILED, '记录插入失败')
    DELETE_FAILD = HTTPException(Code.OPERATION_FAILED, '记录删除失败')
    UPDATE_FAILD = HTTPException(Code.OPERATION_FAILED, '记录更新失败')
    METHOD_EORROR = HTTPException(Code.INVALID_PARAMS, '错误的请求方式')
    NOT_INIT = HTTPException(555, '服务器缺少配置, 未能完成初始化')


class ErrorTemplate:

    def ARGUMENT_LACK(did): return HTTPException(
        Code.NOT_FOUND, '参数[%s]不能为空' % did)

    def ARGUMENT_ERROR(did): return HTTPException(
        Code.NOT_FOUND, '参数[%s]有错' % did)

    def TIP_ARGUMENT_ERROR(did): return HTTPException(
        Code.NOT_FOUND, '请输入正确的%s地址' % did)
