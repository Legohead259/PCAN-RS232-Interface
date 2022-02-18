def parse_frame_message(msg:str):
    """
    Parses a CAN message sent from the PCAN module over the serial bus
    Example: 't1234DEADBEEF' - standard (11-bit) identifier message frame
             'R123456784'    - extended (29-bit) identifier request frame
    Returns a tuple with type, ID, size, and message
    Example: ('t', '00000123', '4', 'DEADBEEF')
             ('R', '00000123', '4')
    """

    _type = msg[0:1] # type is the first character of the message
    _ext = _type == 'T' or _type == 'R' # Determine if the message is an extended (29-bit) identifier frame
    _rtr = _type.lower() == 'r' # Determine if the message is a request frame
    _id = msg[1:4] if not _ext else msg[1:9] # Grab the ID depending on length of it (type-dependent)
    _id = _id.zfill(8)
    _size = msg[4:5] if not _ext else msg[9:10] # Grab the data size
    if not _rtr:
        _data = msg[5:5+int(_size)*2+1] if not _ext else msg[10:10+int(_size)*2+1] # Get the message data bytes depending on the size indicated by _size
    else:
        _data = ""
    return(_type, _id, _size, _data)

print(parse_frame_message('t1234DEADBEEF'))
print(parse_frame_message('T000001234DEADBEEF'))
print(parse_frame_message('r1234'))
print(parse_frame_message('R000001234'))