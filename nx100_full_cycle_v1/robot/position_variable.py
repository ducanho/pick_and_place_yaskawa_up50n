"""HW0483202 3.2: build P010 from Cartesian BASE P009 with a new Z."""
from decimal import Decimal
from settings import AXES
from .protocol import encode_command, ProtocolError


def parse_p010(raw,source='P010'):
    fields=tuple(v.strip() for v in raw.split(','))
    # SAVEV reply has no variable type/index prefix; LOADV adds 4,10.
    try:
        encode_command('LOADV',','.join(('4','10')+fields))
    except ValueError as exc:
        raise ProtocolError(source+' cần dữ liệu Cartesian BASE hợp lệ: '+str(exc)) from exc
    return fields


def with_z(fields,z):
    value=Decimal(str(z))
    if not value.is_finite() or value!=value.quantize(Decimal('.001')):
        raise ValueError('Z P010 cần số hữu hạn, tối đa 3 chữ số thập phân')
    result=fields[:4]+(format(value,'.3f'),)+fields[5:]
    payload=','.join(('4','10')+result)
    encode_command('LOADV',payload)
    return result,payload,dict(zip(AXES,map(float,result[2:8])))


def verify_p010(expected,raw):
    actual=parse_p010(raw)
    if any(Decimal(a)!=Decimal(b) for a,b in zip(actual,expected)):
        raise ProtocolError('Đọc lại P010 không khớp; không gọi DROP')
