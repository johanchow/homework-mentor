from fastapi import Request
from typing import Dict, Any

def parse_dynamic_filters(request: Request) -> Dict[str, Any]:
    """
    解析动态查询参数，支持以下格式：
    - 普通参数：field=value (等于比较)
    - 范围参数：field__gte=value, field__lte=value, field__gt=value, field__lt=value
    - 模糊匹配：field__like=value
    - 包含匹配：field__in=value1,value2,value3
    - 不等于：field__ne=value
    
    Args:
        request: FastAPI请求对象
        
    Returns:
        Dict: 过滤条件字典
    """
    filters = {}
    query_params = dict(request.query_params)

    # 移除特殊参数
    special_params = ['page', 'page_size', 'order_by']
    for param in special_params:
        query_params.pop(param, None)
    
    for key, value in query_params.items():
        if not value:  # 跳过空值
            continue
            
        # 检查是否是范围查询
        if '__' in key:
            field_name, operator = key.split('__', 1)
            
            if operator in ['gte', 'lte', 'gt', 'lt', 'ne', 'like', 'in']:
                if operator == 'in':
                    # 处理包含查询，支持逗号分隔的值
                    values = [v.strip() for v in value.split(',') if v.strip()]
                    filters[field_name] = {"$in": values}
                else:
                    # 其他操作符
                    op_map = {
                        'gte': '$gte',
                        'lte': '$lte', 
                        'gt': '$gt',
                        'lt': '$lt',
                        'ne': '$ne',
                        'like': '$like'
                    }
                    filters[field_name] = {op_map[operator]: value}
            else:
                # 未知操作符，当作普通字段处理
                filters[key] = value
        else:
            # 普通字段，使用等于比较
            filters[key] = value
    
    return filters

